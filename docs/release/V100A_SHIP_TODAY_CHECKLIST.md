# Rhetoric V1.00a ship-today checklist

Controlling objective: [V100A_SHIP_TODAY_GOAL.md](V100A_SHIP_TODAY_GOAL.md). Attached master prompt supplies execution details; this checklist tracks current evidence. Do not infer PASS from historical evidence for a different artifact. Update each row when evidence changes.

**Candidate source anchor:** `32ac9df7200e5fedf04dfd01c0edb55be642dd50` (application/package source). **Initial branch/head at checklist creation:** `V1.00a-beta_build` / `6a75f88331471499eb5c36c921f9caa4d46009d7`; current task commits are in `git log`. **Candidate:** `release_artifacts/linux-rc-32ac9df/Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc1.tar.zst`, 4,742,706,176 bytes, SHA-256 `00e0caa5a15af0757e56e69a5baf5d19044ab13b5a0d18cb7f729d04294f4b28`. Embedded `.deb`: SHA-256 `51cd9f263f4d5f134c8da3ee2ab98ca39fc9e43cd2617383556916d64a994931`. Public label V1.00a maps to engineering version 1.5.0.

States: `PENDING | ACTIVE | PASS | FAIL | BLOCKED | INVALIDATED`. A PASS is limited to its stated evidence and exact candidate identity.

| ID | Requirement and acceptance evidence | Source / artifact SHA-256 | State | Narrow next action |
|---|---|---|---|---|
| P0-01 | Preserve canonical checkout and existing dirty owner content. Evidence: `git status --short --branch`, `docs/release/EXECUTION_CHECKLIST_2026-11-17.md`. | `32ac9df7200e5fedf04dfd01c0edb55be642dd50` / `00e0caa5a15af0757e56e69a5baf5d19044ab13b5a0d18cb7f729d04294f4b28` | PASS | Keep pre-existing changes untouched; update this ledger only. |
| P0-02 | Verify exact archive and `.deb` hashes, zstd integrity, inner manifest, safe extraction/install entry point. Evidence: `release_artifacts/evidence-2026-11-17/kit-checksums-32ac9df.log`, `AIRGAP_INSTALL_PROOF.md`; current archive hash and `zstd -t` rechecked. | same / same | PASS | No rebuild unless a specific archive defect is reproduced. |
| P0-03 | Fresh Ubuntu 24.04 install with network disabled, installed CLI/version, uninstall. Evidence: `release_artifacts/evidence-2026-11-17/airgap-install-uninstall-32ac9df.log`. | same / same | PASS | No additional container route currently accessible; Docker socket permission denied. |
| P0-04 | Installed real GUI and customer first-launch lifecycle on exact bytes. Evidence: `release_artifacts/evidence-2026-11-17/COMPATIBILITY_MATRIX.md`. | same / same | BLOCKED | Reattempt only with accessible display/session; current `xdpyinfo` fails. |
| P0-05 | Authorized offline activation and invalid-token rejection. Evidence: `AIRGAP_INSTALL_PROOF.md`, `RENDER_ACCEPTANCE.md`. | same / same | BLOCKED | Owner supplies/uses authorized validation serial; do not bypass licensing. |
| P0-06 | Installed CPU and RX 5700 XT Vulkan monologue/two/five-speaker FLACs, selected from current `Input/`. Evidence: `RENDER_ACCEPTANCE.md`, `current-input-inventory.txt`. | same / same | BLOCKED | Once activation is authorized, render selected inputs and record paths, backend, output hashes. Current host has no `/dev/dri`. |
| P0-07 | Paired human listening and parity review. Evidence: `LISTENING_REVIEW.md`. | same / same | BLOCKED | After exact-candidate renders exist, provide packet for owner/authorized listener. |
| P0-08 | Project/settings/recordings/license data retention across install, upgrade, uninstall. Evidence: `AIRGAP_INSTALL_PROOF.md`. | same / same | BLOCKED | Exercise disposable user-data fixture in an offline install when GUI/activation path is available. |
| P0-09 | Compliance materials, current SBOM/security evidence, activation/privacy obligations. Evidence: `kit/README.md`, `kit/SBOM-STATUS.md`, `security/SECRET_SCAN_STATUS.md`, `RELEASE_VERDICT.md`, `docs/release/V100A_SHIP_TODAY_UPDATE_LICENSE_AUDIT.md`. | same / same | BLOCKED | Notices and scoped secret scan exist; advisory audit remains unverified (DNS failure). Candidate uses frozen `.deb` notification-only updates; AppImage self-apply is a separate unsigned-manifest path. Test-only license keys cannot activate this release build. |
| P0-10 | Current beta CI status and release-relevant red jobs. Evidence: [run 44188534582](https://github.com/kingcinder/Rhetoric-TTS/actions/runs/44188534582), `release_artifacts/evidence-2026-11-17/ci-remediation-2026-11-17.md`, `suite-counts-6ad8c68.log`, `suite-counts-c38cfb3.log`, `suite-counts-c412eb0.log`, and commits `53c53d9` / `ad79496`. | same / same | PASS | Ubuntu 3.11/3.12, clean-clone acceptance, suite-count gate, Vulkan no-skip job, compiled license core, and frozen Linux packaging passed on `ad79496`. Overall workflow remains red only for Windows 3.11/3.12 suite and Windows theme-certification jobs; those are outside the Ubuntu-only release scope. |
| P0-11 | Exact customer download, quick-start, final verdict, signature/publication authority. Evidence: candidate kit and `RELEASE_VERDICT.md`. | same / same | BLOCKED | Deliver unsigned local candidate with `ENGINEERING_RC_BLOCKED` unless every mandatory gate closes; no public release absent authorization. |
| P1 | Versioned verified upgrades, then minimal recorder/GUI seams. | source/artifact-bound after P0 | PENDING | Start only after P0 has a durable shippable candidate and no achievable P0 engineering gate remains. |
| P2 | Reversible, provenance-preserving workspace cleanup. | source/artifact-bound after P1 | PENDING | Do not begin while P0/P1 gates remain. |
| P3 | Wider Linux/GPU/USB and bare-metal Windows 11 preparation. | separate qualification | PENDING | Document next actions only after earlier phases. |

## Current environment facts

- Ubuntu 24.04.5 LTS x86-64; session advertises `DISPLAY=:0.0`, but `xdpyinfo` fails.
- `/dev/dri` is absent; host RX 5700 XT Vulkan cannot be exercised in this session.
- Docker daemon access is denied to this session.
- No Rhetoric package is installed in the current host environment.
- Exact archive SHA-256 and embedded package SHA-256 match the recorded values; `zstd -t` passes. Candidate remains unsigned and not authorized for public distribution.
