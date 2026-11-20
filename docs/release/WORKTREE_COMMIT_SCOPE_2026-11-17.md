# Working-tree source commit scope — 2026-11-17

## Purpose and boundary

This manifest defines the source-only commit and ordinary push requested for
the current Linux frozen/offline build review. The checkout is
`release/1.5.0-final` at base `33618789b7d2eebc994fdd5c127ec8866d6ede5b`.
`release_artifacts/linux-frozen-33618789/` is the latest identified Linux
artifact set. It was produced from a dirty tree, so this manifest does not
claim that the artifact is reproducible from the base commit or that this
source commit qualifies the release.

The commit includes modified product/build source, associated QA source and
tests, and the requested ownership/release documentation. It excludes
generated binaries, frozen bundles, caches, model weights, and unrelated input
content. No Git LFS rules are needed for this source-only scope.

The rights statement being recorded is that the Developer is the sole owner of
all stock voice files included with Rhetoric except material already covered
by applicable fair-use statutes. The owner requires no additional waiver,
proof, or rights documentation. Existing file-specific license and attribution
terms remain documented and applicable.

## Included paths and roles

### Product and build source

| Path | Role |
|---|---|
| `packaging/linux/entrypoint.py` | Frozen Linux executable dispatch for GUI and CLI. |
| `packaging/linux/rhetoric.spec` | PyInstaller data and dependency metadata collection. |
| `scripts/build_offline_linux_kit.py` | Offline kit assembly and uninstall behavior. |
| `scripts/patch_audio_cpp_ggml.sh` | Applies the tracked native ggml/audio.cpp build patches. |
| `scripts/patch_surface_manifest.json` | GUI patch-surface/census metadata. |
| `scripts/patches/ggml_shader_compile_robustness.patch` | Native Vulkan shader-generator compile patch. |
| `src/rhetoric/audio/recorder.py` | Runtime capture-backend initialization used by the packaged app. |
| `src/rhetoric/third_party.py` | Generates bundled component and stock-voice ownership notices. |
| `src/rhetoric/EULA.md` | Packaged EULA copy. |

The frozen build also consumes the unmodified Python package, project
dependencies, license texts, and other files listed by the packaging
configuration. They are already tracked and are not changed by this commit.

### Release and QA source

| Path | Role |
|---|---|
| `scripts/airgap_proof.py` | Windows guest air-gap proof orchestration. |
| `scripts/airgap_proof_windows.ps1` | Windows guest-side proof script and volume-label default. |
| `scripts/certify_gui.py` | Offscreen GUI/theme certification harness. |
| `scripts/crash_hunt.py` | Renderer crash-reproduction command. |

### Test source

| Path | Role |
|---|---|
| `tests/conftest.py` | Hermetic test-module inventory. |
| `tests/helpers.py` | Source-tree snapshots and worker-import analysis helpers. |
| `tests/test_airgap_proof.py` | Air-gap proof argument/layout regression coverage. |
| `tests/test_app_gui_profiles.py` | GUI profile setup isolation. |
| `tests/test_certifier_hermeticity.py` | Certification side-effect boundary. |
| `tests/test_crash_handlers.py` | Crash-handler process-global cleanup. |
| `tests/test_doctor_read_only.py` | Doctor output and filesystem side-effect contract. |
| `tests/test_gui_theme_certification.py` | GUI certification snapshot scope. |
| `tests/test_offline_linux_kit.py` | Offline installer/uninstaller ownership checks. |
| `tests/test_patch_audio_cpp_shader_generator.py` | Native patch generation/retry-window output. |
| `tests/test_powershell_wrapper.py` | PowerShell availability and wrapper behavior. |
| `tests/test_recording_studio.py` | Recording UI behavior without host audio devices. |
| `tests/test_theme_switch_certification.py` | Theme-certification filesystem scope. |
| `tests/test_worker_import_sweep.py` | Worker-thread import constraints. |
| `tests/test_gui_imports_without_audio.py` | GUI import without loading a host audio backend. |
| `tests/test_linux_frozen_dependency_metadata.py` | Frozen-build dependency metadata coverage. |
| `tests/test_linux_frozen_entrypoint.py` | Frozen Linux CLI/GUI entrypoint dispatch. |
| `tests/test_repo_tree_snapshot.py` | Repository-tree snapshot helper behavior. |

