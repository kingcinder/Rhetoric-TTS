# Final release gate matrix — Rhetoric V1.00a RC1

- Source commit: `32ac9df7200e5fedf04dfd01c0edb55be642dd50`
- Debian package SHA-256: `51cd9f263f4d5f134c8da3ee2ab98ca39fc9e43cd2617383556916d64a994931`
- Single-file archive SHA-256: `00e0caa5a15af0757e56e69a5baf5d19044ab13b5a0d18cb7f729d04294f4b28`
- Signature: unsigned; distribution not authorized.

| Gate | Required | Status | Evidence / remaining blocker |
|---|---:|---|---|
| G01 | Yes | **PASS** | Clean git archive at the exact committed source was built. The working checkout remains dirty only with preserved Input/evidence changes. Evidence: `release_artifacts/evidence-2026-11-17/SOURCE_AND_ARTIFACT_PROVENANCE.json; release_artifacts/evidence-2026-11-17/FULL_TEST_REPORT.md` |
| G02 | Yes | **PASS** | One offline installation archive contains the app, pinned models, runtime packages, instructions, manifests, checksums, installer and uninstaller. Inner checksums and offline install smoke pass. Evidence: `release_artifacts/linux-rc-32ac9df/Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc1.tar.zst; release_artifacts/evidence-2026-11-17/kit-checksums-32ac9df.log` |
| G03 | Yes | **BLOCKED** | Offline checksum/install/CLI/uninstall smoke passed in Ubuntu 24.04 with network disabled. The complete activation, interactive GUI, doctor, production render and personal-data workflow was not run. Evidence: `release_artifacts/evidence-2026-11-17/AIRGAP_INSTALL_PROOF.md; airgap-install-uninstall-32ac9df.log` |
| G04 | Yes | **BLOCKED** | DISPLAY was set but the X server was unreachable from this session; no display-backed first-user lifecycle was observed. Evidence: `release_artifacts/evidence-2026-11-17/host-and-repository-inventory.txt; release_artifacts/evidence-2026-11-17/COMPATIBILITY_MATRIX.md` |
| G05 | Yes | **BLOCKED** | Current mono/two/five-speaker paths are recorded. No authorized test serial was present, so no production CPU FLAC was rendered. Evidence: `release_artifacts/evidence-2026-11-17/current-input-inventory.txt; release_artifacts/evidence-2026-11-17/RENDER_ACCEPTANCE.md` |
| G06 | Yes | **BLOCKED** | No licensed candidate Vulkan render was performed. Direct host device access was absent; Docker GPU pass-through capability alone is not a render result. Evidence: `release_artifacts/evidence-2026-11-17/host-and-repository-inventory.txt; release_artifacts/evidence-2026-11-17/RENDER_ACCEPTANCE.md` |
| G07 | Yes | **BLOCKED** | No exact-candidate paired outputs exist. Human listening and parity judgment remain open. Evidence: `release_artifacts/evidence-2026-11-17/LISTENING_REVIEW.md` |
| G08 | Yes | **BLOCKED** | Package/app removal and retained CPU model cache passed. Projects/settings/recordings/license retention and reinstall/upgrade were not verified. Evidence: `release_artifacts/evidence-2026-11-17/airgap-install-uninstall-32ac9df.log; release_artifacts/evidence-2026-11-17/AIRGAP_INSTALL_PROOF.md` |
| G09 | Yes | **BLOCKED** | Canonical soft-launch is ready with zero blockers and one weak-copyleft warning; notices pass. No authorized offline serial was available and exact shipped obligations were not fully acceptance-tested. Evidence: `release_artifacts/evidence-2026-11-17/canonical-gates-32ac9df/; docs/release/LGPL_FULFILLMENT.md` |
| G10 | Yes | **BLOCKED** | Fresh file-derived SBOM and scoped zero-finding Gitleaks scan exist. Advisory vulnerability status is NOT VERIFIED because the build environment could not resolve the advisory host; >5 MiB binary/model files were excluded from Gitleaks. Evidence: `release_artifacts/linux-rc-32ac9df/sbom.json; release_artifacts/evidence-2026-11-17/security/SECRET_SCAN_STATUS.md; release_artifacts/evidence-2026-11-17/current-source-build-32ac9df.log` |
| G11 | Yes | **BLOCKED** | No owner-approved release signing identity is available. Candidate is unsigned and not authorized for distribution; no publication/tag was made. Evidence: `release_artifacts/evidence-2026-11-17/RELEASE_VERDICT.md` |
| G12 | Yes | **BLOCKED** | Exact-source full suite passed 2357/2357 executed tests; two documented environment skips. Mandatory interactive, licensed CPU/Vulkan, human, advisory and signing gates remain open. Evidence: `release_artifacts/evidence-2026-11-17/FULL_TEST_REPORT.md; release_artifacts/evidence-2026-11-17/RELEASE_GATE_MATRIX.md` |

## Exact-candidate verification

- Clean source archive: `32ac9df7200e5fedf04dfd01c0edb55be642dd50`.
- Debian package: `51cd9f263f4d5f134c8da3ee2ab98ca39fc9e43cd2617383556916d64a994931`.
- Fresh CycloneDX 1.5 SBOM: `a9e6a4b1a8ca78c238259649e7173e3c10f2b36c45f8d7e43aebc2e52b2b2b97`; 635 components.
- Offline kit inner checksums and fresh Ubuntu 24.04 `--network none` install/uninstall smoke passed; outer archive SHA-256 verified and zstd stream integrity passed.
- Release check, soft-launch, notices, pip check and full test suite passed with the documented warnings/skips.
- No activation, render, GUI, human-review, vulnerability-free, signature, or distribution claim is made.
