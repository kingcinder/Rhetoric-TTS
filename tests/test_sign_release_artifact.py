from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "sign_release_artifact.py"


def test_release_signing_helper_is_available() -> None:
    assert SCRIPT.is_file()


@pytest.fixture
def signer(tmp_path: Path) -> tuple[dict[str, str], str]:
    gpg = shutil.which("gpg")
    if gpg is None:
        pytest.skip("gpg is required for release-signing tests")
    home = tmp_path / "gnupg"
    home.mkdir(mode=0o700)
    env = os.environ.copy()
    env["GNUPGHOME"] = str(home)
    made = subprocess.run(
        [
            gpg,
            "--batch",
            "--pinentry-mode",
            "loopback",
            "--passphrase",
            "",
            "--quick-generate-key",
            "Rhetoric Test Signer <test@example.invalid>",
            "ed25519",
            "sign",
            "1d",
        ],
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert made.returncode == 0, made.stderr
    listing = subprocess.run(
        [gpg, "--batch", "--with-colons", "--list-secret-keys"],
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
        check=True,
    )
    fingerprint = next(
        row.split(":")[9]
        for row in listing.stdout.splitlines()
        if row.startswith("fpr:")
    )
    return env, fingerprint


def _run(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def test_sign_creates_detached_signature_and_hash_metadata(
    tmp_path: Path, signer: tuple[dict[str, str], str]
) -> None:
    env, fingerprint = signer
    artifact = tmp_path / "candidate.tar.zst"
    artifact.write_bytes(b"fixed candidate bytes\x00\xff")
    signature = tmp_path / "candidate.tar.zst.asc"

    result = _run(
        env,
        "sign",
        "--artifact",
        str(artifact),
        "--fingerprint",
        fingerprint,
        "--signature",
        str(signature),
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["fingerprint"] == fingerprint
    assert report["artifact_sha256"]
    assert report["artifact_size"] == len(b"fixed candidate bytes\x00\xff")
    assert signature.is_file()
    assert Path(report["metadata_path"]).is_file()
    assert artifact.read_bytes() == b"fixed candidate bytes\x00\xff"


def test_sign_refuses_to_overwrite_signature_or_artifact(
    tmp_path: Path, signer: tuple[dict[str, str], str]
) -> None:
    env, fingerprint = signer
    artifact = tmp_path / "candidate.tar.zst"
    artifact.write_bytes(b"fixed bytes")
    signature = tmp_path / "candidate.tar.zst.asc"
    signature.write_text("owner data", encoding="utf-8")

    result = _run(
        env,
        "sign",
        "--artifact",
        str(artifact),
        "--fingerprint",
        fingerprint,
        "--signature",
        str(signature),
    )

    assert result.returncode != 0
    assert "exists" in result.stderr.lower()
    assert signature.read_text(encoding="utf-8") == "owner data"


def test_verify_rejects_tampered_artifact_and_wrong_fingerprint(
    tmp_path: Path, signer: tuple[dict[str, str], str]
) -> None:
    env, fingerprint = signer
    artifact = tmp_path / "candidate.tar.zst"
    artifact.write_bytes(b"before")
    signature = tmp_path / "candidate.tar.zst.asc"
    made = _run(
        env,
        "sign",
        "--artifact",
        str(artifact),
        "--fingerprint",
        fingerprint,
        "--signature",
        str(signature),
    )
    assert made.returncode == 0, made.stderr

    wrong = "0" * len(fingerprint)
    rejected = _run(
        env,
        "verify",
        "--artifact",
        str(artifact),
        "--fingerprint",
        wrong,
        "--signature",
        str(signature),
    )
    assert rejected.returncode != 0

    artifact.write_bytes(b"after")
    tampered = _run(
        env,
        "verify",
        "--artifact",
        str(artifact),
        "--fingerprint",
        fingerprint,
        "--signature",
        str(signature),
    )
    assert tampered.returncode != 0
