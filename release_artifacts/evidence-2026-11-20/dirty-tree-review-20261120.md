# Dirty-tree review — Rhetoric V1.00a-beta_build, 2026-11-20

- **Reviewer:** Wren (dirty-tree review agent, one of six parallel Rhetoric agents)
- **Date:** 2026-11-20 ~14:05 PST
- **Checkout:** `/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric`, branch `V1.00a-beta_build`
- **HEAD:** `49f06787a995704467ef38ea71f55951ff8a71c7` (2026-11-17 14:41 -0800, "test(ci): record final ship-today evidence count")
- **Status at review time:** 94 entries — 8 deleted, 30 modified, 56 untracked. No commit or push made by this review (read-only except this file).

## Headline

**NO DRIFT in anything that determines the RC13 artifact. The RC13 candidate still corresponds exactly to the current tree.**

- RC13 tarball SHA-256 recomputed by this review: `b1fcd5e4f8880776e4ae076aae5466adf48fa5e025d4dc5daf24ad8b10a97f8d` — exact match to `candidate-rc13/build-identity.json`.
- RC13 `.deb` SHA-256 recomputed by this review: `8883329c3f8c340b2b6e6757aa3d10e38dd6fafe1bc3169e6cd08d41f82fe992` — exact match.
- The two source files fingerprinted in `build-identity.json` (`src/rhetoric/audio/recorder.py`, `tests/test_recorder.py`) hash exactly to their snapshot values.
- No `src/`, `packaging/`, `scripts/`, or `tests/` file has an mtime after the RC13 build (tarball 2026-11-19 18:33, `.deb` 18:20) or after the snapshot (2026-11-19 19:48). The only files changed after the snapshot are documentation and evidence.
- A sibling agent independently re-verified the same hashes today (`current-byte-verification-20261120-rerun.json`, 2026-11-20 13:55, gzip integrity OK, SBOM hash matches) and re-ran the release-path suite: **176 passed in 55.82s** (`release-path-tests-20261120-wren.log`).

Caveat (stated plainly): `build-identity.json` fingerprints only two source files. For the other 28 modified files the no-drift conclusion rests on mtimes (all ≤ 2026-11-19 18:07, before the build) plus the byte-identical artifact hashes above — the artifact itself is unchanged, and it was built from this tree.

## 1. Inventory — all 94 dirty entries

| Group | Count | Entries |
|---|---|---|
| Deleted (`D`) | 8 | All under `Input/` (see §3) |
| Modified (`M`) | 30 | docs 7, packaging 3, `pyproject.toml` 1, scripts 5, `src/` 4, tests 10 |
| Untracked (`??`) | 56 | New `Input/` files 4, `docs/release/SIGNING.md` 1, `scripts/sign_release_artifact.py` 1, new test files 3, evidence dirs 4, build-output dirs 40, temp offline roots 3 |

`git diff --stat` on the 37 tracked changed files: **493 insertions, 2,243 deletions** (2,074 of the deletions are the 8 removed `Input/` files).

## 2. What changed — modified files by group

### src/ (4 files, +105 / −43) — release-path fixes, all inside the RC13 build
- `src/rhetoric/audio/recorder.py` (+35/−1): new `_import_sounddevice()` shim that routes sounddevice's PortAudio lookup to the exact PyInstaller-bundled `libportaudio.so.2`, so a fresh offline install needs no host PortAudio.
- `src/rhetoric/eula_acceptance.py` (+10/−4): EULA acceptance record now goes to the per-user config dir when the install root is not writable (system installs), instead of always beside the install.
- `src/rhetoric/gui_render.py` (+47/−20): render-child environment now applies the offline env on offline installs and pins `VK_ICD_FILENAMES` to the Radeon ICD manifest for Vulkan jobs (loader-wide ICD enumeration was losing the RX 5700 XT in audio.cpp SDMA init); new `_render_subprocess_command()` dispatches through the frozen entrypoint (`--rhetoric-render-subprocess`) when frozen.
- `src/rhetoric/licensing/store.py` (+43/−18): token store moves to per-user installed store with legacy migration, candidate fallback across store locations, and `0600` permissions on the token file (atomic write via `os.open` + `fsync` + `chmod`).

