# Phase 1 Distribution Progress — 1.5.0 RC

**Current status (2026-10-26):** Source package rehearsal complete; customer distribution is not approved. `MANIFEST.in` and `.gitignore` agree on release exclusions. On `92c55b86ff86`, `scripts/release.py` built the 1.5.0 sdist and wheel; both SHA-256 checks passed. The filtered inventory contained 153 sdist and 118 wheel entries outside the excluded owner-data area. Required release docs are present; tests, `scripts/ci_smoke_render.py`, and the test-only license-status shim are absent. The tracked checksums are in `release_checksums/checksums-1.5.0.sha256`. Frozen AppImage/deb builds and their CycloneDX SBOM, hosted artifacts, and clean-machine acceptance remain pending.

> Historical progress below describes a previous release-candidate state. Its metrics and CI results are not current-head evidence.

Previous progress notes are retained in [`archive/PHASE1_DISTRIBUTION_PROGRESS_HISTORICAL.md`](archive/PHASE1_DISTRIBUTION_PROGRESS_HISTORICAL.md).