### Ownership, scope, and release documentation

| Path | Role |
|---|---|
| `AGENTS.md` | Persistent repository handling instructions for future work. |
| `docs/PROJECT_AUTHORITY.md` | Canonical owner-provided content and rights statement. |
| `docs/release/WORKTREE_COMMIT_SCOPE_2026-11-17.md` | This exact commit-scope manifest. |
| `README.md` | Links users and contributors to project content scope. |
| `EULA.md` | Shipped/root EULA ownership statement. |
| `Seashells/ASSETS.md` | Stock voice asset inventory and per-file terms. |
| `THIRD_PARTY_NOTICES.md` | Regenerated notices with the Developer ownership statement and retained file-level terms. |
| `Input/README.md` | Input content scope. |
| `docs/HISTORY_SCRUB_RELEASE.md` | Corrected owner scope; separates it from history rewriting. |
| `docs/release/PHASE0_BASELINE_1.5.0_RC.md` | Erratum for the earlier "user-excluded" characterization. |
| `docs/release/PHASE5_HISTORY_AUDIT.md` | Clarifies the prior preservation note. |
| `docs/release/archive/PHASE5_HISTORY_AUDIT_PRE_MIGRATION.md` | Historical scope clarification. |
| `docs/release/OFFLINE_QUALIFICATION_2026-11-14.md` | Clarifies that the prior asset exclusion was an implementation choice. |
| `release_artifacts/linux-frozen-33618789/qualification-2026-11-16/RELEASE_QUALIFICATION_REPORT.md` | Adds the dated Developer ownership-scope correction to the latest identified Linux qualification record. |

`THIRD_PARTY_NOTICES.md` is regenerated from `src/rhetoric/third_party.py`;
the generated notice adds the Developer ownership assertion and preserves the
file-level license and attribution rows.

## Excluded working-tree paths

These paths remain untouched and unstaged by this source commit:

- Eight tracked deletions under `Input/`: `READ_THIS_TO_RECORD_SEASHELLS.txt`,
  `Read Aloud transcript.txt`, `What is, reality.txt`, `cli_short.txt`,
  `local_audio_test.txt`, `recording prompt.txt`,
  `stream_of_consciousness_dialogue_with_typos.txt`, and `test.txt`. Because
  their deletions are not committed, the remote branch retains its existing
  copies.
- `Input/Recording_Studio_Generic_Teleprompter_File.txt`: untracked input
  content; it is not a compiler input for the latest frozen build.
- `release_artifacts/`: 35,700 untracked paths were present at inventory time;
  this includes the latest qualification report above, while 35,699 other
  binaries, installers, logs, model files, checksums, manifests, and the older
  `linux-v100a-review/RELEASE_QUALIFICATION_REPORT.md` are excluded. Path-size summation was 121.4 GiB, including duplicate payloads
  across artifact directories; 101 paths exceeded 100 MiB.
- `squashfs-root/`: 5,843 untracked extracted-bundle paths, excluded as build
  output.

The four untracked test files listed above are included as test source. The
remaining changes outside these categories are included only if listed in the
included-path tables. No generated model checkpoint, GGUF, installer binary,
AppImage runtime, or extracted application library is staged.

## Verification boundary

This manifest is a path-and-purpose record, not a test report. No tests or
fresh build are claimed by this document. Before commit, verify the staged path
set against these tables, run whitespace and secret checks over that bounded
set, and confirm that no generated artifact or excluded `Input/` deletion is
staged. Push only this commit to `origin/release/1.5.0-final`; do not force-push,
tag, or publish a release.
