"""The support gate: submissions require updates on and a current install.

Dyther's rule, enforced here in one place so every submission path
(Report a Problem share actions, the CLI share commands, and the crash
flow, which shares the same dialog) applies it identically:

- automated updates must be enabled in Settings, and
- the installed version must be current — proven by an update check run
  in this session that found no newer version (see
  :mod:`rhetoric.update_service`).

Creating a local diagnostic bundle for the user's own inspection is NOT
gated; only sending/submitting is. When the gate blocks, the message
states exactly what to do, mirroring the warning shown next to the
Settings opt-out toggle.
"""

from __future__ import annotations

from dataclasses import dataclass

UPDATE_STATUS_CURRENT = "current"
UPDATE_STATUS_UPDATE_AVAILABLE = "update_available"
UPDATE_STATUS_NOT_CHECKED = "not_checked"
UPDATE_STATUS_CHECK_FAILED = "check_failed"
UPDATE_STATUS_DISABLED = "disabled"

_REASON_TEXT = {
    "updates_disabled": "automated updates are turned off",
    "update_pending": "a newer version of Rhetoric is available but not installed",
    "not_checked": "no update check has been run in this session",
    "check_failed": "the last update check could not be completed",
}

SUPPORT_STEPS = (
    "1. Turn automated updates back on in Settings (if they are off).\n"
    "2. Fully update Rhetoric to the current version.\n"
    "3. Re-check your issue with the automatic bug catcher on the fully "
    "updated program.\n"
    "4. Then submit your report."
)


@dataclass(frozen=True)
class SupportGateResult:
    allowed: bool
    reasons: tuple[str, ...]
    message: str


def evaluate_support_gate(
    *,
    automatic_updates_enabled: bool,
    update_status: str,
) -> SupportGateResult:
    """Return whether a support submission may proceed right now."""
    reasons: list[str] = []
    if not automatic_updates_enabled or update_status == UPDATE_STATUS_DISABLED:
        reasons.append("updates_disabled")
    if update_status == UPDATE_STATUS_UPDATE_AVAILABLE:
        reasons.append("update_pending")
    elif update_status == UPDATE_STATUS_CHECK_FAILED:
        reasons.append("check_failed")
    elif update_status != UPDATE_STATUS_CURRENT:
        # Default-deny: "not_checked" and ANY unrecognized status value
        # mean currency is unproven, so the gate stays closed.
        reasons.append("not_checked")
    if not reasons:
        return SupportGateResult(
            allowed=True,
            reasons=(),
            message="Support submission is available.",
        )
    detail = "; ".join(_REASON_TEXT[reason] for reason in reasons)
    message = (
        "Support submissions are unavailable because "
        + detail
        + ".\n\n"
        "While automated updates are off, or the program is not fully "
        "updated, you cannot submit bug tickets or receive any other form "
        "of customer support.\n\n"
        "To restore support:\n"
        + SUPPORT_STEPS
    )
    return SupportGateResult(allowed=False, reasons=tuple(reasons), message=message)


def current_gate() -> SupportGateResult:
    """Evaluate the gate from the live settings + update session state."""
    from rhetoric.gui_settings import load_app_settings
    from rhetoric.update_service import gate_status

    settings = load_app_settings()
    return evaluate_support_gate(
        automatic_updates_enabled=bool(settings.get("automatic_updates_enabled", True)),
        update_status=gate_status(),
    )


def support_submission_block() -> SupportGateResult:
    """Gate verdict for a submission attempted right now.

    Reads the live settings and the update session. When updates are
    enabled but this session has no conclusive check yet (never ran,
    failed, or predates a re-enable), one bounded check is run on the
    spot — submission attempts are explicit user actions, unlike the
    silent background check at startup — and the verdict uses its
    fresh result.
    """
    from rhetoric import update_service
    from rhetoric.gui_settings import load_app_settings

    settings = load_app_settings()
    if not settings.get("automatic_updates_enabled", True):
        return evaluate_support_gate(
            automatic_updates_enabled=False,
            update_status=update_service.gate_status(),
        )
    status = update_service.gate_status()
    if status in (
        UPDATE_STATUS_NOT_CHECKED,
        UPDATE_STATUS_CHECK_FAILED,
        UPDATE_STATUS_DISABLED,
    ):
        update_service.check_for_update()
        status = update_service.gate_status()
    return evaluate_support_gate(
        automatic_updates_enabled=True,
        update_status=status,
    )
