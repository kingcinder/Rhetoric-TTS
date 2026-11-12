# Changelog

Notable user-facing changes to Rhetoric. The version number itself lives in
one place (`src/the_oracle/__init__.py`); see `scripts/release.py --check`.

## [1.5.0] — 2026-11-12

### Added

- Windows edition: Inno Setup installer for Windows 11, qualified end to end — install smoke test, certification soak, and a fully offline (air-gapped) install, activation, and render.
- One-time serial-number licensing: buy once and activate with a serial key — no account, no subscription, activation works offline.

### Changed

- Slow-hardware resilience: long renders now complete reliably on modest hardware instead of timing out (verified on a throttled 2-CPU machine).
- The 2026-10-26 release-candidate notes are superseded by this release; qualification is complete.

Earlier release history is retained in [`docs/release/archive/CHANGELOG_PRE_1.5.0.md`](docs/release/archive/CHANGELOG_PRE_1.5.0.md).