### packaging/ (3 files)
- `packaging/linux/entrypoint.py` (+13): frozen Numba cache configuration (`UserWideCacheLocator`) plus `--rhetoric-render-subprocess` dispatch to the render subprocess main.
- `packaging/linux/rhetoric.spec` (+2/−2): collect torchvision dynamic libs via `collect_dynamic_libs`.
- `packaging/linux/README.md` (+5/−2): wording updates.

### scripts/ (5 files) + pyproject.toml
- Torch bump across `scripts/build_frozen_linux.py` and `pyproject.toml`: torch 2.6.0 → 2.15.0, torchaudio 2.6.0 → 2.11.1, torchvision 0.21.0 → 0.29.2; added floors for `typing-extensions>=4.13.0`, `setuptools>=77.0.3`, `sympy>=1.13.3`; removed the stale `setuptools<82` comment.
- `scripts/build_offline_linux_kit.py` (+33/−6): kit now bundles the owner-provided `Seashells/` voice-reference directory (build fails if it is missing or empty), records voice assets with per-file SHA-256 in the kit manifest, and install/uninstall wording now says the activation license and installed Seashells directory are retained.
- `scripts/build_offline_bundle.py` (+5/−6), `scripts/manage_install.py` (+1/−1), `scripts/patch_chatterbox_metadata.py` (+2): small adjustments.

### tests/ (10 files, +177 / −17)
Mostly new/expanded coverage for the above: `test_licensing_store.py` +50, `test_offline_linux_kit.py` +39, `test_recorder.py` +35, `test_offline_bundle.py` +23/−10, `test_eula_acceptance.py` +14, `test_frozen_linux_packaging.py` +8, `test_chatterbox_metadata_patch.py` +4, `test_install_boundary.py` +2/−2, `test_release.py` +1/−1.

### docs/ (7 files)
- `docs/release/V100A_SHIP_TODAY_CHECKLIST.md` (+28/−26) and `V100A_SHIP_TODAY_GOAL.md` (+8/−11): the ledger rewritten from RC1 (candidate `32ac9df`, HEAD `6a75f88`) to RC13 (HEAD `49f0678`), with every P0 row re-evidenced against `candidate-rc13/`.
- `docs/LICENSING_OPS.md` (+44/−34): signing-seed vs release-signature OpenPGP identity split (never reuse the Ed25519 activation seed for installer signatures); vendor keygen now uses `--repo-root` and seals to `$HOME/secrets/rhetoric-seed-k3.gpg`.
- `docs/LICENSING_DESIGN.md` (+11/−4), `docs/LICENSING_THREAT_MODEL.md` (+6/−4), `docs/SOFT_LAUNCH.md` (+16/−10), `docs/legal/LICENSE_DECISIONS_PROPOSED.md` (+3/−3): conforming edits.

### Untracked code (new, not in HEAD)
- `scripts/sign_release_artifact.py` (196 lines) + `tests/test_sign_release_artifact.py` (175 lines): release-signing tooling and its tests. NOTE: the tooling exists but P0-11 is still BLOCKED — there is no eligible signing key; the tool cannot sign anything today.
- `tests/test_gui_subprocess_command.py` (140 lines), `tests/test_linux_entrypoint.py` (37 lines): tests for the new frozen entrypoint / subprocess command.

## 3. The eight deleted Input/ files — verified safe

| Deleted file (HEAD) | Lines | History | HEAD blob |
|---|---|---|---|
| `Input/READ_THIS_TO_RECORD_SEASHELLS.txt` | 108 | 5 commits, last 2026-11-12 | present |
| `Input/Read Aloud transcript.txt` | 1,757 | 8 commits, last 2026-10-25 | present |
| `Input/What is, reality.txt` | 10 | 10 commits, last 2026-10-25 | present |
| `Input/cli_short.txt` | 3 | 8 commits, last 2026-10-25 | present |
| `Input/local_audio_test.txt` | 3 | 4 commits, last 2026-11-12 | present |
| `Input/recording prompt.txt` | 55 | 3 commits, last 2026-10-25 | present |
| `Input/stream_of_consciousness_dialogue_with_typos.txt` | 137 | 3 commits, last 2026-10-25 | present |
| `Input/test.txt` | 1 | 8 commits, last 2026-10-25 | present |

