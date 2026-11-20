# Rhetoric release-path test suite — re-run 2026-11-20

- Date: 2026-11-20, run 22:00:43–22:06:21 UTC (14:00:43–14:06:21 PST)
- Checkout: /media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric, branch V1.00a-beta_build, HEAD 49f0678 ("test(ci): record final ship-today evidence count")
- Full log: `release_artifacts/evidence-2026-11-19/candidate-rc13/release-path-tests-20261120.log`

## Results

- Release-path suite (11 files: test_frozen_linux_packaging, test_offline_bundle, test_offline_linux_kit, test_install_boundary, test_release, test_licensing_store, test_eula_acceptance, test_linux_entrypoint, test_sign_release_artifact, test_recorder, test_recording_studio): **176 passed in 142.45s**, exit 0. Checklist baseline was 176 passed in 26.61s; today's run was slower (machine under load — NVR stack plus parallel Rhetoric work). No failures.
- Recorder/studio-only run (`tests/test_recorder.py tests/test_recording_studio.py`): **30 passed in 74.27s**, exit 0. Checklist baseline was 30 passed in 12.80s.
- `git diff --check`: clean, exit 0.

## Notes

- No source or test files were modified to make anything pass; failures would have been reported verbatim. There were none.
- An independent run of the same 176-test suite earlier today (`release-path-tests-20261120-wren.log`) also passed: 176 passed in 55.82s.
- GPG-backed signing tests used only temporary pytest keys in /tmp (fixture GNUPGHOME); no production key was used.
