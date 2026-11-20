"""The customer support layer: diagnose, report, package, share.

Three pieces sit on top of the existing doctor and crash unit:

- :mod:`rhetoric.support.diagnostics` — a structured, read-only snapshot
  of the machine and install (doctor verdict included, heavy imports never
  loaded).
- :mod:`rhetoric.support.report` — the bug-report model, validation, and
  Markdown rendering; :mod:`rhetoric.support.store` keeps drafts locally.
- :mod:`rhetoric.support.packaging` — one zip containing the report, the
  diagnostics, and the existing redacted support bundle; plus prefilled
  issue/email links from :mod:`rhetoric.support.channels`.

Import discipline matches the rest of the suite: stdlib plus Rhetoric's own
small modules, nothing runs at import time, and there is no transport code.
"""

from __future__ import annotations

from rhetoric.support.channels import (
    ISSUE_REPO,
    SUPPORT_EMAIL,
    issue_body,
    issue_title,
    issue_url,
    mailto_url,
    share_note,
)
from rhetoric.support.diagnostics import collect_diagnostics, compact_diagnostics
from rhetoric.support.packaging import ReportPackageResult, build_report_package
from rhetoric.support.report import (
    AREAS,
    SEVERITIES,
    BugReport,
    new_report,
    new_report_id,
    report_json,
    report_markdown,
    validate_report,
)
from rhetoric.support.store import (
    MAX_REPORTS,
    delete_report,
    list_reports,
    load_report,
    prune_reports,
    save_report,
    store_dir,
)

__all__ = [
    "AREAS",
    "ISSUE_REPO",
    "MAX_REPORTS",
    "SEVERITIES",
    "SUPPORT_EMAIL",
    "BugReport",
    "ReportPackageResult",
    "build_report_package",
    "collect_diagnostics",
    "compact_diagnostics",
    "delete_report",
    "issue_body",
    "issue_title",
    "issue_url",
    "list_reports",
    "load_report",
    "mailto_url",
    "new_report",
    "new_report_id",
    "prune_reports",
    "report_json",
    "report_markdown",
    "save_report",
    "share_note",
    "store_dir",
    "validate_report",
]