**Committing these deletions loses no unique owner work from the repo.** Every file exists in git history (3–10 commits each) and every blob exists at HEAD `49f0678`; `git checkout HEAD -- Input/` restores all eight. Verified, not assumed.

The deletions are a deliberate swap, not an accident. Four replacement files were created untracked on 2026-11-16/17 and are the inputs the RC13 renders actually used (referenced by `candidate-rc13/render-matrix.json`, `cpu-vulkan-parity.json`, `monologue-cpu-vulkan-parity.json`, `current-verification-20261119.json`):

| Replacement (untracked) | Size | Relation to deleted file |
|---|---|---|
| `Input/What_Is_Reality_Output_Test_File.txt` | 2,054 B | Content-identical to deleted `What is, reality.txt` (verified by direct comparison) |
| `Input/Stream_of_Consciousness_Dialogue_2Party_AI_Generated_Test_File.txt` | 12,154 B | Content-identical head to deleted `stream_of_consciousness_dialogue_with_typos.txt` |
| `Input/High_Quality_Seashells_Instruction_set_and_Teleprompter_Text.txt` | 2,936 B | Same text as `READ_THIS_TO_RECORD_SEASHELLS.txt` except one word: "Rhetoric use case" → "Oracle use case" |
| `Input/Recording_Studio_Generic_Teleprompter_File.txt` | 1,299 B | Different content — new generic teleprompter sentences, replacing the "Good morning!" monologue of `recording prompt.txt` |

`Input/cli_short.txt`, `Input/local_audio_test.txt`, and `Input/test.txt` were 1–3 line throwaway test scripts with no replacement; nothing references them except the test below.

**Code references to the deleted names (checked with `git grep` over tracked code/docs):**
- `scripts/crash_hunt.py:56` and `tests/test_ingest_transformer.py:516` reference `tests/fixtures/stream_of_consciousness_dialogue_with_typos.txt` — the fixture copy, which **still exists on disk** (12,154 B). Unaffected.
- `tests/test_ingest_transformer.py:175` (`test_bundled_inputs_are_issue_free`) reads `Input/What is, reality.txt`, `Input/cli_short.txt`, `Input/test.txt` — but it **skips missing files** (`if not path.is_file(): continue`). No test failure, but the check is now vacuous for those three files: a silent coverage loss, not a break. Recommend updating it to the new filenames.
- `tests/test_recording_studio.py:47,56` creates `Read Aloud transcript.txt` itself in a temp dir and asserts on it. Unaffected.
- `docs/release/WORKTREE_COMMIT_SCOPE_2026-11-17.md` references both the deleted and the replacement filenames — the swap was documented on 2026-11-17 as part of the worktree commit scope.

## 4. Drift vs the RC13 snapshot — the detailed check

Snapshot: `release_artifacts/evidence-2026-11-19/candidate-rc13/build-identity.json`, written 2026-11-19 19:48. It records `git_head 49f0678`, `working_tree_dirty: true`, the two fingerprinted source hashes, and the artifact hashes.

**Artifact hashes — recomputed by this review (independent of the sibling re-verification):**

| Artifact | Recorded in snapshot | Recomputed 2026-11-20 | Match |
|---|---|---|---|
| `linux-frozen-rc13-20261119/Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz` (4,985,608,078 B) | `b1fcd5e4f8880776e4ae076aae5466adf48fa5e025d4dc5daf24ad8b10a97f8d` | `b1fcd5e4f8880776e4ae076aae5466adf48fa5e025d4dc5daf24ad8b10a97f8d` | YES |
| `linux-frozen-rc13-20261119/rhetoric_1.5.0_amd64.deb` (472,970,192 B) | `8883329c3f8c340b2b6e6757aa3d10e38dd6fafe1bc3169e6cd08d41f82fe992` | `8883329c3f8c340b2b6e6757aa3d10e38dd6fafe1bc3169e6cd08d41f82fe992` | YES |

**Fingerprinted source files:**

| File | Snapshot hash | Current hash | Match |
|---|---|---|---|
| `src/rhetoric/audio/recorder.py` | `9d24eb11dfcf1994dd6cd8897f8e217878529a617bf3e57218d6e7fe0bae2170` | `9d24eb11dfcf1994dd6cd8897f8e217878529a617bf3e57218d6e7fe0bae2170` | YES |
| `tests/test_recorder.py` | `9fb2c1b14e6425e1bf6611505a7350e13c4062e14324702586a8828aabc46fc8` | `9fb2c1b14e6425e1bf6611505a7350e13c4062e14324702586a8828aabc46fc8` | YES |

