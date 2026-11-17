# Rhetoric V1.00a Ubuntu 24.04 Release Checklist

**Controlling directive:** `/home/cody/.codex/attachments/b2847168-41ca-4d81-ae6f-bbca025d503c/Pasted text.txt` (Autonomous Execution Directive). Per the user's 2026-11-17 clarification, it supersedes conflicting requirements in earlier prompts and documents.
**Earlier execution contract:** `/home/cody/Downloads/Rhetoric_Codex_Prompt_01_Ubuntu24_Airgap_V1.00a_Release.md` (Execution Contract 01 of 03), applied where consistent with the controlling directive.
**Goal:** Complete and qualify the smallest commercially viable, fully air-gapped Rhetoric V1.00a Ubuntu 24.04 x86-64 release, preserving the existing application, development history, and owner decisions. Prepare the highest-qualified immutable candidate possible; do not sign or publish without authority.

Statuses are `PENDING`, `ACTIVE`, `PASS`, `FAIL`, or `BLOCKED`. A `PASS` requires the stated acceptance evidence. Preserve original evidence when a later change requires a gate to be reopened.

## Phase A — Reconnaissance and gate contract

| ID | Objective | Acceptance criterion | Required evidence | Depends on | Status |
|---|---|---|---|---|---|
| A1 | Capture deadline, repo root, branch, HEAD, upstream/history, submodules, working tree and preserve pre-existing changes. | Timestamped snapshot records all fields and no pre-existing path is overwritten or discarded. | `release_artifacts/evidence-2026-11-17/host-and-repository-inventory.txt`; `tracked-files.txt`; `untracked-files.txt` | — | PASS |
| A2 | Map the project files and classify source, docs, tests, Input, Seashells, release packages, models and generated evidence. | Complete current path map and tracked/untracked inventories exist; Input and Seashells remain in scope. | `current-project-file-map.txt`; `tracked-files.txt`; `untracked-files.txt`; repository `AGENTS.md` | A1 | PASS |
| A3 | Locate dated qualification reports and compare their revision, dirty-state and artifact claims with this checkout. | Report location and source/artifact mismatch are recorded without carrying historical PASS claims forward. | `release_artifacts/linux-frozen-33618789/qualification-2026-11-16/RELEASE_QUALIFICATION_REPORT.md`; `release_artifacts/linux-v100a-review/RELEASE_QUALIFICATION_REPORT.md`; `git diff 33618789..HEAD` captured in execution log | A1 | PASS |
| A4 | Record host OS/hardware/storage, graphics access, build tools, Docker/VM support, installed Rhetoric and user-data locations. | Read-only environment inventory has exact results and no host driver/application/user-data changes. | `host-and-repository-inventory.txt`; canonical gate logs; installed package and user path inventory | A1 | PASS |
| A5 | Inventory and verify candidate `.deb`, offline kit, model, audio.cpp, EULA/license, notices, manifests and hashes. | Candidate payload paths, sizes, pinned revisions and independently checked SHA-256 results are recorded. | `release_artifacts/linux-rc-32ac9df/`; `release_artifacts/evidence-2026-11-17/kit-checksums-32ac9df.log`; `release_artifacts/evidence-2026-11-17/ARTIFACT_BINDING_CHECKS.json` | A2, A3 | PASS |
| A6 | Run canonical release, soft-launch, packaging and notices checks against exact source and retain return codes. | Each command, start/finish, exit code and full output is stored and accurately interpreted. | `release_artifacts/evidence-2026-11-17/canonical-gates-32ac9df/` | A1 | PASS |
| A7 | Create machine-readable and human-readable G01–G12 gate ledgers. | Every gate has required/optional, environment, exact criterion, evidence, status, source SHA, artifact SHA and reviewer fields. | `release_gate_matrix.json`; `RELEASE_GATE_MATRIX.md` | A3, A6 | PASS |
| A8 | Review current owner decisions, changelog, relevant source history, release readiness, audio acceptance and LGPL fulfillment. | Relevant project decisions are carried forward; unknown historical intent is not changed. | `docs/PROJECT_AUTHORITY.md`; `docs/release/WORKTREE_COMMIT_SCOPE_2026-11-17.md`; release decision docs; current git history | A2, A3 | PASS |
| A9 | Set a bounded dependency-ordered closure path and note owner-only actions once. | Next actions address mandatory gates first; publication/signing/listening are not falsely authorized. | This checklist; `RELEASE_EXECUTION_LOG.md`; gate matrix | A7, A8 | PASS |

