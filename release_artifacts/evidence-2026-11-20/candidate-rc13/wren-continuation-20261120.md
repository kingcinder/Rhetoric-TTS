# Wren continuation of Codex ship-today session — 2026-11-20

Codex hit its usage limit mid-rerender (2speaker CPU, evidence-2026-11-20/rerun-microphone-owner-confirmed-20261120).
Owner lifted the Rhetoric pause 2026-11-20 13:45 PST; Wren continues only the Ubuntu V1.00a release objective.

## State at start (verified live 2026-11-20 ~14:00 PST)
- HEAD 49f0678, branch V1.00a-beta_build, 94 dirty entries (unchanged from Codex session end).
- License: VALID, licensee Cody, key_id k2 (owner entered the purchased serial since the checklist was written).
- dpkg: ii rhetoric 1.5.0 amd64. Installed binary matches candidate.
- Rerun dir: only 2speaker/cpu/gui-job.json exists; no FLAC, no gui-result.json, no render-record.json.
- Disk: root 43G free (91%), Data 57G free (94%).

## Plan
1. Four rerenders (2speaker cpu/vulkan, 3speaker cpu/vulkan) via run_gui_worker_rc13.py, sequential, detached.
2. Re-verify RC13 archive+deb SHA-256 vs build-identity.json; dpkg-deb fields; gzip integrity.
3. Re-run release-path pytest suite (176-test command from release-path-tests.log).
4. Refresh security scans (pip-audit/OSV, Trivy vs exact runtime deb versions).
5. Drift check: build-identity source hashes vs working tree; files changed since RC13 build.
6. Update checklist + evidence; commit evidence/checklist updates only (never the artifact).
7. Owner-only handoff for P0-04 remainder (none — serial entered), P0-07 listening, P0-09 counsel/scope, P0-11 signing/publication.

## Progress log
- 2026-11-20 ~14:05 PST: render batch launched (4 sequential renders, log wren-rerender-batch-20261120.log).

