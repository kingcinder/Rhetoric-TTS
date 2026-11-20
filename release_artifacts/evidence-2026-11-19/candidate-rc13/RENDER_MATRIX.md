# RC13 two- and three-speaker CPU/Vulkan renders

All four outputs were synthesized through the RC13 installed frozen GUI RenderWorker, using an offline Ubuntu 24.04 amd64 qualification container. `ffmpeg` fully decoded every FLAC; each is mono, 24 kHz, signed 16-bit FLAC. CPU/Vulkan parity checks passed for corresponding input text, order, speaker labels, and voice reference hashes. Human listening has not been performed.

| Case | Backend | Output | Duration | SHA-256 | Device |
|---|---|---|---:|---|---|
| 2speaker | cpu | [rc13-2speaker-cpu-7341.flac](/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric/release_artifacts/evidence-2026-11-19/candidate-rc13/2speaker/cpu/rc13-2speaker-cpu-7341.flac) | 13.10s | `8b68e6c61c4953a4b791f58f1245676a0524a6efaa4cb739f08ce8423b1011cb` | CPU / system DRAM |
| 2speaker | vulkan | [rc13-2speaker-vulkan-7342.flac](/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric/release_artifacts/evidence-2026-11-19/candidate-rc13/2speaker/vulkan/rc13-2speaker-vulkan-7342.flac) | 10.10s | `232eaa3ee5e4ae7520e6445f1fb3f67e0689fffabc10394a4d430342461aabd5` | AMD Radeon RX 5700 XT (RADV NAVI10) |
| 3speaker | cpu | [rc13-3speaker-cpu-7441.flac](/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric/release_artifacts/evidence-2026-11-19/candidate-rc13/3speaker/cpu/rc13-3speaker-cpu-7441.flac) | 21.22s | `dec9f0877e31aee0b7425d36c34ab47c946bb66f7150d36ea7a83cdbfd830f8f` | CPU / system DRAM |
| 3speaker | vulkan | [rc13-3speaker-vulkan-7442.flac](/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric/release_artifacts/evidence-2026-11-19/candidate-rc13/3speaker/vulkan/rc13-3speaker-vulkan-7442.flac) | 16.14s | `627e872b20910c93146757001c292360c13159da12ffeff8a47aef072652c6e6` | AMD Radeon RX 5700 XT (RADV NAVI10) |

Casting map: A = Cody1; B = Fransisco Monster Edited; C = Christopher2. The 2-speaker case uses A/B. The 3-speaker case uses A/B/C.

Parity evidence: `cpu-vulkan-parity.json`. Per-file records, exact selected turns, input hashes, voice paths/hashes, FLAC metadata, and decode result are in each backend directory as `render-record.json`.


## Fresh post-microphone dialogue rerenders

After the Recording Studio microphone fix was verified, all four requested dialogue renders were regenerated through the installed RC13 GUI RenderWorker using separate empty render caches. The exact FLACs, hashes, per-backend logs, and CPU/Vulkan parity evidence are in [`rerun-microphone-20261119/RENDER_MATRIX.md`](rerun-microphone-20261119/RENDER_MATRIX.md). The earlier render set above is preserved as prior evidence.