## Phase B — Confirmed blockers only

| ID | Objective | Acceptance criterion | Required evidence | Depends on | Status |
|---|---|---|---|---|---|
| B1 | Reproduce and classify current P0/P1 blockers; preserve working CPU/Vulkan paths and RDNA1 mitigation. | Each blocker is linked to a current source/artifact check; no optional compatibility work is mixed into the core path. | canonical gate logs; focused diagnostics; relevant tests and source review | A6, A7 | PASS |
| B2 | Apply minimal fixes only where the defect is reproduced and the fix preserves owner intent. | Focused regression evidence passes; existing behavior and before/after source are retained. | small diff; targeted verification logs; updated gate statuses | B1 | PASS |

## Phase C — Freeze source and build one final candidate

| ID | Objective | Acceptance criterion | Required evidence | Depends on | Status |
|---|---|---|---|---|---|
| C1 | Preserve pre-existing dirty state and identify a clean committed release source. | Source is committed, clean, traceable and derived from existing work; user data and old evidence remain intact. | before-state backup/snapshot; commit SHA; clean `git status` | A1, B2 | PASS |
| C2 | Record exact Python/dependency/model/audio.cpp/toolchain/native-runtime inputs and hashes. | Build inputs are pinned and linked to the exact source and candidate. | `release_artifacts/evidence-2026-11-17/SOURCE_AND_ARTIFACT_PROVENANCE.json`; current input hashes; `current-source-build-32ac9df.log`; `package-assembly-32ac9df.log` | C1 | PASS |
| C3 | Run canonical version/soft-launch checks, relevant tests and the full relevant suite at the freeze boundary. | Results name exact source SHA, full pass/fail/skip/warning counts and reasons. | `release_artifacts/evidence-2026-11-17/FULL_TEST_REPORT.md`; `full-suite-32ac9df.log`; canonical-gates-32ac9df | C1, C2 | PASS |
| C4 | Build one immutable RC and single-file offline installation kit from frozen source. | Kit contains app, pinned models/runtime assets, instructions, integrity records, install/uninstall paths and coherent version identity. | `release_artifacts/linux-rc-32ac9df/Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc1.tar.zst`; manifests; SHA-256 | C1, C2, C3 | PASS |
| C5 | Generate current-build SBOM, license inventory, checksum records, provenance and secret/content scan. | Inventories match the actual frozen package; stale SBOMs are explicitly excluded; no prohibited material is included. | `release_artifacts/linux-rc-32ac9df/sbom.json`; shipped notices; `security/SECRET_SCAN_STATUS.md`; provenance and checksums | C4 | PASS |

## Phase D — Exact-byte acceptance

| ID | Objective | Acceptance criterion | Required evidence | Depends on | Status |
|---|---|---|---|---|---|
| D1 | Install the exact candidate in fresh Ubuntu 24.04 with network disabled before installation. | Checksummed kit installs and completes offline workflow without external requests or unseeded caches. | `release_artifacts/evidence-2026-11-17/AIRGAP_INSTALL_PROOF.md`; `airgap-install-uninstall-32ac9df.log`; checksum log | C4, C5 | PASS |
| D2 | Verify actual interactive GUI and first-user lifecycle. | Real display-backed installed GUI handles themes, controls, EULA/activation, projects/settings, render and backend selection. | `release_artifacts/evidence-2026-11-17/COMPATIBILITY_MATRIX.md`; host display diagnostics; exact artifact hash | D1 | BLOCKED |
| D3 | Produce installed CPU monologue, two-speaker and five-speaker FLACs. | Current `Input/` text selection is recorded per render; installed CPU backend and no-cache synthesis are proven; FLAC output and hashes validated. | `release_artifacts/evidence-2026-11-17/RENDER_ACCEPTANCE.md`; `current-input-inventory.txt`; no render outputs because no authorized serial | D1, D2 | BLOCKED |
| D4 | Produce the same installed RX 5700 XT Vulkan cases. | Actual RX 5700 XT/RADV device and audio.cpp/GGUF Vulkan backend are evidenced; input paths and validated FLAC hashes are recorded. | `RENDER_ACCEPTANCE.md`; Vulkan enumeration/activity; logs; output hashes/statistics | D1, D2, D3 | BLOCKED |
| D5 | Prepare paired audio packet and human review sheet. | Mandatory cases are paired to current input text and references; authorized human verdict is recorded without agent impersonation. | `release_artifacts/evidence-2026-11-17/LISTENING_REVIEW.md`; packet deferred until renders exist | D3, D4 | BLOCKED |
| D6 | Verify install/reinstall/uninstall and personal-data retention. | Filesystem/package comparison proves only package-owned files removed and promised user data retained. | `airgap-install-uninstall-32ac9df.log`; package/app removal and CPU cache retention; personal data lifecycle remains unverified | D1, D2 | BLOCKED |
| D7 | Verify offline activation, notices/privacy/support and exact shipped LGPL fulfillment. | Authorized test key works offline, invalid/tampered serial rejects, and shipped legal/fulfillment materials match actual payload. | activation log without serial/token; EULA/notices inventory; LGPL replacement evidence | D1, C5 | BLOCKED |

