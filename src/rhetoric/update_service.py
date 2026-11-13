"""In-app automated updates for Rhetoric, driven by the static manifest.

Channel design: the release process publishes ``update-manifest.json``
(format 1, see :mod:`rhetoric.update_manifest`) plus the artifacts it
lists as assets of a GitHub Release. The stable URL below always resolves
to the newest release's manifest, so pushing an update is "cut a release";
there is no update server to run.

Behaviour contract:

- Automated checks are ON unless the user opts out in Settings
  (``automatic_updates_enabled`` app setting, default True).
- A check never raises and never blocks startup: network/offline failures
  come back as an ``error`` result and are otherwise silent.
- An artifact is applied only after its size and SHA-256 verify against
  the manifest. An unverified artifact is never installed.
- Self-apply is supported for AppImage installs (the running file is
  replaced, keeping a ``.previous`` copy so a failed apply rolls back).
  Other frozen builds and source checkouts are notified, not replaced:
  source installs update with ``./rhetoric update``.
- The most recent check is kept on :data:`SESSION` so the support gate
  can tell whether this session has verified the install is current.
"""

from __future__ import annotations

import os
import shutil
import sys
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from rhetoric import __version__ as INSTALLED_VERSION
from rhetoric.update_manifest import (
    ManifestError,
    is_newer_version,
    parse_manifest,
    validate_manifest,
    verify_artifact,
    verify_artifact_bytes,
)

ISSUE_REPO = "kingcinder/Rhetoric-TTS"
DEFAULT_MANIFEST_URL = (
    f"https://github.com/{ISSUE_REPO}/releases/latest/download/update-manifest.json"
)
MANIFEST_URL_ENV = "RHETORIC_UPDATE_MANIFEST_URL"
USER_AGENT = "Rhetoric-Updater"
FETCH_TIMEOUT_SECONDS = 15

STATUS_CURRENT = "current"
STATUS_UPDATE_AVAILABLE = "update_available"
STATUS_ERROR = "error"
STATUS_DISABLED = "disabled"
STATUS_NOT_CHECKED = "not_checked"

Fetcher = Callable[[str], bytes]


class UpdateError(RuntimeError):
    """An update step failed; nothing unverified was applied."""


def manifest_url() -> str:
    """The single update-channel URL (env override for mirrors/tests)."""
    override = os.environ.get(MANIFEST_URL_ENV, "").strip()
    return override or DEFAULT_MANIFEST_URL


