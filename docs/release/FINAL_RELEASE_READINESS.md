# Final Release Readiness — Rhetoric 1.5.0

- **Assessment date:** 2026-11-13 (fix pass of 2026-11-12)
- **Branch:** `release/1.5.0-final`
- **Distribution:** Not authorized or performed. No tag, no GitHub release.

## Status

**ENGINEERING STATUS: READY for the owner's release decision**, with the
release-publication steps below still open and owner-only. Every functional
hosted job passed at `a37c8b4`, and this fix pass closes the seven issues the
owner reported from live use. The remaining engineering work is installed-
lifecycle qualification on the frozen Linux artifacts and human listening
review of the CJK and Arabic corpus cases (see "Acceptance still open").

**COMMERCIAL STATUS: CLOSED by owner decision.** The owner decided on
2026-11-12 that the EULA ships as written and that independent counsel review
is waived. The storefront (§ "Owner-only decisions") is still open.

## Suite and CI story

- **Full suite at this fix pass's head** (serial, main checkout venv):
  **2,275 passed, 0 failed, 0 skipped** in 736 s, `QT_QPA_PLATFORM=offscreen`.
  This is after hybridized voices were removed (fewer tests) and the new
  wheel-guard, numbering, legacy-path, cache-honesty and render-work tests were
  added. The earlier run at `a37c8b4` was 2,244 passed / 1 failed, the single
  failure being the in-tree pre-rename `src/rhetoric.egg-info` artifact
  described in the fixed-pass table; hosted CI at that head passed both Ubuntu
  suite jobs on fresh checkouts.
- **Hosted CI at `a37c8b4`** (run 43365230005): Ubuntu and Windows full suites,
  the Vulkan no-skip suite, Linux frozen AppImage/deb build, Windows installer
  end-to-end, and the compiled license core all passed. The only failing job was
  the repository's own bookkeeping gate ("Suite counts recorded or inheritable");
  the remedy is `scripts/certify_suite_counts.py --record`, recorded in
  `scripts/suite_counts_baseline.json`.
- **This fix pass** is covered by targeted tests per fix plus hosted CI at the
  final head. Per-fix evidence is listed below.

## This fix pass (2026-11-12 → 13)

