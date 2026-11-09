"""Shared validation for Rhetoric's static update manifest (format 1).

This module is the single owner of the manifest rules. The release-side
checker (``scripts/check_update_manifest.py``) and the in-app updater
(``the_oracle.update_service``) both use it, so a manifest that passes the
release gate is exactly the manifest the app will accept — there is no
second, divergent copy of the parsing logic.

A manifest is ``{"format": 1, "version": str, "artifacts": [{"name",
"sha256", "size"}], "rollback": str}``. Validation is deliberately strict:
artifact names must be bare file names (no directory components), sizes
must be real ints, hashes must be lowercase hex SHA-256, and artifact
names must be unique. Nothing here touches the network.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_NAME_SEPARATORS = re.compile(r"[/\\]")


class ManifestError(ValueError):
    """The manifest or selected artifact is not trustworthy."""


def validate_manifest(payload: Any) -> dict[str, Any]:
    """Return ``payload`` if it is a well-formed format-1 manifest."""
    if not isinstance(payload, dict) or payload.get("format") != 1:
        raise ManifestError("unsupported update manifest format")
    if isinstance(payload.get("format"), bool):
        raise ManifestError("unsupported update manifest format")
    if not isinstance(payload.get("version"), str) or not payload["version"]:
        raise ManifestError("update manifest has no version")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ManifestError("update manifest has no artifacts")
    seen: set[str] = set()
    for item in artifacts:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise ManifestError("update manifest contains an invalid artifact")
        name = item["name"]
        if not name or name in {".", ".."} or _NAME_SEPARATORS.search(name):
            raise ManifestError(f"artifact name must be a plain file name: {name!r}")
        if name in seen:
            raise ManifestError(f"duplicate artifact in update manifest: {name}")
        seen.add(name)
        if not _SHA256.fullmatch(str(item.get("sha256", ""))):
            raise ManifestError(f"invalid SHA-256 for {name}")
        size = item.get("size")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ManifestError(f"invalid size for {name}")
    rollback = payload.get("rollback", "")
    if not isinstance(rollback, str):
        raise ManifestError("update manifest rollback note must be text")
    return payload


def parse_manifest(data: bytes | str) -> dict[str, Any]:
    """Parse and validate manifest JSON from raw bytes or text."""
    try:
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        payload = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"could not parse update manifest: {exc}") from exc
    return validate_manifest(payload)


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ManifestError(f"could not read update manifest: {exc}") from exc
    return parse_manifest(raw)


def parse_version(value: str) -> tuple[int, ...] | None:
    """Parse a dotted numeric version, or return None when it is not one."""
    parts = str(value).strip().split(".")
    numbers: list[int] = []
    for part in parts:
        if not part.isdigit():
            return None
        numbers.append(int(part))
    return tuple(numbers) if numbers else None


def is_newer_version(candidate: str, current: str) -> bool:
    """True only when ``candidate`` is strictly newer than ``current``.

    Dotted numeric versions compare numerically (1.10.0 > 1.9.0). When
    either side is not dotted numeric, fall back to plain inequality so
    unusual version strings still behave sanely, and equal strings are
    never an update (a downgrade is never offered as one either when the
    versions are numeric).
    """
    new = parse_version(candidate)
    old = parse_version(current)
    if new is not None and old is not None:
        width = max(len(new), len(old))
        return new + (0,) * (width - len(new)) > old + (0,) * (width - len(old))
    return str(candidate) != str(current)


def update_available(current_version: str, payload: dict[str, Any]) -> bool:
    return is_newer_version(str(payload["version"]), str(current_version))


def _artifact_entry(payload: dict[str, Any], name: str) -> dict[str, Any]:
    item = next((entry for entry in payload["artifacts"] if entry["name"] == name), None)
    if item is None:
        raise ManifestError(f"artifact is not listed in the manifest: {name}")
    return item


def verify_artifact_bytes(payload: dict[str, Any], name: str, data: bytes) -> bytes:
    """Return ``data`` unchanged if it matches the manifest entry."""
    item = _artifact_entry(payload, name)
    if len(data) != item["size"]:
        raise ManifestError(f"artifact size mismatch for {name}")
    if hashlib.sha256(data).hexdigest() != item["sha256"]:
        raise ManifestError(f"artifact SHA-256 mismatch for {name}")
    return data


def verify_artifact(payload: dict[str, Any], directory: Path, name: str) -> Path:
    item = _artifact_entry(payload, name)
    path = (directory / name).resolve()
    if path.parent != directory.resolve():
        raise ManifestError("artifact name must not escape the artifact directory")
    if not path.is_file():
        raise ManifestError(f"artifact is missing: {path}")
    if path.stat().st_size != item["size"]:
        raise ManifestError(f"artifact size mismatch for {name}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != item["sha256"]:
        raise ManifestError(f"artifact SHA-256 mismatch for {name}")
    return path
