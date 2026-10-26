# Phase 1 Distribution Progress — 1.5.0 RC

**Current status (2026-10-25):** Partial; no release artifacts are approved. Old 1.3.0–1.4.2 checksum manifests and generated archives were removed. `MANIFEST.in` and `.gitignore` now agree on release exclusions; `tests/test_distribution_manifest.py` verifies tests and `scripts/ci_smoke_render.py` do not ship. The canonical release command built the Rhetoric 1.5.0 sdist and wheel and their checksums. Both archive checksums verified. This build predates the final release-record edits and must be rebuilt from the final head. The final filtered package inventory is still to be regenerated.

> Historical progress below describes a previous release-candidate state. Its metrics and CI results are not current-head evidence.

Previous progress notes are retained in [`archive/PHASE1_DISTRIBUTION_PROGRESS_HISTORICAL.md`](archive/PHASE1_DISTRIBUTION_PROGRESS_HISTORICAL.md).
