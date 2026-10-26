# Final Release Readiness — Rhetoric 1.5.0

**Assessment date:** 2026-10-25
**Branch:** `release/1.5.0-final`
**Distribution:** Not authorized or performed.

## Status

**ENGINEERING STATUS: NOT READY for customer release.** Product rename, packaging-name migration, support routing, distribution-manifest rules, and the release version guard are implemented in the current working tree. Focused tests pass. The full suite has not yet been re-run against a stable final tree. Linux/Windows frozen installed-artifact acceptance and human audio review remain unverified.

**COMMERCIAL STATUS: BLOCKED.** The EULA remains a draft requiring owner and qualified-counsel approval. The soft-launch gate also requires a current checksum manifest; that manifest can only be generated from the committed release head. LGPL source/replacement obligations remain a warning.

## Current gate evidence

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Core functionality | Partial | Focused tests pass; final full suite and real output/human listening remain. |
| Installation | Partial | New Rhetoric entrypoints and legacy forwarders exist. Frozen Linux/Windows installed-artifact and clean-machine acceptance remain. |
| Quality | In progress | Fresh environment installs; pip check, pip-audit, release version check, notices check and secret scan completed. A prior full run overlapped edits and is invalid as final evidence. |
| Privacy and security | Partial | Gitleaks scanned 1,110 commits with no findings. detect-secrets reports high-entropy candidates requiring review; no clean finding-free claim is made. |
| Distribution | Blocked | Old-version artifacts/manifests were removed. Current checksums, built artifacts, hosted CI and publication remain. |
| Commercial approval | Blocked | Owner/counsel approval, offer and voice-rights confirmation, and publication authorization are outstanding. |

## Verified in this pass

- Fresh Python 3.12 environment: `pip install -e '.[dev]'` succeeded.
- `pip check`: no broken requirements.
- `pip-audit`: no known vulnerabilities in auditable installed packages; local and non-PyPI dependencies were skipped.
- `scripts/release.py --check`: version invariant passes after removing stale 1.1.1–1.4.2 release artifacts.
- Third-party notices: current, 117 components.
- Soft-launch check: blocked by draft EULA and missing current checksum manifest; LGPL obligations warning.
- Focused support/logging checks: 34 passed.
- A prior full-suite run overlapped source edits and produced contaminated results; it will be rerun after edits stop.

Prior CI run IDs, commit hashes, package measurements, and security findings in older release records describe historical states and are not evidence for this release head.

## Required owner actions

1. Obtain qualified-counsel review and owner approval of the EULA and commercial terms.
2. Confirm voice-asset rights and third-party obligations.
3. Have a human reviewer assess intelligibility, speaker assignment, and usability of the exact release output.
4. Complete clean-machine install, first-user, project save/reopen, update, rollback, and uninstall acceptance.
5. Explicitly authorize publication after all engineering and commercial gates pass.
6. Do not rewrite remote history; ordinary branch push is authorized.
