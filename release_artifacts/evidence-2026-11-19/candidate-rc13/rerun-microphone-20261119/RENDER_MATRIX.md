# Post-microphone CPU/Vulkan dialogue rerenders

These four files were regenerated after the Recording Studio microphone fix through the exact RC13 installed frozen GUI RenderWorker in the existing network-isolated Ubuntu 24.04 qualification container. Each backend/case used a fresh independent render-work directory; all four reports show zero cache hits. Every output fully decodes as mono 24 kHz signed 16-bit FLAC. CPU/Vulkan parity is exact for selected current Input path/hash, turns, speaker labels, and reference audio hashes. Human listening has not been performed.

| Case | Backend | Output | Duration | SHA-256 | Device |
|---|---|---|---:|---|---|
| 2speaker | cpu | [rc13-micfixed-2speaker-cpu-7341.flac](/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric/release_artifacts/evidence-2026-11-19/candidate-rc13/rerun-microphone-20261119/2speaker/cpu/rc13-micfixed-2speaker-cpu-7341.flac) | 13.10s | `8b68e6c61c4953a4b791f58f1245676a0524a6efaa4cb739f08ce8423b1011cb` | CPU / system DRAM |
| 2speaker | vulkan | [rc13-micfixed-2speaker-vulkan-7342.flac](/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric/release_artifacts/evidence-2026-11-19/candidate-rc13/rerun-microphone-20261119/2speaker/vulkan/rc13-micfixed-2speaker-vulkan-7342.flac) | 9.82s | `53b8fea3487aa51cc8481e18bf655fc35e254f55a7b60253b5795551e84327f4` | AMD Radeon RX 5700 XT (RADV NAVI10) |
| 3speaker | cpu | [rc13-micfixed-3speaker-cpu-7441.flac](/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric/release_artifacts/evidence-2026-11-19/candidate-rc13/rerun-microphone-20261119/3speaker/cpu/rc13-micfixed-3speaker-cpu-7441.flac) | 21.22s | `dec9f0877e31aee0b7425d36c34ab47c946bb66f7150d36ea7a83cdbfd830f8f` | CPU / system DRAM |
| 3speaker | vulkan | [rc13-micfixed-3speaker-vulkan-7442.flac](/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric/release_artifacts/evidence-2026-11-19/candidate-rc13/rerun-microphone-20261119/3speaker/vulkan/rc13-micfixed-3speaker-vulkan-7442.flac) | 16.78s | `81ddd009d3962ae6d6f529e3c20d0cf1f16be0a6298e8d60cd394294d5dc0bcd` | AMD Radeon RX 5700 XT (RADV NAVI10) |

Casting: A = Cody1; B = Fransisco Monster Edited; C = Christopher2. The 2-speaker case uses A/B. The 3-speaker case uses only A/B/C (six turns) from the current `Input/Release_Qualification_5Speaker_Test_File.txt`; no D/E turns or voices were rendered.

Input path/hash, every selected line/text, casting reference path/hash, device label, synthesis timing, output hash/size, FLAC metadata, full-decode status, cache status, and source candidate are recorded in each backend directory as `render-record.json`. CPU/Vulkan parity evidence is `cpu-vulkan-parity.json`.
