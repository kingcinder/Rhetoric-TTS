"""The dispatch force-failure input must fail INSIDE pytest, not before it.

The failure artifact is the only readable evidence a hosted run leaves behind
(the Actions log endpoint needs repository admin rights), so the input has to
prove the capture path, not bypass it. An ``exit 1`` before pytest ran produced
an artifact with no ``pytest.txt`` at all: the one file that says *what* failed.

The workflow now passes the input to the suite as ``RHETORIC_FORCE_TEST_FAILURE``
and this module fails a test when it is set. That means a deliberate red run
still starts pytest, its summary carries a real failure, ``pipefail`` keeps the
step red, and the upload collects ``pytest.txt``, ``resources-before.txt`` and
the post-crash ``resources-after.txt`` together.

The workflow pins below are the ways that could silently regress: an early exit
coming back, the input no longer reaching the suite, the expression losing its
push-event fallback, or the post-crash step being dropped.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
VARIABLE = "RHETORIC_FORCE_TEST_FAILURE"
SUITE_STEP = "Run Test Suite (Linux)"
POST_CRASH_STEP = "Post-Crash Headroom (Linux)"


def test_a_forced_failure_is_a_pytest_failure() -> None:
    """Fail here, where the run can still capture it.

    Deliberately a test and not a workflow step: the point is that pytest ran
    and its failure is in ``ci-test-logs/pytest.txt``.
    """
    requested = os.environ.get(VARIABLE, "").strip().lower()
    if requested in {"1", "true", "yes", "on"}:
        pytest.fail(
            f"{VARIABLE}={requested!r}: failing inside pytest on purpose "
            "(workflow_dispatch force-failure) so the run uploads pytest.txt"
        )


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _step(name: str) -> dict:
    for job in _workflow()["jobs"].values():
        for step in job.get("steps", []):
            if step.get("name") == name:
                return step
    raise AssertionError(f"ci.yml has no step named {name!r}")


def test_the_forced_failure_does_not_exit_before_pytest() -> None:
    """An early exit is exactly what left pytest.txt missing from the artifact."""
    step = _step(SUITE_STEP)
    script = str(step["run"])

    assert "./.venv/bin/pytest" in script
    assert "exit 1" not in script, (
        "the suite step must not fail itself: a forced failure has to come out "
        "of pytest so ci-test-logs/pytest.txt exists in the artifact"
    )
    # pipefail is what keeps the tee'd pytest status authoritative.
    assert "set -o pipefail" in script


def test_the_dispatch_input_reaches_the_suite_as_an_environment_variable() -> None:
    """Passed via env, so the user-controlled text never becomes shell code."""
    step = _step(SUITE_STEP)

    assert step["env"][VARIABLE] == "${{ github.event.inputs['force-failure'] || 'false' }}", (
        "the input must arrive through the step env; splicing it into the shell "
        "and dropping the push-event fallback are both regressions"
    )


def test_the_workflow_keeps_the_post_crash_headroom_probe() -> None:
    """A failed suite still records the state at the moment of the failure."""
    step = _step(POST_CRASH_STEP)

    condition = str(step.get("if", ""))
    assert "failure()" in condition and "runner.os == 'Linux'" in condition, (
        "the post-crash probe must keep running only after a failure, on Linux"
    )
    script = str(step["run"])
    assert "resources-after.txt" in script
    assert "free -m" in script and "df -h" in script


def test_a_failure_uploads_the_whole_log_directory() -> None:
    """pytest.txt and both headroom files travel together or the evidence is split."""
    upload = next(
        step
        for step in _workflow()["jobs"]["test"]["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact")
    )

    assert "failure()" in str(upload.get("if", ""))
    assert str(upload["with"]["path"]).rstrip("/") == "ci-test-logs"
