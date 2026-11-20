#!/usr/bin/env python3
"""Create and verify a detached GPG signature for one immutable artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path


class SigningError(RuntimeError):
    """The requested artifact cannot be safely signed or verified."""


def _digest(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(block)
            digest.update(block)
    return size, digest.hexdigest()


def _fingerprint(value: str) -> str:
    normalized = value.replace(" ", "").upper()
    if not re.fullmatch(r"(?:[A-F0-9]{40}|[A-F0-9]{64})", normalized):
        raise SigningError("fingerprint must be a full 40- or 64-character hexadecimal fingerprint")
    return normalized


def _gpg() -> str:
    binary = shutil.which("gpg")
    if binary is None:
        raise SigningError("gpg is required; install GnuPG and import the approved public key")
    return binary


def _valid_signature_fingerprints(result: subprocess.CompletedProcess[str]) -> set[str]:
    fingerprints: set[str] = set()
    for line in result.stdout.splitlines():
        if not line.startswith("[GNUPG:] VALIDSIG "):
            continue
        fields = line.split()
        if len(fields) >= 3:
            fingerprints.add(fields[2].upper())
        if len(fields) >= 12:
            fingerprints.add(fields[-1].upper())
    return fingerprints


def _verify_signature(artifact: Path, signature: Path, expected: str) -> None:
    result = subprocess.run(
        [_gpg(), "--batch", "--status-fd=1", "--verify", str(signature), str(artifact)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "GPG rejected the detached signature"
        raise SigningError(detail)
    actual = _valid_signature_fingerprints(result)
    if expected not in actual:
        raise SigningError(
            f"signature is valid but signer fingerprint does not match {expected}"
        )


def _paths(args: argparse.Namespace) -> tuple[Path, Path, Path, str]:
    artifact = Path(args.artifact).expanduser().resolve(strict=True)
    if not artifact.is_file():
        raise SigningError(f"artifact is not a regular file: {artifact}")
    signature = Path(args.signature).expanduser().resolve() if args.signature else Path(f"{artifact}.asc")
    metadata = (
        Path(args.metadata).expanduser().resolve()
        if args.metadata
        else Path(f"{signature}.json")
    )
    if artifact in {signature, metadata} or signature == metadata:
        raise SigningError("artifact, signature, and metadata paths must be different")
    return artifact, signature, metadata, _fingerprint(args.fingerprint)


def _sign(args: argparse.Namespace) -> dict[str, object]:
    artifact, signature, metadata, expected = _paths(args)
    if signature.exists() or metadata.exists():
        raise SigningError("signature or metadata path already exists; refusing to overwrite")
    before_size, before_hash = _digest(artifact)
    completed = subprocess.run(
        [
            _gpg(),
            "--armor",
            "--detach-sign",
            "--local-user",
            expected,
            "--output",
            str(signature),
            "--",
            str(artifact),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        signature.unlink(missing_ok=True)
        raise SigningError(completed.stderr.strip() or "gpg failed to create the signature")
    try:
        _verify_signature(artifact, signature, expected)
        after_size, after_hash = _digest(artifact)
        if (before_size, before_hash) != (after_size, after_hash):
            raise SigningError("artifact changed during signing; no success record was written")
        record: dict[str, object] = {
            "artifact": artifact.name,
            "artifact_size": after_size,
            "artifact_sha256": after_hash,
            "signature": signature.name,
            "fingerprint": expected,
            "verified": True,
        }
        metadata.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=metadata.parent,
            prefix=f".{metadata.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_metadata = Path(handle.name)
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")
        if metadata.exists():
            raise SigningError(f"metadata path appeared during signing: {metadata}")
        os.replace(temp_metadata, metadata)
        return {**record, "metadata_path": str(metadata)}
    except Exception:
        signature.unlink(missing_ok=True)
        if "temp_metadata" in locals():
            temp_metadata.unlink(missing_ok=True)
        raise


def _verify(args: argparse.Namespace) -> dict[str, object]:
    artifact, signature, _metadata, expected = _paths(args)
    if not signature.is_file():
        raise SigningError(f"signature file does not exist: {signature}")
    before = _digest(artifact)
    _verify_signature(artifact, signature, expected)
    after = _digest(artifact)
    if before != after:
        raise SigningError("artifact changed during verification")
    return {
        "artifact": artifact.name,
        "artifact_size": after[0],
        "artifact_sha256": after[1],
        "signature": signature.name,
        "fingerprint": expected,
        "verified": True,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("sign", "verify"):
        command = commands.add_parser(name)
        command.add_argument("--artifact", required=True)
        command.add_argument("--fingerprint", required=True)
        command.add_argument("--signature")
        if name == "sign":
            command.add_argument("--metadata")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = _sign(args) if args.command == "sign" else _verify(args)
    except (OSError, SigningError, subprocess.SubprocessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
