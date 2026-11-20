"""Token persistence with repo-local development and per-user installed stores.

The source checkout keeps its existing repo-local activation. A system
installation under a root-owned directory stores activation in the user's
XDG config directory, while still reading an existing system-wide token.
Writes are atomic so interruption cannot leave a partial token.

Load failures are typed, never raised: corrupted_content (parseable JSON but
wrong shape), unreadable (permission/OS error). A missing file is simply
"no_token" — the valid unlicensed state.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

STORE_FILENAME = "rhetoric_license.json"

# Pre-rename store filename. Moved forward on first use after the rename
# so an existing activation survives untouched.
LEGACY_STORE_FILENAME = "oracle_license.json"


@dataclass(frozen=True)
class StoredToken:
    token: str


@dataclass(frozen=True)
class LoadResult:
    state: str  # "no_token" | "loaded" | "corrupted_content" | "unreadable"
    stored: StoredToken | None = None
    detail: str = ""


def store_path(repo_root: str | Path) -> Path:
    root = Path(repo_root)
    if os.access(root, os.W_OK):
        return root / STORE_FILENAME
    config_home = os.environ.get("XDG_CONFIG_HOME")
    config_root = Path(config_home) if config_home else Path.home() / ".config"
    return config_root / "rhetoric" / STORE_FILENAME


def _migrate_legacy_store(repo_root: str | Path) -> None:
    """Move a pre-rename license file forward, if the new one is absent."""
    new_path = store_path(repo_root)
    if new_path.exists():
        return
    legacy_path = Path(repo_root) / LEGACY_STORE_FILENAME
    if legacy_path.is_file():
        try:
            os.replace(legacy_path, new_path)
        except OSError:
            pass


def save_token(repo_root: str | Path, token: str, *, verify_before_save) -> LoadResult:
    """Atomically persist ``token`` after ``verify_before_save(token)`` passes.

    The verify callback keeps this module honest: a token that does not verify
    is refused *before* any bytes are written, so the store can never hold a
    token the verifier would reject on next load (M4 pins this).
    """
    if os.access(repo_root, os.W_OK):
        _migrate_legacy_store(repo_root)
    verdict = verify_before_save(token)
    if not verdict.ok:
        return LoadResult(state="refused", detail=verdict.detail or verdict.state)

    path = store_path(repo_root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temp_path = path.with_name(path.name + ".tmp")
        descriptor = os.open(
            temp_path,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o600,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump({"token": token}, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, path)
    except OSError as error:
        return LoadResult(state="unreadable", detail=f"could not write {path}: {error}")
    return LoadResult(state="saved", stored=StoredToken(token=token))


def load_token(repo_root: str | Path) -> LoadResult:
    """Read the stored token. Missing file -> no_token (the normal case)."""
    root = Path(repo_root)
    root_path = root / STORE_FILENAME
    path = store_path(root)
    if path == root_path:
        _migrate_legacy_store(root)
        candidates = (path, root / LEGACY_STORE_FILENAME)
    else:
        candidates = (path, root_path, root / LEGACY_STORE_FILENAME)

    raw = None
    for candidate in candidates:
        try:
            raw = candidate.read_text(encoding="utf-8")
            path = candidate
            break
        except FileNotFoundError:
            continue
        except OSError as error:
            return LoadResult(state="unreadable", detail=f"could not read {candidate}: {error}")
    if raw is None:
        return LoadResult(state="no_token")

    try:
        data = json.loads(raw)
    except ValueError:
        return LoadResult(
            state="corrupted_content",
            detail=f"{path} is not valid JSON. Re-run `rhetoric activate` with your serial number to restore it.",
        )
    if not isinstance(data, dict) or not isinstance(data.get("token"), str) or not data["token"]:
        return LoadResult(
            state="corrupted_content",
            detail=f"{path} does not contain a serial number. Re-run `rhetoric activate`.",
        )
    return LoadResult(state="loaded", stored=StoredToken(token=data["token"]))


def clear_token(repo_root: str | Path) -> bool:
    """Deactivation is local: remove the file, move the seat. True if removed."""
    if os.access(repo_root, os.W_OK):
        _migrate_legacy_store(repo_root)
    path = store_path(repo_root)
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        return False
