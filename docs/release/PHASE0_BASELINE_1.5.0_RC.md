# Phase 0 Baseline — Rhetoric 1.5.0

Date: 2026-10-25
Branch: `release/1.5.0-final`
Base commit: `93a55d4` (`main`)

## Environment and source state

- Canonical checkout was clean on `main`; branch created locally as requested.
- Python: 3.12.3. Fresh environment `/tmp/rhetoric-phase0-venv`; editable dev install succeeded.
- The checked-in `.venv` works through its Python binary, but generated entrypoint wrappers contain a stale absolute shebang. The fresh environment was used for tool checks.
- Initial source size: 445 tracked files; 30,831 Python LOC under `src`; 169 `test_*.py` files. `Seashells/` was excluded from inventory and remains untouched.

## Baseline commands and results

| Check | Result |
|---|---|
| `scripts/release.py --check` | Pass after adding a package/artifact version invariant and removing stale 1.1.1–1.4.2 artifacts/manifests. |
| `scripts/certify_suite_counts.py --availability` | Pass for inherited baseline 2,124 passed / 3 skipped; this is not a fresh final-tree measurement. |
| `scripts/generate_third_party_notices.py --check` | Pass, 117 components. |
| `scripts/soft_launch.py --check --json` | Blocked by draft EULA and missing current checksum manifest; LGPL source/replacement warning. |
| `pip check` | Pass, no broken requirements. |
| `pip-audit` | No known vulnerabilities among auditable packages; local and non-PyPI dependencies were skipped. |
| `gitleaks git --log-opts=--all --redact --no-banner` | Pass, no findings across 1,110 commits. |
| `detect-secrets scan .` | 147 high-entropy candidates across 18 files; these require classification and are not asserted to be secrets or clean. |
| `test_every_commit_hash_cited_in_the_records_resolves` | Pass at baseline. |

The first full-suite run overlapped edits and is not valid evidence. After all changes stopped, `./.venv/bin/python -m pytest -q` completed with **2,136 passed, 6 warnings, 0 failed** in 384.87 seconds.