| Item | Verdict | Evidence | Commit |
| --- | --- | --- | --- |
| Vulkan timeout death (owner's settings held `audio_cpp_timeout: 3` against a 600 s default, and model load + shader compile was charged inside every per-synthesis budget) | **Fixed and verified** | 60 s floor at the engine choke point + 120 s startup allowance per subprocess budget; settings-load clamp. The owner's exact scenario now completes: RC 0 in 28 s, FLAC 24 kHz / 16.58 s / decode OK. 15 new tests, 2 updated. Logs: `~/vulkan-measure-2026-11-12.log`, `~/vulkan-verify-a-2026-11-12.log`. | `eaba85e` |
| Automated-updates opt-out sat in Shared Render Settings | **Fixed** | The opt-out is a checkable Settings-menu action (Advanced, default on); same `automatic_updates_enabled` key, same warning text, same support gate. 3 new tests + placement pins updated. | `9e5ee1f` |
| Mouse wheel hijacked spin boxes / combo boxes / sliders in scrollable panels | **Fixed** | The controls themselves are focus-gated subclasses (`gui_wheel.WheelSpinBox`, `WheelComboBox`, `WheelSlider`, `WheelDoubleSpinBox`): an unfocused control scrolls its enclosing panel, a focused one keeps the wheel. Implemented this way after both event-filter designs crashed hosted runners inside Qt's filter dispatch; no filter is installed anywhere now. 7 tests. | `fe56d8a` |
| Output filename default overwrote earlier renders | **Fixed** | The field defaults to `<input stem>_No_<n>` (the recorder's `Seashell_No_N` scheme), taking the next free number in the chosen folder; re-derived at render time; a typed name is never renumbered. Tests pin numbering, gaps, and typed names. | `aab6ce3` |
| Working material scattered into the user's output folder | **Fixed** | Stems, cache, logs, previews, `render_plan.json`, and the hidden subprocess job directory now live in the app's `render-work` home (`~/.local/share/rhetoric/render-work`, `RHETORIC_RENDER_WORK` override). The chosen folder receives only the finished FLAC (and SRT when enabled). The tracked `Output/.gitkeep` was removed. A deterministic render test asserts the output folder holds exactly the FLAC. | `b7f8494` |
| Legacy path values inside settings (`the oracle tts` Documents folders, `the_oracle` data dir) | **Fixed** | Load-time migration rewrites default input/output, saved project output dir, speaker reference paths, and the recorder's folder onto the current Rhetoric homes; the next save persists it. 4 new tests. The owner's live file still needs one GUI restart to pick the migration up (his GUI was open during this pass, so it was not hand-edited). | `4262a13` |
| Cache assembly presented as a fresh render | **Fixed** | The render plan records `cache_hit_segments` / `segment_count` before dispatch; the completion log states either "no audio was synthesized in this run" or "reused N of M segments". A second deterministic render of the same plan is asserted to report `rendered_from_cache=1`. The stem-cache key was audited against every audio-changing input (text, speaker, reference hash, variant, backend, voice settings, engine version, seed) with a new sensitivity test; no gap was found — correction mode is covered because the key hashes the post-correction text. | `4262a13` |
| Hybridized voices (GUI section, blend logic, settings, tooltips, wizard, tests) | **Removed entirely** | `audio/blend.py`, the blend voice catalog, `SpeakerSettings`/`VoiceProfile` blend fields, the cast-panel controls, the tooltip/wizard text, and the tests that pinned them are gone. Existing cast entries carrying blend fields still load: the loaders ignore the dropped keys. Non-hybrid cast management and rendering are unchanged (233 tests green across the affected modules). | `59999d6` |

Additional bookkeeping commit: `49686ad` adjudicates the wheel guard's Qt
readership pairs in the patch-couple policy and prunes the removed blend
catalog's sanctioned split.

## Earlier evidence carried forward

- **Windows edition fix** (`3652354`, `78630fe`): the Inno Setup installer and
  its launcher/edition behavior are qualified end to end — install smoke,
  certification soak, and a fully offline install, activation, and render.
- **Rename purge** (`a98a307`, `86df7ee`, `a37c8b4`): package
  `the_oracle` → `rhetoric`, `ORACLE_*` → `RHETORIC_*`, data-folder migration,
  brand guard restored.
- **Pins audit (report-only; owner's decision, pins unchanged):** the base
  install resolves and `[ml]` alone resolves. `[chatterbox]` and
  `[ml,chatterbox]` do **not** co-resolve today (`transformers==5.20.0` in
  `[ml]` vs `chatterbox-tts 0.1.7` wanting `transformers==5.2.0`;
  `Pillow>=13.0.0` vs `gradio 6.8.0` wanting `pillow<13`). The product's
  managed install path (`manage_install`, chatterbox `--no-deps`,
  hash-verified from the offline bundle) is unaffected and was proven end to
  end in the 2026-11-11 airgap proof.
- **Vulkan backend sound** (two independent renders): with a sane timeout the
  script renders clean on the RX 5700 XT — exit 0, FLAC 24 kHz mono,
  ~16.5–17.4 s. Per-utterance synthesis 1.9–3.6 s; audio.cpp subprocess
  startup (2 GB GGUF load + RADV shader compile) ~10–14 s cold. Evidence
  renders in `~/rhetoric-parallel-verify/`.
- **Audio acceptance:** the owner's verdict "Those renders sound fine" covers
  the ENGLISH corpus cases 1, 2, 3 and 6 only. Case 4 (CJK) and case 5
  (Arabic) are **automated-metrics-only**; human listening review is
  outstanding. The corpus must not be presented as fully human-reviewed.

## Acceptance still open

1. **Installed-lifecycle qualification** on the frozen Linux AppImage and deb
   in fresh Ubuntu 24.04 containers (activation with a throwaway key, cold
   download/resume/offline/low-disk, doctor, first render, project save/reopen,
   settings persistence, update, rollback, uninstall, data retention).
2. **Human listening review of corpus cases 4 (CJK) and 5 (Arabic).**
3. **Data-cleanup follow-up (pending, GUI was open during this pass):** the
   owner's GUI was running, so the remaining working material in the repo
   `Output/` folder (`cache/`, `logs/`, `stems/`, `render_plan.json`) and the
   legacy Documents folder were not moved into `render-work/`. The source-side
   fix means new renders write there; moving the old material is a follow-up
   once the GUI is closed.
4. **Windows installed-product qualification** (hosted installer E2E is green;
   a Windows guest install is still open).

## Owner-only decisions and actions

1. **Dependency pins:** the `[chatterbox]` / `[ml,chatterbox]` co-resolution
   conflict above is a product decision; pins were not changed.
2. **Storefront:** Lemon Squeezy store creation remains blocked (bot-walled;
   support ticket pending). No payment path ships in this repository.
3. **v1.5.0 tag and publish:** explicitly the owner's decision. This pass
   pushed commits only.
4. **Publication** of the GitHub release and any store listing.
5. Whether the owner's ~62 MB of reference WAVs stay in the public history
   (left untouched).

Ordinary branch push is authorized; history rewriting and publication are not.
