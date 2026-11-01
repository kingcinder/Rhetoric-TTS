"""Integrity attestation: the compiled manifest decides, not the caller.

The core hashes the installed modules itself from a manifest compiled at build
time (``scripts/build_native_license.py --attest``), so a patched install cannot
simply hand it the digests it prefers. These tests cover the two halves that can
be exercised without a second cargo build: the manifest writer, and the Python
wiring that turns a native mismatch into an ``integrity`` status.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from the_oracle import _native  # noqa: E402
from the_oracle.licensing import LicenseStatus, current_license  # noqa: E402


def _load_build_script():
    path = REPO_ROOT / "scripts" / "build_native_license.py"
    spec = importlib.util.spec_from_file_location("build_native_license", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_development_core_carries_no_manifest() -> None:
    if not _native.available():
        pytest.skip("compiled core is not built in this checkout")
    verdict = _native.attest(REPO_ROOT / "src" / "the_oracle")
    assert verdict is not None
    assert verdict["enforced"] is False
    assert verdict["ok"] is True
    assert verdict["checked"] == 0
    assert _native.attestation_enforced() is False


def test_manifest_writer_hashes_every_protected_module(tmp_path: Path) -> None:
    module = _load_build_script()
    manifest = module.write_manifest(
        REPO_ROOT / "src" / "the_oracle", tmp_path / "integrity-manifest.txt"
    )
    lines = manifest.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(module.PROTECTED_MODULES)

    entries = {}
    for line in lines:
        digest, relative = line.split("  ")
        entries[relative] = digest
        expected = hashlib.sha256(
            (REPO_ROOT / "src" / "the_oracle" / relative).read_bytes()
        ).hexdigest()
        assert digest == expected, relative

    # Every module that carries a gate must be covered, or patching it would
    # leave attestation clean.
    assert {
        "pipeline.py",
        "render_subprocess.py",
        "audio/export_flac.py",
        "licensing/__init__.py",
        "licensing/tokens.py",
    } <= set(entries)


def test_manifest_writer_refuses_a_package_missing_gates(tmp_path: Path) -> None:
    module = _load_build_script()
    package = tmp_path / "the_oracle"
    (package / "licensing").mkdir(parents=True)
    with pytest.raises(SystemExit, match="missing protected modules"):
        module.write_manifest(package, tmp_path / "integrity-manifest.txt")


def test_a_native_mismatch_is_reported_as_integrity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from the_oracle.licensing import _attestation_memo

    _attestation_memo.clear()
    monkeypatch.setattr(
        _native,
        "load",
        lambda: SimpleNamespace(
            attest=lambda _root: {
                "enforced": True,
                "ok": False,
                "checked": 2,
                "mismatched": ["pipeline.py"],
            }
        ),
    )

    status = current_license(tmp_path)
    assert status.ok is False
    assert status.state == "integrity"
    assert "Reinstall" in status.detail


def test_a_clean_manifest_does_not_change_the_verdict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from the_oracle.licensing import _attestation_memo

    _attestation_memo.clear()
    monkeypatch.setattr(
        _native,
        "load",
        lambda: SimpleNamespace(
            attest=lambda _root: {
                "enforced": True,
                "ok": True,
                "checked": 10,
                "mismatched": [],
            }
        ),
    )
    status = current_license(tmp_path)
    assert status.state == "no_token"
    assert isinstance(status, LicenseStatus)


def test_attestation_is_memoized_once_per_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from the_oracle.licensing import _attestation_memo

    _attestation_memo.clear()
    calls: list[str] = []

    def fake_attest(root: str) -> dict[str, object]:
        calls.append(root)
        return {"enforced": True, "ok": True, "checked": 10, "mismatched": []}

    monkeypatch.setattr(_native, "load", lambda: SimpleNamespace(attest=fake_attest))
    current_license(tmp_path)
    current_license(tmp_path)
    assert len(calls) == 1


def test_a_core_that_cannot_answer_does_not_brick_the_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from the_oracle.licensing import _attestation_memo

    _attestation_memo.clear()

    def explode(_root: str) -> dict[str, object]:
        raise OSError("cannot read package files")

    monkeypatch.setattr(_native, "load", lambda: SimpleNamespace(attest=explode))
    assert current_license(tmp_path).state == "no_token"