- 2026-11-20 ~14:05 PST: render batch 1 failed fast on all four cases: PermissionError, bridge not executable (Codex wrote it 0644; 2026-11-19 bridge was 0755). Fixed with chmod 0755.
- 2026-11-20 ~14:10 PST: render batch 2 failed fast on all four cases: child ValueError, voice reference /mnt/repo-voices/... does not exist on host. Root cause: the 2026-11-20 bridge runs the child on the host, but the plan still carries the container /mnt/* paths (the 2026-11-19 bridge routed the child into the container where those paths exist). Fix: bridge now translates /mnt/repo-voices, /mnt/user-voices, /mnt/current-input to host paths before invoking /usr/bin/rhetoric.
- 2026-11-20 ~14:12 PST: a heredoc rewrite of the bridge truncated it to 644 bytes (partial write). Restored in full via stdin (3236 bytes, syntax-checked, 0755). Lesson: do not use heredocs through this shell wrapper; use the stdin field instead.
- 2026-11-20 ~14:08 PST: RC13 hashes re-verified live: archive b1fcd5e4...a97f8d (4985608078 B), deb 8883329c...fe992 (472970192 B), sbom 6b9de3cd...1311, dpkg-deb rhetoric 1.5.0 amd64, gzip integrity OK. Recorded in current-byte-verification-20261120-rerun.json.
- 2026-11-20 ~14:09 PST: release-path pytest suite re-run: 176 passed in 55.82s (same 176-test command; slower than the recorded 26.61s, CPU was shared with the render batch). Log saved as release-path-tests-20261120-wren.log.

## 2026-11-20 14:04 PST — rerender batch 3 COMPLETE, finalized

Batch 3 (run_gui_worker_rc13.py, host bridge with path translation, all four renders sequential, exit 0 each):
- 2speaker cpu 13:55:25–13:58:06 (161s), seed 7341, synth 113.82s, FLAC 301,841 B
- 2speaker vulkan 13:58:06–13:59:09 (63s), seed 7342, synth 9.34s, FLAC 298,166 B
- 3speaker cpu 13:59:09–14:02:51 (222s), seed 7441, synth 171.79s, FLAC 495,342 B
- 3speaker vulkan 14:02:51–14:03:56 (65s), seed 7442, synth 13.42s, FLAC 465,016 B
- Total batch ~8.5 min. Logs saved in the rerun dir (wren-render3-*.log, wren-rerender-batch3-20261120.log).

Finalize (finalize_evidence.py, adapted from the 2026-11-19 version for host paths / host execution): EXIT 0, all checks passed.
- 2speaker cpu: sha256 8b68e6c61c4953a4b791f58f1245676a0524a6efaa4cb739f08ce8423b1011cb, 13.10s, CPU / system DRAM, 0 cache hits
- 2speaker vulkan: sha256 c022bb66344cc8fa7bdc5809721d5ab33ac9bcf390cbcd16514d70aa1e5f36e7, 10.58s, AMD Radeon RX 5700 XT (RADV NAVI10), 0 cache hits
- 3speaker cpu: sha256 dec9f0877e31aee0b7425d36c34ab47c946bb66f7150d36ea7a83cdbfd830f8f, 21.22s, CPU / system DRAM, 0 cache hits
- 3speaker vulkan: sha256 b0c2ee0de3b505ae9d04df10ca88fb74b94b2f1fc673be4ca0be946996c8f710, 16.14s, AMD Radeon RX 5700 XT (RADV NAVI10), 0 cache hits
- Parity PASS, full decode PASS (ffprobe flac/s16/24000/mono, ffmpeg full decode on all four).
- Outputs written: render-matrix.json, cpu-vulkan-parity.json, RENDER_MATRIX.md in the rerun dir; each render-record.json updated in place.
- Determinism note: CPU outputs are BYTE-IDENTICAL to the 2026-11-19 micfixed outputs (same seeds/inputs/cast, deterministic CPU inference). Vulkan outputs differ run to run (non-deterministic backend); durations 10.58s/16.14s vs 9.82s/16.78s on 2026-11-19. The vulkan synth-time drop (9.34s/13.42s vs 120.5s/198.6s on 2026-11-19) is the host audio.cpp path running faster than the container route; cache-hit checks (0) and full decodes confirm the renders are genuine fresh renders, not cache reuse.
- Human listening: NOT PERFORMED (owner-only).

Verification file: `release_artifacts/evidence-2026-11-19/candidate-rc13/current-verification-20261120.json` — re-hashed all six 2026-11-19 outputs (unchanged, full decode PASS), verified the four new outputs (full decode PASS), recorded live license status (valid, Cody, k2), the 176-passed test re-run, and the drift check (recorder.py/test_recorder.py hashes match build-identity; no source drift).

## 2026-11-20 14:10 PST — checklist reconciled (only Wren touches it)

- P0-02: PASS, unchanged; added fresh 2026-11-20 recomputation citation.
- P0-04: BLOCKED -> PASS. Owner entered the purchased serial (license valid, Cody, k2, lic_id b0a7fe4c-8ab2-4629-8d2b-6eb06cccbc14); mic path verified; owner confirmed recording; four rerenders complete. Caveat recorded in the row: no retained GUI-recorded WAV on disk (capture was inspected and deleted per protocol); in-app dropdown/playback re-check after activation not re-run (owner confirmation covers it).
- P0-06: PASS, unchanged; added the four new micconfirmed outputs.
- P0-07: BLOCKED, unchanged (human listening not performed).
- P0-09: ACTIVE, unchanged; noted scan refresh is in flight by a parallel stream — do not treat as refreshed until those results land.
- P0-10: ACTIVE, unchanged (hosted CI unavailable); added my 176-passed 55.82s re-run and noted the parallel independent re-run.
- P0-01/03/05/08/11: unchanged.
- No commit/push per owner order (files only). Single final commit+push by parent after all parallel streams report.

## Owner-only handoff (unchanged gates, in order)

1. Human listening (P0-07) — owner or authorized listener must listen to the ten RC13 outputs (6 from 2026-11-19 + 4 new micconfirmed) and judge quality.
2. SentencePiece scope-vs-backport decision (P0-09) — owner decides: record the supported model scope OR backport the upstream hardening and requalify a replacement candidate. Independent counsel review still required before commercial clearance.
3. Signing + publication (P0-11) — owner must restore the k2 seed or authorize key rotation, identify/provision the approved release-signing key, complete commercial review, and separately authorize signing/publication. Only key in the default GPG home is RedTeam Harness (not eligible).
4. (Optional, not a blocker) If a retained GUI-recorded WAV is wanted as a keepsake artifact, that is a two-minute owner step in the installed GUI.
