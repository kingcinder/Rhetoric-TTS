# Offline qualification evidence — 2026-11-14

## Scope and result

Source checkout: `/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric`, branch
`release/1.5.0-final`, source HEAD `35185ca1d63a0b83cbb0141415341cb1872d829d`.
The Linux frozen artifacts were rebuilt from the current uncommitted working
tree, including the installed GGUF discovery change. Product version remains
`1.5.0`. Linux qualification was partial: an unsigned
single-file Ubuntu 24.04 offline installer kit installed, launched, and
uninstalled in a network-disabled base container. CPU and AMD Vulkan render
matrices passed through the source CLI with cached models and a development
test license. They were not run from the installed frozen artifact. Windows
installer qualification was unavailable.

## Artifacts

Linux frozen outputs are in `release_artifacts/linux-frozen-35185ca/`:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `rhetoric-1.5.0-x86_64.AppImage` | 436533752 | `087736253693086617b39825c2940dee0faceec6c606ee0950ce7dd7b48cdcfc` |
| `rhetoric_1.5.0_amd64.deb` | 352690706 | `2bf796de8b470423196e51eaf78503f9c08ca02720b75f48d7b4807924be2998` |
| `rhetoric-1.5.0-ubuntu24.04-amd64-offline.tar.gz` | 4747821283 | `b63c3dc11b243ed7b09bfa89f803de7a5f8840af0ca2e8987350027374c5c097` |
| `sbom.json` | 20769 | `a6b0074d23ec3d6fbb2851c31520161a1ecaad39424853271e2ce1abc8b9de00` |

The offline tar contains the `.deb`, 93 Ubuntu 24.04 amd64 dependency packages,
install/uninstall scripts, a README, checksums, the five-file pinned standard
Chatterbox CPU checkpoint, and the audio.cpp Chatterbox Q8_0 GGUF. It does not
contain the audio.cpp Vulkan executable or an AMD driver/Vulkan runtime. `sha256sum -c
checksums-1.5.0.sha256` passed. `scripts/check_update_manifest.py` verified the
AppImage, `.deb`, and offline kit against the update manifest. `pip-audit`
reported no known vulnerabilities.

The source bundle builder was configured to exclude tracked `Seashells/` paths
from its Git archive, with a regression test. This was an implementation
choice, not an owner-imposed restriction. The owner clarified on 2026-11-17
that `Seashells/` is not protected or categorically excluded; review this
builder behavior against [project authority](../PROJECT_AUTHORITY.md) before
using it for future distribution. The Debian launcher symlink was
corrected to target the frozen binary directly. The release version scanner
was narrowed to Rhetoric package artifact names so bundled runtime-library
versions do not create false release blockers; both corrections have
regression tests.

## Offline Ubuntu install and uninstall

Test environment: Ubuntu 24.04 amd64 base container, started with Docker
`--network none`; no Python, Git, or compiler was installed. The container was
given the offline kit with its runtime dependencies and models. The kit's
internal checksum check passed; `install.sh` installed the dependencies and
Rhetoric, seeded the invoking user's Hugging Face cache, and installed the GGUF
under `/opt/rhetoric/models`. `/usr/bin/rhetoric` stayed alive for a 15-second
offscreen launch. `uninstall.sh` removed the application and installer-owned
GGUF while retaining the per-user CPU model cache. Observed result:
`offline_model_install=pass gui_alive=15s app_and_system_gguf_uninstall=pass
per_user_cpu_cache=retained`. The process test proves startup/liveness, not
visual UI inspection or full interactive acceptance.

With `HF_HUB_OFFLINE=1`, `snapshot_download(..., local_files_only=True)` resolved
the staged pinned Chatterbox cache and all five required standard CPU files.
The installer build records each model file's size and SHA-256 in
`offline-ubuntu24.04-amd64/models/manifest.json`. The Vulkan model is
`chatterbox-q8_0.gguf`, 2,088,393,668 bytes, SHA-256
`d586dd1aa59613cab8046176fb7ca5ba191c02a9b10ffa5b0d892ed22b470656`.
The CPU checkpoint is `ResembleAI/chatterbox` revision
`5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18`, 3,191,966,992 bytes.

