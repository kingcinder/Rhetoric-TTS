# Rhetoric RC13 security scan refresh — 2026-11-20

Candidate: RC13 (`Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz`, SHA-256 `b1fcd5e4f8880776e4ae076aae5466adf48fa5e025d4dc5daf24ad8b10a97f8d`).
Scan date: 2026-11-20. Host disk at scan time: root 43G free (91% full), Data drive 57G free.
This is a point-in-time refresh of checklist P0-09. It is not counsel, not commercial clearance, and not release clearance.

## 1. Python dependencies — pip-audit (OSV)

- Tool: pip-audit **2.10.1** (installed via pipx on 2026-11-20), vulnerability service **OSV** (passed explicitly with `-s osv`; pip-audit's default service is PyPI).
- Scope: the 124-component Python dependency inventory recorded by the candidate SBOM (`release_artifacts/linux-frozen-rc13-20261119/sbom.json`, CycloneDX 1.4, no purls — name + version only).
- Command: `pip-audit -r <resolvable-subset> -s osv --disable-pip --no-deps --format json`
- **Result: 0 vulnerabilities across the audited scope.**
  - pip-audit audited 119 of the 124 pins. 5 pins could not be resolved by pip and were excluded from the pip-audit run:
    - `resemble-perth==1.1.0` — not published on PyPI (only 1.0.0/1.0.1 exist there)
    - `rhetoric==1.5.0` — the application itself, not a PyPI package
    - `torch==2.15.0+cpu`, `torchaudio==2.11.1+cpu`, `torchvision==0.29.2+cpu` — local `+cpu` builds; PyPI carries the base versions only
  - A direct OSV batch query covered **all 124 pins** (same data source pip-audit uses) and returned **0 vulnerabilities**, including for the 5 excluded pins.
  - A supplemental OSV check of the base versions behind the local builds (`torch 2.15.0`, `torchaudio 2.11.1`, `torchvision 0.29.2`) and the latest published `resemble-perth 1.0.1` also returned **0 vulnerabilities**.
  - Two pip-audit runs without `--disable-pip --no-deps` failed before auditing: first on the unpublished `resemble-perth==1.1.0` pin, then on a dependency conflict between the frozen pins and `transformers==5.20.0`. The frozen pin set cannot be re-resolved as a fresh install; the `--disable-pip --no-deps` run audits the pins as specified, which is the correct mode for a frozen SBOM inventory.
- Files:
  - `candidate-rc13/pip-audit-20261120.json` — SHA-256 `6a963df5aabf8980263fc7f22c6a65e75bc2c21218f61921f9e307b37fe543e4`
  - `candidate-rc13/pip-audit-20261120-osv-supplement.json` — raw OSV batch response for all 124 pins — SHA-256 `5759b1f895a4520813b003c3df171cc0022e6825640cc5a2ab04259812a31616`
  - `candidate-rc13/pip-audit-20261120-osv-base-versions.json` — OSV check of base versions — SHA-256 `9514e3a939a8fadc213503185e9e00f208726b70ed3668c667eeab1c7dc2d63c`

## 2. Ubuntu 24.04 runtime debs — Trivy

- Tool: Trivy **0.74.0**. Vulnerability DB updated **2026-11-20 18:59:53 UTC** (downloaded 2026-11-20 22:02:23 UTC, Version 2, next update 2026-11-21 18:59:53 UTC).
- Method: identical to the prior scan — synthetic rootfs built from the exact kit runtime-deb control metadata (`linux-frozen-rc13-20261119/kit/runtime-debs`, 94 debs), scanned with `trivy rootfs --distro ubuntu/24.04 --pkg-types os --scanners vuln --format json`. Package files were not installed on this host. The 94-package set was verified identical to the prior scan's set (same name-version pairs). Kit `SHA256SUMS` verified: **all 129 entries match**.
- **Result: 42 advisories — 31 MEDIUM, 11 LOW, 0 CRITICAL, 0 HIGH. All 42 have no fixed Ubuntu version recorded in the database.**
- Comparison with the prior scan: the 2026-11-19 scan (DB updated 2026-11-20 01:04:07 UTC) reported **0 advisories** for the identical 94-package set. The delta is the database, not the packages — roughly 18 hours of DB updates added these advisories.
- Top affected packages: avahi (9 across 3 packages), krb5 (8 across 4 packages), libexpat1 (5), libsndfile1 (5), libxi6 (4), libcups2t64 (3).
- Full list (all 42; `fixed: none` for every entry):

| Severity | CVE | Package | Installed version |
|---|---|---|---|
| MEDIUM | CVE-2025-52194 | libsndfile1 | 1.2.2-1ubuntu5.24.04.1 |
| MEDIUM | CVE-2025-59529 | libavahi-client3 | 0.8-13ubuntu6.2 |
| MEDIUM | CVE-2025-59529 | libavahi-common-data | 0.8-13ubuntu6.2 |
| MEDIUM | CVE-2025-59529 | libavahi-common3 | 0.8-13ubuntu6.2 |
| MEDIUM | CVE-2025-66382 | libexpat1 | 2.6.1-2ubuntu0.6 |
| MEDIUM | CVE-2026-102633 | libexpat1 | 2.6.1-2ubuntu0.6 |
| MEDIUM | CVE-2026-107708 | libgssapi-krb5-2 | 1.20.1-6ubuntu2.10 |
| MEDIUM | CVE-2026-107708 | libk5crypto3 | 1.20.1-6ubuntu2.10 |
| MEDIUM | CVE-2026-107708 | libkrb5-3 | 1.20.1-6ubuntu2.10 |
| MEDIUM | CVE-2026-107708 | libkrb5support0 | 1.20.1-6ubuntu2.10 |
| MEDIUM | CVE-2026-107778 | libgssapi-krb5-2 | 1.20.1-6ubuntu2.10 |
| MEDIUM | CVE-2026-107778 | libk5crypto3 | 1.20.1-6ubuntu2.10 |
| MEDIUM | CVE-2026-107778 | libkrb5-3 | 1.20.1-6ubuntu2.10 |
| MEDIUM | CVE-2026-107778 | libkrb5support0 | 1.20.1-6ubuntu2.10 |
| MEDIUM | CVE-2026-109088 | libxtst6 | 2:1.2.3-1.1ubuntu0.1 |
| MEDIUM | CVE-2026-113351 | libexpat1 | 2.6.1-2ubuntu0.6 |
| MEDIUM | CVE-2026-119373 | libsqlite3-0 | 3.45.1-1ubuntu2.9 |
| MEDIUM | CVE-2026-120749 | libdbus-1-3 | 1.14.10-4ubuntu4.1 |
| MEDIUM | CVE-2026-37555 | libsndfile1 | 1.2.2-1ubuntu5.24.04.1 |
| MEDIUM | CVE-2026-55480 | libcups2t64 | 2.4.7-1.2ubuntu7.14 |
| MEDIUM | CVE-2026-61702 | libcups2t64 | 2.4.7-1.2ubuntu7.14 |
| MEDIUM | CVE-2026-77214 | libexpat1 | 2.6.1-2ubuntu0.6 |
| MEDIUM | CVE-2026-86469 | libglib2.0-0t64 | 2.80.0-6ubuntu3.10 |
| MEDIUM | CVE-2026-87875 | libcups2t64 | 2.4.7-1.2ubuntu7.14 |
| MEDIUM | CVE-2026-88372 | libsndfile1 | 1.2.2-1ubuntu5.24.04.1 |
| MEDIUM | CVE-2026-88807 | libxrender1 | 1:0.9.10-1.1build1 |
| MEDIUM | CVE-2026-93541 | libxi6 | 2:1.8.1-1build1 |
| MEDIUM | CVE-2026-93542 | libxi6 | 2:1.8.1-1build1 |
| MEDIUM | CVE-2026-93543 | libxi6 | 2:1.8.1-1build1 |
| MEDIUM | CVE-2026-93544 | libxi6 | 2:1.8.1-1build1 |
| MEDIUM | CVE-2026-93990 | libexpat1 | 2.6.1-2ubuntu0.6 |
| LOW | CVE-2024-50613 | libsndfile1 | 1.2.2-1ubuntu5.24.04.1 |
| LOW | CVE-2024-52615 | libavahi-client3 | 0.8-13ubuntu6.2 |
| LOW | CVE-2024-52615 | libavahi-common-data | 0.8-13ubuntu6.2 |
| LOW | CVE-2024-52615 | libavahi-common3 | 0.8-13ubuntu6.2 |
| LOW | CVE-2024-52616 | libavahi-client3 | 0.8-13ubuntu6.2 |
| LOW | CVE-2024-52616 | libavahi-common-data | 0.8-13ubuntu6.2 |
| LOW | CVE-2024-52616 | libavahi-common3 | 0.8-13ubuntu6.2 |
| LOW | CVE-2025-1352 | libelf1t64 | 0.190-1.1ubuntu0.1 |
| LOW | CVE-2025-1376 | libelf1t64 | 0.190-1.1ubuntu0.1 |
| LOW | CVE-2025-5222 | libicu74 | 74.2-1ubuntu3.1 |
| LOW | CVE-2025-56226 | libsndfile1 | 1.2.2-1ubuntu5.24.04.1 |

- Notes on the findings: most are denial-of-service or crafted-input issues in libraries the application links (expat XML parsing, libsndfile audio-file parsing, krb5, avahi, cups, X11 input libraries). No CRITICAL or HIGH severity was reported, and no fixed Ubuntu version exists in the database for any of the 42 — so there is currently no newer runtime deb to upgrade to. This is a refresh finding to record, not something patchable by rebuilding the same candidate.
- Files:
  - `candidate-rc13/ubuntu-runtime-vulnerability-report-20261120.json` — SHA-256 `6042b19fa021f237acfc57d3d0a9f9b2c48c93a8d43d6cbcb90f566cf31a926e`
  - `candidate-rc13/ubuntu-runtime-security-summary-20261120.json` — SHA-256 `8a8fc06d87f6c90e4068f69a062fe53b745ae99c99ff7dc0eabb028115908c96`
  - `candidate-rc13/ubuntu-runtime-trivy-db-version-20261120.txt` — SHA-256 `a3b243cf262937427fc85bf9be3aa43fd74b9b2dea27f591a6e7f18a4846b9a1`
  - Synthetic rootfs used: `/tmp/rhetoric-rc13-runtime-rootfs-20261120` (rebuilt from the exact kit debs; the JSON report is the durable artifact)

## 3. SentencePiece 0.2.1 / issue #1269

Re-checked upstream 2026-11-20. The fix for #1269 shipped in sentencepiece **0.2.2** (2026-07-12; "Model loading verifies darts-clone trie offsets"), with regression test `RejectCorruptedModel1269`; latest PyPI release is **0.2.3** (2026-11-04/05). RC13 still bundles **0.2.1** and does not contain fix commit d685ef31. The supported Chatterbox route does not load `.model` files (uses `tokenizer.json`), so the residual is confined to the generic CLI loading an untrusted model (process DoS only). Full detail and the two options are in the decision note: `evidence-2026-11-20/sentencepiece-1269-decision-note-20261120.md`. The owner decides; no decision is made here. CVE-2026-1260 is a separate defect and is patched in 0.2.1.

## 4. Implications for checklist P0-09

- The prior P0-09 record ("Trivy reported no advisories") no longer holds under today's database: **42 MEDIUM/LOW advisories** now attach to the exact pinned runtime debs, with no fixed versions available. The Python side remains clean (0 vulnerabilities).
- This does not by itself block the release — no CRITICAL/HIGH, and no fix exists to apply — but P0-09's state needs updating by the release coordinator, and scans must be refreshed again before distribution, since the database moves daily.
- The SentencePiece decision (record scope vs. backport + requalify) is still open and belongs to the owner.

## 5. Limitations

- Point-in-time scans; refresh before distribution.
- No C/C++ binary vulnerability scan of the audio.cpp executable; no scan of model weights, kernel, firmware, or customer host libraries.
- The Trivy scan covers Ubuntu runtime deb package metadata only; the candidate's 124-component library SBOM does not inventory those debs.
- pip-audit covers the SBOM Python inventory as pinned; 5 pins were audited via direct OSV queries instead of pip-audit because pip cannot resolve them (see section 1).
- Nothing here is counsel review or release clearance.

## 6. Files written by this refresh

All under `/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric/release_artifacts/`:

| File | SHA-256 |
|---|---|
| `evidence-2026-11-19/candidate-rc13/pip-audit-20261120.json` | `6a963df5aabf8980263fc7f22c6a65e75bc2c21218f61921f9e307b37fe543e4` |
| `evidence-2026-11-19/candidate-rc13/pip-audit-20261120-osv-supplement.json` | `5759b1f895a4520813b003c3df171cc0022e6825640cc5a2ab04259812a31616` |
| `evidence-2026-11-19/candidate-rc13/pip-audit-20261120-osv-base-versions.json` | `9514e3a939a8fadc213503185e9e00f208726b70ed3668c667eeab1c7dc2d63c` |
| `evidence-2026-11-19/candidate-rc13/ubuntu-runtime-vulnerability-report-20261120.json` | `6042b19fa021f237acfc57d3d0a9f9b2c48c93a8d43d6cbcb90f566cf31a926e` |
| `evidence-2026-11-19/candidate-rc13/ubuntu-runtime-security-summary-20261120.json` | `8a8fc06d87f6c90e4068f69a062fe53b745ae99c99ff7dc0eabb028115908c96` |
| `evidence-2026-11-19/candidate-rc13/ubuntu-runtime-trivy-db-version-20261120.txt` | `a3b243cf262937427fc85bf9be3aa43fd74b9b2dea27f591a6e7f18a4846b9a1` |
| `evidence-2026-11-20/security-scan-refresh-20261120.md` | (this file) |
| `evidence-2026-11-20/sentencepiece-1269-decision-note-20261120.md` | (decision note) |

No existing evidence files were overwritten. No source was modified. No commit or push was made by this refresh.
