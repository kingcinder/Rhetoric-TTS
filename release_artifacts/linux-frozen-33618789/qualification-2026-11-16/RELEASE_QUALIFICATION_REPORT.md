# Rhetoric 1.5.0 / V1.00a qualification checkpoint

**Recorded:** 2026-11-16 (America/Los_Angeles)
**Source head:** `33618789b7d2eebc994fdd5c127ec8866d6ede5b`
**Release designation:** V1.00a is not approved or frozen. These artifacts remain internal 1.5.0 engineering candidates.

## Result

The Linux Ubuntu 24.04 amd64 offline path installed, launched, rendered all six CPU/Vulkan scenario combinations, and uninstalled in a network-disabled Ubuntu container. This verifies one host configuration only: AMD Ryzen 7 3700X plus AMD Radeon RX 5700 XT (RADV/NAVI10), with the host's AMDGPU kernel module, firmware, and `/dev/dri` access already available.

The commercial release gate is **not passed**. Artifacts are unsigned, Windows CPU rendering was not requalified against this source head, and broader Linux/GPU coverage plus subjective audio review remain outstanding.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---:|---|
| `rhetoric-1.5.0-x86_64.AppImage` | 473,348,600 B | `6ead218d2c1f8183a90b411bdb061587370a9efda1bc789bea7aa5eca5199189` |
| `rhetoric_1.5.0_amd64.deb` | 389,211,010 B | `8defabaf4244be651e97e97826f3dfb45216fce48bcfbfe01a10333ea2fe6337` |
| `rhetoric-1.5.0-ubuntu24.04-amd64-offline.tar.gz` | 4,846,451,117 B | `d39c6475cdeb803bbe19aa2e0cbc1500eb92b17f520ccc0460b50d3ed4d9f0c6` |

`checksums-1.5.0.sha256` verified the AppImage, deb, offline archive, and SBOM. The AppImage CLI returned `rhetoric 1.5.0`. Build output declares the artifacts unsigned; the offline tar contains the CPU checkpoint, Vulkan GGUF, audio.cpp CLI, declared Ubuntu runtime packages, and Mesa RADV userspace package.

Model pins: CPU `ResembleAI/chatterbox@5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18`; Vulkan `audio-cpp/audio.cpp-gguf@ae77d06579f5ed1be99dd7614d99929e76a46d9e`. The Vulkan CLI was built from audio.cpp commit `748c5e28f6a7228b8f38ad7142ca97d29584544b`.

## Linux offline acceptance

- Two fresh Ubuntu 24.04 containers used `--network none`; archive checksums passed and the deb/runtime packages installed without external package downloads.
- The final packaged CLI reported version 1.5.0, and offline activation succeeded with the local validated license. No license serial or token is included in this report or release artifacts.
- The bundled audio.cpp enumerated `AMD Radeon RX 5700 XT (RADV NAVI10)` and `AMD Ryzen 7 3700X`.
- The final GUI process remained alive for a 20-second `QT_QPA_PLATFORM=offscreen` probe. This was headless startup evidence, not an interactive desktop-session test. Qt logged that PipeWire was unavailable in the container.
- The updated uninstaller was exercised after a fresh offline install and activation. It removed the launcher, package, app tree, activation file, Vulkan model, and kit-owned audio.cpp CLI. It intentionally retains the per-user CPU model cache and shared Ubuntu runtime packages.

## Render results

All six FLACs were fully read by `soundfile`: 24 kHz, mono, finite samples, and nonzero RMS. Durations were within the requested 30-second to 5-minute range.

| Scenario | CPU duration / wall time | Vulkan duration / wall time | CPU / Vulkan RMS | Samples ≥ 0.999 (CPU / Vulkan) |
|---|---:|---:|---:|---:|
| Monologue | 35.50 s / 463.40 s | 34.74 s / 38.58 s | 0.112386 / 0.108741 | 62 / 0 |
| Two-speaker, four-turn dialogue | 58.77 s / 482.06 s | 60.33 s / 52.85 s | 0.110675 / 0.110116 | 55 / 0 |
| Five-speaker, two-round dialogue | 128.68 s / 999.77 s | 126.96 s / 101.26 s | 0.118637 / 0.110234 | 334 / 0 |

CPU/Vulkan duration differences were 0.76–1.72 seconds (1.35–2.66%). RMS differed by 0.51–7.08%. The CPU files contain a small number of near-full-scale samples; Vulkan files did not. A `librosa.yin` midpoint sample estimated median F0 between 101.6 and 130.7 Hz across the six files. These metrics show valid, broadly comparable outputs; they do not establish perceptual smoothness, natural tone, or human-reviewed speaker parity. The fixture audio references were synthetic eSpeak clips.

The render logs record an unavailable optional punctuation-model cache and fallback while `HF_HUB_OFFLINE=1`; synthesis continued without network access. Rendering used correction mode `off`. This is non-fatal, but means punctuation-model behavior was not qualified as an offline feature.

## Verification and release blockers

- Focused release/offline/Vulkan suite: **73 passed, 1 device-only smoke deselected**.
- `scripts/release.py --check`: internal 1.5.0 version invariant holds. It also reports the tracked changelog section's existing 2026-11-12 date as the documented post-cut state.
- Full pytest run did not complete: collection blocked inside `sounddevice._initialize` / PortAudio while importing GUI recording tests. The process was interrupted after stack inspection; no full-suite pass is claimed.
- Coverage is limited to Ubuntu 24.04 amd64 and one AMD GPU. Other Ubuntu releases, distributions, AMD GPU generations, and GPU drivers are unverified. Kernel module, firmware, kernel compatibility, and `/dev/dri` access are host-provided requirements.
- Windows remains **experimental-unconfirmed**. The prior Windows guest acceptance is from source head `17fdab9`; Python/GUI/pipeline files changed after that point, so it cannot qualify this build. No Windows CPU render was run against `3361878`.
- No product-trusted installer signing key was available in the release environment. The activation signing material is not an installer-signing identity. The generated artifacts are unsigned and must not be represented as commercially signed or V1.00a-ready.

## Evidence files

Logs, fixtures, and outputs are under `qualification-2026-11-16/`. All six FLACs are under `output/final4/{cpu,vulkan}/`; clean-install, GUI, checksum, and uninstall logs are beside this report.

## Developer ownership scope clarification (2026-11-17)

The Developer is the sole owner of all stock voice files included with
Rhetoric, including the files inventoried in `Seashells/ASSETS.md`, except
material already covered by applicable fair-use statutes. `Input/` and
`Seashells/` are not protected or categorically excluded from project work.
No additional waiver, proof, or rights documentation is required. See
[`docs/PROJECT_AUTHORITY.md`](../../../docs/PROJECT_AUTHORITY.md) and
[`AGENTS.md`](../../../AGENTS.md) for the continuing project instruction.
