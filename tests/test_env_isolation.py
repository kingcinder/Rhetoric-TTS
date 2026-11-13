"""Regression guard for the global RHETORIC_* env isolation.

The autouse ``_restore_rhetoric_env`` fixture in ``tests/conftest.py`` must
guarantee that no test can leak ``RHETORIC_*`` environment variables into a
later test — even when the code under test writes ``os.environ`` directly,
bypassing ``monkeypatch``. These two tests prove the mechanism: the first
deliberately mutates the environment the worst possible way (direct writes,
including a brand-new key), and the second asserts the environment is exactly
back to the module baseline. If the fixture is ever weakened or removed, the
second test fails loudly instead of silently hiding the pollution.
"""

from __future__ import annotations

import os

_RHETORIC_PREFIX = "RHETORIC_"

# Captured at module import (before any test in this module runs). Because the
# autouse fixture restores RHETORIC_* after every test — including tests in
# earlier files — this is the clean baseline the mutating test must not disturb.
_BASELINE = {
    key: value
    for key, value in os.environ.items()
    if key.startswith(_RHETORIC_PREFIX)
}


def _rhetoric_env() -> dict[str, str]:
    return {
        key: value
        for key, value in os.environ.items()
        # The suite's autouse render-work fixture seeds this one for every test;
        # it is part of the harness baseline, not a leak from a test body.
        if key.startswith(_RHETORIC_PREFIX) and key != "RHETORIC_RENDER_WORK"
    }


def test_rhetoric_env_mutated_directly() -> None:
    """Deliberately pollute the session env the worst possible way: direct
    ``os.environ`` writes and deletions that ``monkeypatch`` cannot track — a
    changed value, a brand-new key, and every pre-existing RHETORIC_* key
    removed. The autouse fixture must put all of it back afterwards."""
    os.environ["RHETORIC_AUDIOCPP_MODEL"] = "/tmp/leaked-model.gguf"
    os.environ["RHETORIC_BRAND_NEW_FLAG"] = "1"
    for key in [key for key in os.environ if key.startswith(_RHETORIC_PREFIX)]:
        os.environ.pop(key, None)


def test_rhetoric_env_restored_after_mutating_test() -> None:
    """Runs after the mutator; the autouse restore fixture must have put the
    environment back to the module baseline — changed values, created keys,
    and deleted keys all restored."""
    assert _rhetoric_env() == _BASELINE