## Phase E — Optional same-day compatibility expansion

| ID | Objective | Acceptance criterion | Required evidence | Depends on | Status |
|---|---|---|---|---|---|
| E1 | Consider one low-risk expansion only after all mandatory Ubuntu 24.04 gates pass. | No mandatory gate is open and sufficient time remains for final integrity/signing checks; otherwise defer. | matrix state and time record | D1–D7 | PENDING |

## Phase F — Provenance, final gates and handoff

| ID | Objective | Acceptance criterion | Required evidence | Depends on | Status |
|---|---|---|---|---|---|
| F1 | Sign with an existing owner-approved release identity and independently verify, if available. | Final kit/checksum signature verifies against an approved identity; otherwise kit remains unsigned and signing is marked BLOCKED. | `release_artifacts/evidence-2026-11-17/RELEASE_VERDICT.md`; unsigned owner-signer blocker | C5, D1–D7 | BLOCKED |
| F2 | Re-run final source and artifact-dependent gates on immutable candidate bytes. | Every G01–G12 row has an evidence-backed PASS/FAIL/BLOCKED/NOT_RUN state with exact source/artifact identity. | `release_artifacts/evidence-2026-11-17/RELEASE_GATE_MATRIX.md`; `release_gate_matrix.json`; exact hashes; full test report | C3–F1 | PASS |
| F3 | Deliver required release evidence and an unambiguous verdict. | Provenance, air-gap proof, render report, listening sheet, compatibility matrix, fresh SBOM/security state and verdict exist. | `RELEASE_EXECUTION_LOG.md`; `SOURCE_AND_ARTIFACT_PROVENANCE.json`; `AIRGAP_INSTALL_PROOF.md`; `RENDER_ACCEPTANCE.md`; `LISTENING_REVIEW.md`; `COMPATIBILITY_MATRIX.md`; fresh SBOM; `RELEASE_VERDICT.md` | F2 | PASS |
| F4 | Consolidate outstanding owner-only actions without further interruption. | Signing, human listening and publication actions are each precise; no unauthorized action is taken. | `release_artifacts/evidence-2026-11-17/RELEASE_VERDICT.md` | F2, F3 | PASS |

## Phase reviews

- **Phase A review:** source/repository inventory, historical comparison, exact requirements and G01–G12 ledger are complete. Correct release, soft-launch, notice and dependency checks pass under `.venv`.
- **Phase B review:** the full suite identified one generated shader patch line-ending drift; the repository generator reproduced and corrected it. No application code change was needed. Focused suites and the full final-source suite pass.
- **Phase C review:** frozen source is commit `32ac9df7200e5fedf04dfd01c0edb55be642dd50`; build, package, fresh SBOM, provenance, kit checksums, and a single-file offline archive are complete. Advisory vulnerability state remains unverified because DNS resolution failed.
- **Phase D review:** exact-candidate network-disabled install/CLI/uninstall smoke passes. Activation and interactive GUI were not available; no CPU/Vulkan production render or human listening packet exists. Full user-data/reinstall lifecycle and shipped-license acceptance remain unverified.
- **Phase E review:** no compatibility expansion was attempted while mandatory gates remain open.
- **Phase F review:** source suite and artifact integrity evidence are complete; final verdict and gate matrix record required blockers. Candidate remains unsigned and unauthorized for distribution; signing and publication were not attempted.
