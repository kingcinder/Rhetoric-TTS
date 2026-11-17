# CI remediation notes — 2026-11-17

## Baseline

Last observed beta workflow for `V1.00a-beta_build` / `6a75f88331471499eb5c36c921f9caa4d46009d7`: [Actions run 44149008064](https://github.com/kingcinder/Rhetoric-TTS/actions/runs/44149008064). This run predates the local changes in this note; no hosted run has verified them.

The `Suite counts recorded or inheritable (every head)` job failed because no baseline existed for `6a75f883`; `.venv/bin/python scripts/certify_suite_counts.py --availability` reproduces the gate. The Ubuntu Python 3.11 suite run reported **5 failed, 2319 passed, 35 skipped, 7 warnings**. The failures were four `tests/test_offline_linux_kit.py` cases whose code assumes `audio.cpp/` exists in a standard checkout, plus the record-integrity scan misclassifying two segments of the attached directive UUID as Git commit citations. The Linux frozen AppImage/deb rehearsal passed. The Vulkan job built `audio.cpp` but stopped when the file resolver omitted `X-Repo-Commit`; the Windows installer and compiled license-core jobs passed. Windows matrix/theme jobs had additional failures and remain outside the Ubuntu candidate gate.

## Local scoped changes

- `tests/test_offline_linux_kit.py` now creates a temporary Git checkout with required license fixtures. This keeps source-revision and notice checks exercised without relying on an ignored local `audio.cpp/` directory.
- `tests/test_record_integrity.py` classifies the two UUID segments as non-commit tokens and adds a regression for the attachment path.
- `scripts/record_audio_cpp_model_provenance.py` now falls back to the documented Hugging Face Model API `sha` for the requested revision when a file resolver HEAD response lacks `X-Repo-Commit`. It continues hashing the actual downloaded GGUF bytes before recording provenance.
- `tests/test_audio_cpp_model_provenance.py` covers the fallback and exact model hash.

Focused command:

```text
.venv/bin/python -m pytest -q tests/test_audio_cpp_model_provenance.py tests/test_offline_linux_kit.py tests/test_record_integrity.py::test_attached_document_uuid_is_not_treated_as_commit_citations tests/test_record_integrity.py::test_every_commit_hash_cited_in_the_records_resolves
16 passed in 2.90s
```

The official clean-worktree measurement ran against `6ad8c688143640ed2870e1806552349af2454b70`, documentation revisions `c38cfb325e2bc261bd31ef424dd4739c98a91895` and `c412eb079ac24fa9fdf7de7745bda5c7b5b3c5a3`:

```text
.venv/bin/python scripts/certify_suite_counts.py HEAD --record --capture-output /tmp/rhetoric-v100a-suite-counts-6ad8c68.log
passed=2326 skipped=35 failed=0 errors=0 exit_code=0
```

All three runs observed `passed=2326 skipped=35 failed=0 errors=0 exit_code=0`; raw output is in `suite-counts-6ad8c68.log`, `suite-counts-c38cfb3.log`, and `suite-counts-c412eb0.log`. The recorder wrote a baseline entry for each measured commit. `.venv/bin/python scripts/certify_suite_counts.py --availability` passes for `a6b1f19` by inheriting the exact `c412eb0` suite tree; the only tree difference is `scripts/suite_counts_baseline.json`. `tests/test_suite_counts.py` passed 43 tests. Skip-ID coverage is incomplete (`skipped_ids_complete=false`); the test count remains recorded, and the limitation is in each captured log.

## Limits and next gate

`hf models info audio-cpp/audio.cpp-gguf --revision main --format json` could not resolve DNS from this environment. The fallback is unit-tested against the official Model API response shape, but the live model revision and the workflow's downloaded GGUF digest were not verified here. The exact RC1 archive is unchanged because these changes affect only the provenance recording tool, tests, and release documentation. Require a new hosted workflow run before calling the CI issues fixed.