The initial bare Ubuntu test without dependencies failed as expected: the `.deb`
reported missing runtime libraries and the AppImage reported missing
`libGL.so.1`. The self-contained Ubuntu kit addresses the `.deb` runtime
dependencies for Ubuntu 24.04 amd64. Other distributions and Ubuntu releases
were not qualified.

The LGPL Qt replacement check replaced all 22 shipped `libQt6*.so.6` libraries
in a disposable AppDir copy with the matching Qt 6.8.3 set from the
`PySide6_Essentials` and `PySide6_Addons` wheels. The replaced AppRun remained
alive for 12 seconds under the offscreen platform (`timeout` exit 124), with no
error output. The original release AppDir was not modified.

## TTS rendering

Host: Ubuntu 24.04.5, AMD Ryzen 7 3700X, AMD Radeon RX 5700 XT, RADV Mesa
26.2.6. Vulkan enumerated the RX 5700 XT as device 0. The Chatterbox model and
synthetic eSpeak reference audio were already cached locally. Runs set
`HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`; the render matrix therefore
proves offline execution with a warm model cache, not a cold installation with
models supplied by the installer. It used an isolated temporary install root
and a disposable development test key, never a production key. No `Seashells/`
audio was used.

| Backend | Monologue | 2-party | 5-party round robin |
| --- | --- | --- | --- |
| CPU, Chatterbox/PyTorch | 1/1 success, no report warnings | 2/2 success, no report warnings | 5/5 success, no report warnings with standard loudness |
| AMD RX 5700 XT Vulkan, audio.cpp | 1/1 success, no report warnings | 2/2 success, no report warnings | 5/5 success, no report warnings |

An initial five-party CPU attempt with loudness disabled reported clipped
samples; rerunning with standard loudness passed. Model/library diagnostics
included synthetic-reference mel-length mismatch and a diffusers deprecation
warning. No listening review was performed. These renders used the source CLI,
not the installed frozen `.deb` or AppImage.

## Checks and remaining release gates

- Targeted release, soft-launch, frozen Linux packaging, and offline bundle
  tests: **106 passed**.
- `scripts/release.py --check`: passed; single-source version invariant holds.
- `scripts/soft_launch.py --check --json`: `ok=true`, `status=ready`, zero
  blockers, one LGPL replacement/source-obligation warning.
- Linux frozen AppImage and `.deb` are **unsigned**. No owner-controlled
  production signing certificate was provided or used.
- No Windows native build/guest was available (`iscc` and `/dev/kvm` absent;
  Wine is not Windows acceptance). The Windows CPU dependency bundle is not a
  native installer and requires preinstalled Python 3.12. No Windows install,
  render, uninstall, or signing claim is made.
- The updated offline kit includes the tested CPU model and Vulkan GGUF, but
  excludes the audio.cpp Vulkan executable and host driver/runtime. The render
  matrix was not run from the installed frozen application. Thus the combined
  criteria for launch and a `v1.00a` designation are **not met**.

## Model-inclusive installer update — 2026-11-15

The reproducible staging/build command is:

```sh
.venv/bin/python scripts/build_offline_linux_kit.py \
  --kit-dir release_artifacts/linux-frozen-35185ca/offline-ubuntu24.04-amd64 \
  --model-cache release_artifacts/offline-bundles/linux-cpu-35185ca/hf_cache \
  --vulkan-model audio.cpp/models/Chatterbox-GGUF/chatterbox-q8_0.gguf \
  --archive release_artifacts/linux-frozen-35185ca/rhetoric-1.5.0-ubuntu24.04-amd64-offline.tar.gz
```

The installer now discovers the installed GGUF through
`/opt/rhetoric/models/Chatterbox-GGUF`. The uninstall script removes that model
only when this kit installed it; it retains the user's Hugging Face CPU cache.
The kit includes a model-specific notice and MIT text with the Resemble AI
copyright line. The CPU checkpoint uses pinned revision
`5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18`; the converted GGUF is identified as
`audio-cpp/audio.cpp-gguf` revision `main` and is content-addressed in the model
manifest by SHA-256.
The kit rebuild also refreshes the release checksum and update manifests. The
final network-disabled install/start/uninstall acceptance passed after this
change.

No commit, tag, merge, push, or publication was performed. The two pre-existing
untracked `Input/` files were preserved.
