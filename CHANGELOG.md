# Changelog

Notable user-facing changes to Rhetoric. The version number itself lives in
one place (`src/rhetoric/__init__.py`); see `scripts/release.py --check`.

## [1.5.0] — 2026-11-12

### Added

- Windows edition: Inno Setup installer for Windows 11, qualified end to end — install smoke test, certification soak, and a fully offline (air-gapped) install, activation, and render.
- One-time serial-number licensing: buy once and activate with a serial key — no account, no subscription, activation works offline.

### Changed

- Slow-hardware resilience: long renders now complete reliably on modest hardware instead of timing out (verified on a throttled 2-CPU machine).
- Vulkan renders no longer fail on a small per-synthesis timeout: the backend enforces a 60-second floor and budgets model load plus shader compile separately from synthesis.
- The automated-updates opt-out moved from the Shared Render Settings panel to a checkable action in the Settings menu (default: updates on).
- The mouse wheel now scrolls a settings panel instead of changing an unfocused spin box, combo box, or slider; a control takes the wheel only when it has keyboard focus.
- A loaded script's output filename defaults to `<script>_No_<n>`, taking the next free number in the output folder, so a render never silently overwrites an earlier one. A name you type is always used as typed.
- The output folder now holds only finished audio (and the subtitle file when enabled). Stems, caches, logs, previews, and render plans live in the app's `render-work` folder.
- Settings files that still pointed at pre-rename folders are migrated to the current Rhetoric locations on load.
- A render completed from the stem cache says so, instead of reporting a cache assembly as a fresh render.
- The 2026-10-26 release-candidate notes are superseded by this release; qualification is complete.

### Removed

- Hybridized voices (the second-voice blend picker, dominance weight, combine mode, and saved blend voices) are gone. Existing cast entries that carry the old blend fields still load; the fields are ignored.

Earlier release history is retained in [`docs/release/archive/CHANGELOG_PRE_1.5.0.md`](docs/release/archive/CHANGELOG_PRE_1.5.0.md).
