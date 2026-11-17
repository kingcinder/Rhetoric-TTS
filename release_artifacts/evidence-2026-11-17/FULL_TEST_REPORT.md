# Full test report — source `32ac9df7200e5fedf04dfd01c0edb55be642dd50`

Command: `.venv/bin/python -m pytest -n 12 --dist=loadgroup -q --tb=short`

Result: **2357 passed, 2 skipped, 6 warnings; exit 0; 707.34 seconds.** Full captured output: `full-suite-32ac9df.log`.

Skips:

- `tests/test_powershell_wrapper.py::test_powershell_wrapper_dispatches_when_python_is_only_a_single_command` — host Snap confinement blocks PowerShell before it starts.
- `tests/test_vulkan_backend.py::test_vulkan_backend_smoke_requires_device` — no Vulkan device is available in the test environment.

Warnings: six multiprocessing `DeprecationWarning`s from `os.fork()` in multithreaded pytest workers (three named concurrency tests reported twice under xdist). No failures remain.

The initial diagnostic run exposed a generated shader patch artifact CRLF drift and timed out a slow doctor worker. The patch was regenerated with the repository script and committed as `32ac9df`; the generator file suite passed 10/10, offline bundle/guarantee suites passed 44/44, and the stable doctor read-only suite passed 8/8. The final full suite passed after these checks with no concurrent repository mutation.