**mtime timeline (all times PST):**
- Last code/packaging/script/test modification: `src/rhetoric/audio/recorder.py`, 2026-11-19 18:07:38 (test_recorder.py 18:07:00). All other code files are Nov 18 or earlier.
- RC13 build: `.deb` 2026-11-19 18:20:31, tarball 18:33:01. The build ran AFTER the last code change.
- Snapshot `build-identity.json`: 2026-11-19 19:48:15.
- Files changed after the snapshot: `docs/release/V100A_SHIP_TODAY_GOAL.md` (20:28 Nov 19), `docs/release/SIGNING.md` untracked (20:35 Nov 19), `docs/SOFT_LAUNCH.md` (21:08 Nov 19), `docs/release/V100A_SHIP_TODAY_CHECKLIST.md` (01:26 Nov 20), and the untracked `release_artifacts/evidence-2026-11-20/` dir (01:42 Nov 20). **Documentation and evidence only — no code, packaging, script, or test file changed after the snapshot or after the build.**

**Conclusion: NO DRIFT.** The RC13 artifact corresponds exactly to the current tree's code state. The post-snapshot changes are checklist/goal wording, the SOFT_LAUNCH doc, the new SIGNING.md doc, and new evidence files — none of which affect the built artifact.

## 5. Risk flags

1. **The four replacement `Input/` files are untracked.** If the tree is committed without `git add`ing them, the repo will record the deletions but not the replacements — the current render inputs would exist only on this disk. The deletions and the four new files must be committed together.
2. **Untracked build output is enormous — 277 GB under `release_artifacts/` alone.** `linux-frozen-rc13-20261119/` 17 GB, `linux-rc-32ac9df/` 20 GB, `linux-frozen-33618789/` 16 GB, `evidence-2026-11-19/` 35 GB, plus `squashfs-root/` 1.4 GB and three `rhetoric-rc13-offline-root-*/` temp dirs. `/media/cody/Data` is 94% full (57 GB free). Committing this bulk would bloat the repo beyond pushable and risks filling the Data drive. The final commit needs an explicit scope decision: commit the small evidence/checklist/docs, and leave the multi-GB build trees untracked (or move them off the Data drive). Do NOT `git add -A`.
3. **`test_bundled_inputs_are_issue_free` is now vacuous for three files** (see §3). Silent coverage loss; update the test to the new `Input/` filenames.
4. **"Oracle use case" wording** in the new Seashells file vs "Rhetoric use case" in the deleted one. One word, likely lineage from the Oracle project. Harmless for rendering, but flag it to the owner in case the text is customer-facing.
5. **Concurrent writers:** sibling agents are actively writing into `release_artifacts/evidence-2026-11-19/candidate-rc13/` and `release_artifacts/evidence-2026-11-20/` today (`current-byte-verification-20261120-rerun.json` 13:55, `release-path-tests-20261120*.log` 13:55–14:00). This review did not touch those files; the final commit agent should re-list the evidence dirs at commit time rather than trusting this snapshot.
6. **Signing tooling without a key:** `scripts/sign_release_artifact.py` (196 lines) and its tests are new and untracked, but P0-11 remains BLOCKED — no eligible signing key exists. The tooling is ready; the key is not. Nothing to do here except not claim otherwise.

## 6. Commit guidance (for the final commit agent)

- Safe to commit: the 30 modified files and the 8 `Input/` deletions — all verified against history and the RC13 snapshot.
- Must be added in the same commit: the 4 new `Input/` files, `docs/release/SIGNING.md`, `scripts/sign_release_artifact.py`, and the 3 new test files.
- Do NOT bulk-add `release_artifacts/` or the temp roots (see risk 2). Decide per-path; the RC13 tarball/`.deb`/SBOM and the `candidate-rc13/` evidence JSONs are the only large items with release standing, and even those deserve a deliberate choice, not `git add -A`.
- The `Input/` deletions + replacements belong in one commit with a message naming the swap; the checklist/goal ledger updates belong with the RC13 evidence they describe.
