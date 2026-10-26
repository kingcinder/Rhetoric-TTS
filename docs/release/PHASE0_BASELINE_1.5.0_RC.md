# Phase 0 Baseline — Rhetoric 1.5.0

Date: 2026-10-25  
Canonical checkout: `/media/cody/Data/DOCUMENTS_PROJECT_FILES/the oracle tts`  
Branch: `release/1.5.0-final`  
Base commit: `93a55d4` (`main`)

## Environment and initial source state

- Python 3.12.3; fresh environment `/tmp/rhetoric-phase0-venv`; editable dev
  install succeeded.
- The checked-in `.venv` runs through its Python binary; generated wrappers
  have a stale absolute shebang, so verification used the interpreter directly.
- Initial source inventory: 445 tracked files, 30,831 Python LOC under `src`,
  and 169 `test_*.py` files. The user-excluded `Seashells/` area was not
  inventoried or inspected.
- Initial working tree was clean on `main`; `release/1.5.0-final` was created
  from `93a55d4`.

## Baseline checks and causes

| Check | Observed result / disposition |
|---|---|
| `scripts/release.py --check` | Initially blocked by stale release dates/banner metadata; the current version guard now passes on the candidate. |
| `scripts/certify_suite_counts.py --availability` | Initially inherited 2,124 passed / 3 skipped from pre-migration evidence; that count was not a fresh-repository measurement. A fresh-worktree run later recorded the candidate commit separately. |
| `scripts/generate_third_party_notices.py --check` | Pass, 117 components. |
| `scripts/soft_launch.py --check --json` | Blocked by the draft EULA; LGPL notice/source/replacement obligations were a warning. It was not rerun after final doc changes because its automated asset check is outside the authorized scope. |
| `pip check` | Pass; no broken requirements. |
| `pip-audit` | No known vulnerabilities in the auditable installed packages; local/non-PyPI dependencies were skipped. |
| `gitleaks git --log-opts='--all' --redact --no-banner` | Pass; no findings across 1,110 commits. |
| `detect-secrets scan .` | 147 candidates across 18 files: 144 high-entropy hex, 1 keyword, 2 Base64. Candidates were not promoted to findings or claimed clean; values were not reproduced. |
| `test_every_commit_hash_cited_in_the_records_resolves` | Initially failed because historical release records cited commits absent from this repository. The records now identify preserved identifiers as pre-migration provenance; the current test passes. |

Initial failures had three separate causes: old-repository commit citations
were treated as current evidence; the 1.5.0 release date/banner invariant
was inconsistent; and the suite-count baseline was inherited rather than
measured from a fresh checkout. No test or gate was disabled to resolve them.

## Current committed-candidate suite evidence

On source commit `92c55b86ff86`, the canonical release command completed with
**2,144 passed, 6 warnings, 0 failed in 395.90 seconds**. A fresh-worktree
count recorded on `d39a94573d35` **2,141 passed, 3 skipped, 0 failed/errors**.
The Vulkan device smoke was the identified environment skip; the test skip
ledger does not retain every skip ID because its audit test clears that ledger.
The checksum and baseline-record commits do not change the shipped package
contents; a final fresh-worktree count is recorded for the checksum-bearing
head and the following baseline-only head inherits it.
