"""Rhetoric crash unit (docs/CRASH_TELEMETRY_DESIGN.md).

Local-first by construction: capture writes to the repo's crash_reports/
directory, transport does not exist, and consent is fail-closed — an
unreadable consent file means opted out. Import discipline mirrors the
licensing package: stdlib plus Rhetoric's own small modules, never a
heavyweight dependency, nothing runs at import time.
"""

from __future__ import annotations

from rhetoric.crash.bundle import (
    MAX_RECORDS,
    clear_records,
    crash_dir,
    list_records,
    write_record,
)
from rhetoric.crash.consent import CONSENT_FILENAME, consent_path, read_consent, write_consent
from rhetoric.crash.handlers import (
    current_handlers_installed,
    disable_faulthandler_catch,
    enable_faulthandler_catch,
    install,
)
from rhetoric.crash.record import build_record
from rhetoric.crash.sanitize import MAX_FIELD_CHARS, sanitize_text

__all__ = [
    "CONSENT_FILENAME",
    "MAX_FIELD_CHARS",
    "MAX_RECORDS",
    "build_record",
    "clear_records",
    "consent_path",
    "crash_dir",
    "current_handlers_installed",
    "disable_faulthandler_catch",
    "enable_faulthandler_catch",
    "install",
    "list_records",
    "read_consent",
    "sanitize_text",
    "write_consent",
    "write_record",
]
