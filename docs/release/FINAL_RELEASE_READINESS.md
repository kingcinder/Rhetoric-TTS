# Final Release Readiness — Rhetoric 1.5.0

**Assessment date:** 2026-10-25  
**Source branch:** `release/1.5.0-final`  
**Distribution:** Not authorized or performed.

## Status

**ENGINEERING STATUS: NOT READY for customer release.** The customer-facing
rename, distribution names, compatibility shims, support routing, version
guards, package-content rules, and explicit experimental GPU labels are
implemented. The canonical release command passed its full test suite and
built a source archive and wheel. Linux frozen-artifact installation,
first-user lifecycle acceptance, real-corpus audio review, and current-head
hosted CI remain open.

**COMMERCIAL STATUS: BLOCKED.** The EULA is a draft awaiting owner and
qualified-counsel approval. The last observed soft-launch check reported the
draft EULA blocker and an LGPL notice/source/replacement obligation warning.
The gate has not been rerun against the final rebuilt manifest because its
asset check is outside the owner's authorized review scope.

## Verified evidence

- Canonical release command: `./.venv/bin/python scripts/release.py` —
  **2,142 passed, 6 warnings, 0 failed in 380.29 seconds**; version check
  passed; built the 1.5.0 sdist, wheel, and checksum manifest.
- Fresh-worktree count for source commit `bb0c9846fb44`: **2,139 passed,
  3 skipped, 0 failed/errors**. The Vulkan device smoke was the identified
  environment skip; the skip-id ledger reports incomplete IDs because
  `tests/test_skip_audit.py` clears it during the run.
- `sha256sum -c checksums-1.5.0.sha256` in `release_artifacts/`: both the
  sdist and wheel passed. This build predates the final phase-record update
  and must be regenerated from the eventual final source head.
- `scripts/release.py --check`: version invariant passes.
- `scripts/release.py --check-packaging`: package, installer, and artifact
  versions match 1.5.0.
- Fresh Python 3.12.3 editable dev install, `pip check`, and `pip-audit`
  completed. No broken requirements or known vulnerabilities were reported
  in auditable installed packages; locally sourced/non-PyPI dependencies were
  skipped.
- `gitleaks git --log-opts='--all' --redact --no-banner`: no findings across
  1,110 commits. `detect-secrets` reported 147 candidates across 18 files
  (144 high-entropy hex, 1 keyword, 2 Base64); those are not asserted to be
  secrets or clean. No values are reproduced here.
- Targeted rename/support, UI, EULA-copy, release-guard, package-manifest,
  and tooltip tests passed. The canonical full run includes the complete test
  suite and the current experimental-GPU UI test.
- Current-release CI is still pending until the final branch head is pushed.
  Historical run IDs and old-repository results do not qualify this head.

## Acceptance still open

1. CI on the pushed final source head, including Linux frozen artifacts,
   Vulkan smoke, Windows installer smoke, and ten consecutive Windows GUI
   certification runs.
2. Install and exercise the frozen Linux artifacts in a fresh Ubuntu 24.04
   VM/container with only documented prerequisites, including activation with
   a throwaway test key, no-cache download/resume/offline/low-disk cases,
   first render, GUI flows, project save/reopen, update, rollback, and
   uninstall/data-retention checks.
3. The installed LGPL library-replacement exercise and a documented fulfillment
   path for source/replacement obligations.
4. The current fixed-corpus automated real-audio measurements and an
   independent human listening verdict. Historical 1.4.2 audio records do not
   qualify 1.5.0.
5. Measured CPU real-time factor, peak RAM, disk per audio hour, a 100-cycle
   render/cancel/close soak, keyboard-only and display-size acceptance, and
   failure-path checks for missing ffmpeg/network, corrupt cache, full disk,
   killed render child, and GPU loss.
6. Windows remains explicitly unsupported and excluded from the proposed paid
   offer. CUDA and Vulkan remain experimental and are labeled that way in the
   UI, documentation, CLI help, and EULA draft.

## Owner-only decisions and actions

1. Have qualified counsel review the EULA and proposed license decisions,
   including whether the no-refund term is enforceable with the payment
   processor and across relevant jurisdictions. The draft must remain a draft
   until approved.
2. Confirm production signing-key custody in the secret manager and remove the
   owner's local seed copy at `~/.config/the-oracle/license-signing-seed`.
   No production seed was generated, displayed, or used in this work.
3. Have an independent human reviewer listen to the exact final-head output
   and record reviewer, date, commit, intelligibility, speaker assignment,
   transitions, pauses, clipping/silence, usability, and defects. The verdict
   must remain **PENDING** until that reviewer supplies it.
4. Confirm the old repository is deleted or private and whether forks remain;
   remove old local clones and the private recovery bundle when no longer
   needed.
5. Authorize publication only after the engineering and commercial gates pass.

Ordinary branch push is authorized; history rewriting and publication are not.
