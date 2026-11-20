# Offline Vulkan Installer Qualification — 2026-11-15

## Verdict

**Partial pass; not release-ready as V1.00a.** The Ubuntu 24.04 amd64 offline kit installs and uninstalls in a fresh network-disabled container. It installs the frozen GUI app, both model payloads, `audiocpp_cli`, Vulkan loader, and Ubuntu Mesa RADV userspace package. The installed GUI remained alive in an offscreen startup check, and audio.cpp found and rendered on the host RX 5700 XT.

The app's own licensed PyTorch CPU render did not produce output: the no-serial test environment left the command without a completed render. I did not bypass the serial gate. The six FLACs below were assembled from the installed audio.cpp engine's WAV outputs and encoded with the host `soundfile` library; they are engine-level evidence, not proof of Rhetoric's licensed project assembly/export path. Subjective listening review was not performed. Therefore the full requested CPU/GPU application acceptance matrix is incomplete.

The verified scope is one amd64 Ubuntu 24.04.5 LTS environment and one AMD Radeon RX 5700 XT. This does not establish support for every Linux distribution, every AMD GPU, or Windows. A system kernel, AMDGPU kernel module, firmware, and `/dev/dri` access remain host prerequisites. The container test used the host kernel while installing the Ubuntu userspace Vulkan packages from the kit.

## Installer Artifacts

Built from Rhetoric source head `35185ca1d63a0b83cbb0141415341cb1872d829d` on Ubuntu 24.04.5 amd64, kernel `6.8.0-138-generic`.

| Artifact | Size | SHA-256 |
|---|---:|---|
| `rhetoric-1.5.0-ubuntu24.04-amd64-offline.tar.gz` | 4,809,922,934 bytes | `729ea2ce12496e208fcd5488630a44a532ceb14420e905519bdd7df7f71115fe` |
| `rhetoric_1.5.0_amd64.deb` | 352,693,812 bytes | `8c6c59188e07d7dfdf303be629675582785180f637c0cc88a9c1916955058fd5` |
| `rhetoric-1.5.0-x86_64.AppImage` | 436,529,656 bytes | `20b0e11e71b0db271a90922fa4bb94516ff894eec5b28690e5b2ab9e5555d657` |

Kit contents include the pinned CPU Chatterbox snapshot, `chatterbox-q8_0.gguf`, audio.cpp Apache-2.0 CLI binary, ggml and sentencepiece license texts, `libvulkan1`, Mesa RADV (`mesa-vulkan-drivers` 25.2.8-0ubuntu0.24.04.4), and the required staged Ubuntu runtime `.deb`s. The native binary is pinned to audio.cpp source commit `748c5e28f6a7228b8f38ad7142ca97d29584544b` and has SHA-256 `e1d566edaf605a25b4db2508945f972a0bb711ee129f24a7a0a48f10de507054`.

The offline kit and outer release checksums were verified. `install.sh` checked every kit file before installing. The final archive was fully extracted and installed in the clean environment, validating the gzip/tar contents; its checksum matches the generated `update-manifest.json`.

## Clean Offline Install and Lifecycle

- Fresh local `ubuntu:24.04` container, no network (`--network=none`), no Python or build tool installed in the image; only host RX 5700 XT device nodes were mapped in for the Vulkan leg.
- `sudo` was unnecessary in the container because the test ran as root. `./install.sh` installed the runtime `.deb`s and Rhetoric package and seeded the root Hugging Face CPU cache from the kit.
- Frozen GUI startup with `QT_QPA_PLATFORM=offscreen` remained alive until the 15-second timeout (`124`, expected for a still-open GUI). The check verifies startup only; no visible desktop session was available.
- `audiocpp_cli --list-devices` enumerated `AMD Radeon RX 5700 XT (RADV NAVI10)` using RADV.
- `./uninstall.sh` removed the Rhetoric package, kit-owned CLI, and GGUF. Post-checks confirmed the app was absent, the per-user CPU model cache remained, and shared Mesa/Vulkan runtime packages remained installed.

## Audio Engine Results

Eight same-text, same-reference, same-seed requests were run from the installed `audiocpp_cli` with the bundled GGUF in CPU and Vulkan modes. The scenarios contained one monologue utterance, two alternating speakers, and five round-robin speakers. Vulkan used device 0, the RX 5700 XT. Each scenario was assembled into mono FLAC at 24 kHz with 300 ms inter-turn silence.

| Scenario | CPU duration | Vulkan duration | CPU / Vulkan RMS | CPU / Vulkan median F0 |
|---|---:|---:|---:|---:|
| Monologue | 3.66 s | 3.50 s | 0.149750 / 0.176179 | 138.7 / 132.6 Hz |
| Two-party | 4.22 s | 3.86 s | 0.139082 / 0.127920 | 126.3 / 123.7 Hz |
| Five-party | 7.58 s | 7.10 s | 0.119817 / 0.120512 | 125.3 / 139.5 Hz |

The six matching FLACs were regenerated from the final archive installation's WAV outputs and decoded successfully with FFmpeg. Each is mono/24 kHz, finite and non-silent; measured clipped-sample fraction was zero and DC offset stayed between -0.000473 and -0.000162. Median pitch estimates were within 123.7–139.5 Hz across the six files. Durations differed by 0.16 s (monologue), 0.36 s (two-party), and 0.48 s (five-party); parity is measured, not waveform identity. Metrics do not establish naturalness, pronunciation, smoothness, or perceived voice match without listening review.

FLAC files and machine-generated integrity metrics are under [`release_artifacts/linux-frozen-35185ca/qualification-2026-11-15/flac/`](../../release_artifacts/linux-frozen-35185ca/qualification-2026-11-15/flac/). Install, GUI, Vulkan, render, and uninstall logs are under [`release_artifacts/linux-frozen-35185ca/qualification-2026-11-15/evidence/`](../../release_artifacts/linux-frozen-35185ca/qualification-2026-11-15/evidence/).

## Remaining Release Gates

- Rhetoric's licensed PyTorch CPU app-render and its app-level FLAC export were not completed. No serial was installed or generated, and no licensing bypass was used.
- The AppImage and `.deb` rebuilt successfully, but the build command exited at CycloneDX SBOM regeneration because its `pip-audit` step could not resolve PyPI with network access restricted. The existing SBOM was retained; it was not refreshed during this build.
- Only synthetic eSpeak references and brief test dialogue were used. Human listening review remains outstanding.
- No production signing certificate or authorized signing step was available. No production signing key was inspected or changed. The installer remains unsigned and must not be designated or frozen as official V1.00a.
- Support beyond the tested Ubuntu 24.04 amd64/RX 5700 XT combination is unverified. The bundle cannot universally provide the host kernel driver, GPU firmware, or device permissions.
- Packaging checks passed: 7 offline-kit tests, 1 installed-CLI discovery test, and Python syntax checks. The complete application render matrix remains open as described above.