def _fetch_url(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
        return response.read()


@dataclass
class UpdateCheckResult:
    status: str
    current_version: str
    remote_version: str = ""
    manifest: dict[str, Any] | None = None
    message: str = ""
    checked_at: str = ""
    applied_artifact: str = ""
    rollback_path: str = ""


@dataclass
class UpdateSession:
    """Process-wide record of the latest automated check (for the gate)."""

    last_result: UpdateCheckResult | None = None

    def record(self, result: UpdateCheckResult) -> UpdateCheckResult:
        self.last_result = result
        return result

    def gate_status(self) -> str:
        """Map the session state onto the support gate's vocabulary."""
        if self.last_result is None:
            return STATUS_NOT_CHECKED
        if self.last_result.status == STATUS_CURRENT:
            return STATUS_CURRENT
        if self.last_result.status == STATUS_UPDATE_AVAILABLE:
            return STATUS_UPDATE_AVAILABLE
        if self.last_result.status == STATUS_DISABLED:
            return STATUS_DISABLED
        return "check_failed"


SESSION = UpdateSession()


def gate_status() -> str:
    return SESSION.gate_status()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def check_for_update(
    current_version: str | None = None,
    *,
    fetcher: Fetcher | None = None,
    url: str | None = None,
    session: UpdateSession | None = None,
) -> UpdateCheckResult:
    """Fetch and validate the manifest; never raises."""
    current = str(current_version or INSTALLED_VERSION)
    fetch = fetcher or _fetch_url
    try:
        payload = parse_manifest(fetch(url or manifest_url()))
    except Exception as exc:  # offline, DNS, bad payload: silent by design
        result = UpdateCheckResult(
            status=STATUS_ERROR, current_version=current,
            message=f"update check failed: {exc}", checked_at=_now(),
        )
        return (session or SESSION).record(result)
    remote = str(payload["version"])
    if is_newer_version(remote, current):
        result = UpdateCheckResult(
            status=STATUS_UPDATE_AVAILABLE, current_version=current,
            remote_version=remote, manifest=payload,
            message=f"Rhetoric {remote} is available (installed: {current}).",
            checked_at=_now(),
        )
    else:
        result = UpdateCheckResult(
            status=STATUS_CURRENT, current_version=current,
            remote_version=remote, manifest=payload,
            message="Rhetoric is up to date.", checked_at=_now(),
        )
    return (session or SESSION).record(result)


def artifact_url(base_url: str, name: str) -> str:
    return base_url.rsplit("/", 1)[0] + "/" + name


def download_artifact(
    payload: dict[str, Any],
    name: str,
    dest_dir: Path,
    *,
    fetcher: Fetcher | None = None,
    url: str | None = None,
) -> Path:
    """Download one artifact and verify it before it lands in place.

    The bytes are hash/size-checked in memory against the manifest, then
    written via a temp file + rename. A mismatch raises and leaves no
    partial artifact behind.
    """
    validate_manifest(payload)
    fetch = fetcher or _fetch_url
    data = fetch(artifact_url(url or manifest_url(), name))
    verify_artifact_bytes(payload, name, data)
    dest_dir.mkdir(parents=True, exist_ok=True)
    final = dest_dir / name
    temp = dest_dir / (name + ".download")
    temp.write_bytes(data)
    try:
        os.replace(temp, final)
    except Exception:
        temp.unlink(missing_ok=True)
        raise
    verify_artifact(payload, dest_dir, name)
    return final


def install_kind(environ: dict[str, str] | None = None) -> str:
    """Classify this install: ``appimage``, ``frozen``, or ``source``."""
    env = os.environ if environ is None else environ
    appimage = env.get("APPIMAGE", "")
    if appimage and Path(appimage).is_file():
        return "appimage"
    if getattr(sys, "frozen", False):
        return "frozen"
    return "source"


def apply_appimage_update(
    downloaded: Path,
    *,
    environ: dict[str, str] | None = None,
) -> Path:
    """Replace the running AppImage, keeping a rollback copy.

    Returns the rollback path. On any failure after the backup is taken,
    the previous AppImage is restored before the error propagates.
    """
    env = os.environ if environ is None else environ
    target = Path(env.get("APPIMAGE", ""))
    if not target.is_file():
        raise UpdateError("APPIMAGE does not point at a file; cannot self-apply")
    if not downloaded.is_file():
        raise UpdateError(f"downloaded artifact is missing: {downloaded}")
    rollback = target.with_name(target.name + ".previous")
    shutil.copy2(target, rollback)
    try:
        os.replace(downloaded, target)
        target.chmod(0o755)
    except Exception as exc:
        shutil.copy2(rollback, target)
        raise UpdateError(f"apply failed; previous version restored: {exc}") from exc
    return rollback


def _pick_artifact(payload: dict[str, Any], kind: str) -> str | None:
    names = [entry["name"] for entry in payload["artifacts"]]
    if kind == "appimage":
        for name in names:
            if name.lower().endswith(".appimage"):
                return name
        return None
    return names[0] if names else None


def run_automated_update(
    settings: dict[str, Any] | None = None,
    *,
    current_version: str | None = None,
    fetcher: Fetcher | None = None,
    url: str | None = None,
    session: UpdateSession | None = None,
    environ: dict[str, str] | None = None,
    staging_dir: Path | None = None,
) -> UpdateCheckResult:
    """One automated-update pass: check, then apply or notify.

    Honors the Settings opt-out. Never raises; the outcome is recorded on
    the session either way so the support gate sees fresh state.
    """
    sess = session or SESSION
    current = str(current_version or INSTALLED_VERSION)
    if settings is not None and not settings.get("automatic_updates_enabled", True):
        return sess.record(UpdateCheckResult(
            status=STATUS_DISABLED, current_version=current,
            message="Automated updates are turned off in Settings.",
            checked_at=_now(),
        ))
    result = check_for_update(current, fetcher=fetcher, url=url, session=sess)
    if result.status != STATUS_UPDATE_AVAILABLE or result.manifest is None:
        return result
    kind = install_kind(environ)
    if kind != "appimage":
        result.message += (
            " Update with ./rhetoric update, then restart Rhetoric."
            if kind == "source"
            else " Download the new release to update, then restart Rhetoric."
        )
        return result
    name = _pick_artifact(result.manifest, kind)
    if name is None:
        result.message += " No AppImage artifact is listed for this platform."
        return result
    try:
        stage = staging_dir or Path.home() / ".cache" / "rhetoric" / "updates"
        downloaded = download_artifact(
            result.manifest, name, stage, fetcher=fetcher, url=url,
        )
        rollback = apply_appimage_update(downloaded, environ=environ)
    except Exception as exc:
        result.message += f" The update was not applied: {exc}"
        return result
    result.applied_artifact = name
    result.rollback_path = str(rollback)
    result.message += (
        f" Update {result.remote_version} was downloaded, verified, and "
        "installed; restart Rhetoric to run it. The previous version was "
        f"kept at {rollback}."
    )
    return result
