# Final Release Readiness — Rhetoric 1.5.0

- **Assessment date:** 2026-10-26
- **Branch:** `release/1.5.0-final`
**Distribution:** Not authorized or performed.

## Status

**ENGINEERING STATUS: NOT READY for customer release.** The customer-facing
rename, distribution names, compatibility shims, support routing, version
guards, package-content rules, and experimental GPU labels are implemented.
The canonical release command passed the full suite and rebuilt the source
archive and wheel. Exact-head hosted CI, Linux frozen-artifact installation,
first-user lifecycle acceptance, and current-corpus audio review remain open.

**COMMERCIAL STATUS: BLOCKED.** The EULA is a draft awaiting owner and
qualified-counsel approval. The last observed soft-launch check reported the
draft EULA blocker and an LGPL notice/source/replacement obligation warning.
The check was not rerun after final edits because its automated asset review is
outside the authorized scope.

## Verified evidence

- Canonical release command: `./.venv/bin/python scripts/release.py` on
  `92c55b86ff86` — **2,144 passed, 6 warnings, 0 failed in 395.90 seconds**;
  the version invariant passed and the command built the Rhetoric 1.5.0 sdist,
  wheel, and checksum manifest.
- Fresh-worktree recorder: `d39a94573d35` — **2,141 passed, 3 skipped,
  0 failed/errors**. The Vulkan device smoke was the identified environment
  skip. Skip IDs are incomplete because `tests/test_skip_audit.py` clears the
  ledger during the run.
- `sha256sum -c checksums-1.5.0.sha256` passed both source artifacts:
  wheel `879733b64fbc73bbbf41616d9046d1ba3dbb555b7d452f80167da3ce908466ba`;
  sdist `07b92f8d4fd26a20327d455e93466818e76e342f952160143c7f7b7c332d72a8`.
- Filtered package inventory: 153 sdist entries and 118 wheel entries outside
  the excluded owner-data area. Required release docs are present; tests,
  `scripts/ci_smoke_render.py`, and the test-only license-status shim are
  absent. The suite-count baseline and tracked checksum copy are also absent
  from the sdist/wheel, so subsequent release-record commits do not change the
  built package bytes.
- `scripts/release.py --check` and `--check-packaging` pass; versions agree at
  1.5.0. The changelog heading was re-stamped for 2026-10-26 with the release
  tool.
- Fresh Python 3.12.3 editable dev install, `pip check`, and `pip-audit`
  completed. No broken requirements or known vulnerabilities were reported in
  auditable installed packages; local/non-PyPI dependencies were skipped.
- A local CycloneDX run emitted a valid CycloneDX SBOM with 168 components and
  no known vulnerabilities. The frozen Linux CI builder now emits its own
  SBOM from the build environment and checksums it; the hosted artifact is not
  yet available.
- `gitleaks git --log-opts='--all' --redact --no-banner`: no findings across
  1,110 commits. `detect-secrets` reported 147 candidates across 18 files
  (144 high-entropy hex, 1 keyword, 2 Base64); these are not asserted to be
  findings or clean. Values are not reproduced here.
- Current-release hosted CI is pending until the final branch head is pushed.
  Historical run IDs and old-repository results do not qualify this head.

## Acceptance still open

1. Current-head CI: Linux frozen artifacts and SBOM, Vulkan smoke,
   Windows installer smoke, and ten consecutive Windows GUI certification
   runs; also run the manual Windows certifier fault-capture workflow.
2. Install the frozen Linux AppImage and deb in fresh Ubuntu 24.04 containers
   with only documented prerequisites. Exercise activation using a throwaway
   test key, cold download/resume/offline/low-disk behavior, doctor, first
   render, GUI, project save/reopen, settings persistence, update, rollback,
   uninstall, and data-retention behavior.
3. Verify the installed LGPL library-replacement path and document fulfillment
   of source/replacement obligations.
4. Complete the six-case production audio corpus and independent human review
   described in [`REAL_AUDIO_ACCEPTANCE_1.5.0.md`](REAL_AUDIO_ACCEPTANCE_1.5.0.md).
   Historical 1.4.2 outputs are not evidence for this candidate.
5. Measure CPU real-time factor, peak RAM, and disk per audio hour; run the
   100-cycle render/cancel/close soak; and record keyboard-only, high-DPI,
   1366x768, theme contrast, and failure-path acceptance.
6. Windows remains explicitly unsupported and excluded from the proposed paid
   offer. CUDA and Vulkan remain experimental and are labeled that way in the
   UI, documentation, CLI help, and EULA draft.

## Owner-only decisions and actions

1. Have qualified counsel review the EULA and proposed license decisions,
   including whether the no-refund term is enforceable with the payment
   processor and across relevant jurisdictions. Keep the draft marker until
   approval.
2. Confirm production signing-key custody in the secret manager and remove the
   owner's local seed copy at `~/.config/the-oracle/license-signing-seed`.
   No production seed was generated, displayed, or used in this work.
3. Have an independent human reviewer listen to exact final-head outputs and
   record reviewer, date, commit, intelligibility, speaker assignment,
   transitions, pauses, clipping/silence, usability, and defects. The verdict
   must remain **PENDING** until supplied by that reviewer.
4. Confirm the old repository is deleted or private and whether forks remain;
   remove old local clones and the private recovery bundle when no longer
   needed.
5. Authorize publication only after all engineering and commercial gates pass.

Ordinary branch push is authorized; history rewriting and publication are not.
