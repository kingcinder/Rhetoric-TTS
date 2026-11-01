"""Rhetoric licensing: offline token verification (docs/LICENSING_DESIGN.md).

Public surface. Import discipline: this package imports stdlib plus the
vendored ``the_oracle._ed25519`` only — never huggingface_hub, torch, or any
ML dependency (pinned by tests/test_offline_guarantee.py), and it runs nothing
at import time. ``current_license()`` is called lazily at feature gates so an
unlicensed install never blocks startup.

Everything is offline by construction: verification is a pure function of the
token bytes, the embedded public keys, and the wall clock. Activation never
contacts a server (pins in tests/test_licensing_offline.py).
"""

from __future__ import annotations

from pathlib import Path

from the_oracle.licensing.policy import (
    LicenseRequired,
    is_licensed,
    require,
)
from the_oracle.licensing.store import clear_token, load_token, save_token, store_path
from the_oracle.licensing.tokens import (
    LicenseStatus,
    TokenPayload,
    canonical_payload_bytes,
    mint,
    parse,
    verify_token,
)

__all__ = [
    "LicenseRequired",
    "LicenseStatus",
    "TokenPayload",
    "canonical_payload_bytes",
    "clear_token",
    "current_license",
    "is_licensed",
    "load_token",
    "mint",
    "parse",
    "require",
    "save_token",
    "store_path",
    "verify_token",
]


#: Process-wide attestation memo: ``{package_root: detail_or_None}``. Hashing
#: the protected modules once per process is enough; a per-gate hash would put
#: a disk read in front of every render.
_attestation_memo: dict[str, str | None] = {}

_ATTESTATION_DETAIL = (
    "This installation's licensing code no longer matches the build it came "
    "from, so the serial number cannot be trusted. Reinstall Rhetoric from the "
    "official download; if it still fails, contact support."
)


def _attestation_failure() -> str | None:
    """A detail string when protected modules were modified after the build.

    Only an artifact built with ``scripts/build_native_license.py --attest``
    carries a manifest, so a development checkout — and any install without the
    compiled core — is unaffected. The check lives here rather than in
    ``policy`` because every gate resolves ``current_license``: a patched gate
    that skips it is exactly what the compiled manifest is there to notice.
    """
    from the_oracle import _native

    core = _native.load()
    if core is None:
        return None
    try:
        import the_oracle

        package_root = str(Path(the_oracle.__file__).resolve().parent)
        if package_root not in _attestation_memo:
            verdict = core.attest(package_root)
            clean = bool(verdict.get("ok", True)) if isinstance(verdict, dict) else True
            _attestation_memo[package_root] = None if clean else _ATTESTATION_DETAIL
        return _attestation_memo[package_root]
    except Exception:
        # A core that cannot answer is not evidence of tampering; failing
        # closed here would brick an install whose files cannot be read.
        return None


def current_license(repo_root: str | Path | None = None) -> LicenseStatus:
    """The install's license status — the one call every consumer makes.

    ``repo_root=None`` resolves the running install's root (the same policy
    the offline module owns). Any store-level failure is a typed
    ``store_error`` status with the remedy in ``detail``; it never raises.
    """
    from the_oracle.licensing import machine
    from the_oracle.offline import repo_root as resolve_repo_root

    tampered = _attestation_failure()
    if tampered is not None:
        return LicenseStatus(ok=False, state="integrity", detail=tampered)

    root = repo_root if repo_root is not None else resolve_repo_root()
    result = load_token(root)
    if result.state == "no_token":
        return LicenseStatus(
            ok=False,
            state="no_token",
            detail="No serial number is activated.",
        )
    if result.state != "loaded" or result.stored is None:
        return LicenseStatus(ok=False, state="store_error", detail=result.detail)

    return verify_token(result.stored.token, machine_hash=machine.machine_hash())
