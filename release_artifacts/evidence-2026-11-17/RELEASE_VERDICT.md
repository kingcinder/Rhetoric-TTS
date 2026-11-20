# Release verdict — Rhetoric V1.00a Ubuntu 24.04 amd64 RC1

Instruction precedence followed: the user clarified that the Autonomous Execution Directive controls over conflicting earlier prompts and documents.

## VERDICT

**NOT AUTHORIZED FOR DISTRIBUTION.** The candidate is internally installable in a fresh Ubuntu 24.04 container without network access, but mandatory activation, interactive GUI, CPU/Vulkan production renders, human listening, complete data-retention, advisory-security, and signing gates remain open.

## ARTIFACT

- Downloadable candidate: `release_artifacts/linux-rc-32ac9df/Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc1.tar.zst`
- Size: 4,742,706,176 bytes
- SHA-256: `00e0caa5a15af0757e56e69a5baf5d19044ab13b5a0d18cb7f729d04294f4b28` (sidecar and `zstd -t` both verified)
- Debian package inside kit: 389,207,072 bytes; SHA-256 `51cd9f263f4d5f134c8da3ee2ab98ca39fc9e43cd2617383556916d64a994931`
- Source: `32ac9df7200e5fedf04dfd01c0edb55be642dd50`; public label V1.00a maps to engineering version 1.5.0.
- Signature: **unsigned**. No release tag, upload, or publication was made.

## SCOPE CERTIFIED

- Full source suite: 2,357 passed, 2 skipped, 6 warnings; exit 0. The skips are the Snap-confined PowerShell launch and unavailable Vulkan-device smoke.
- Release check, soft-launch (`ready`, zero blockers, one weak-copyleft warning), notices check (118 components), and `pip check` passed.
- Fresh Ubuntu 24.04 network-disabled install/uninstall smoke passed. All inner kit checksums, outer archive SHA-256, and Zstandard integrity passed.
- Current-source CycloneDX 1.5 inventory contains 635 components. Scoped Gitleaks scan found no findings in files <=5 MiB; larger binaries and model assets were excluded.

## BLOCKERS

1. No authorized offline validation serial was available; activation, invalid-token rejection, and all production renders remain untested.
2. The host advertised `DISPLAY=:0.0`, but the display server was unreachable; interactive GUI lifecycle remains unverified.
3. No exact-candidate RX 5700 XT Vulkan render, audio parity packet, or human listening verdict exists.
4. Full project/settings/recordings/license retention through reinstall and uninstall remains untested.
5. Vulnerability advisory audit is **NOT VERIFIED** because the configured advisory host did not resolve through DNS. The file-derived SBOM is inventory evidence, not a clean vulnerability result.
6. No owner-approved signing identity or distribution authorization is available.

## DEFERRED

- Additional Ubuntu releases, GPUs and compatibility expansion; mandatory Ubuntu 24.04 acceptance is incomplete.
- Human listening and CPU/Vulkan duration/parity assessment, pending authorized renders.
- Binary/model security audit beyond the scoped text-file secret scan.

## OWNER ACTION

1. Supply/use an owner-authorized offline validation serial in a disposable Ubuntu 24.04 profile so engineering can complete GUI, activation, CPU and RX 5700 XT Vulkan acceptance.
2. Listen to and attest the paired monologue, two-speaker and five-speaker CPU/Vulkan outputs for intelligibility, attribution, pacing, artifacts and parity.
3. Provide an owner-approved Linux release signing identity and explicitly authorize distribution only after all required gates pass.

## MATERIAL INCIDENT

An initial PyInstaller `--clean` invocation removed `/home/cody/.cache/pyinstaller`. Its prior contents were not backed up and could not be restored in this session. The final build used an isolated PyInstaller cache under `/tmp`; no application installation or user project data was changed.
