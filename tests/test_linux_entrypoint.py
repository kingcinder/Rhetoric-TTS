import importlib.util
import os
import sys
import types
from pathlib import Path

import pytest

ENTRYPOINT = Path(__file__).resolve().parents[1] / "packaging" / "linux" / "entrypoint.py"
SPEC = importlib.util.spec_from_file_location("rhetoric_linux_entrypoint", ENTRYPOINT)
assert SPEC is not None and SPEC.loader is not None
entrypoint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(entrypoint)


def test_frozen_entrypoint_enables_numba_user_cache_locator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    monkeypatch.delenv("NUMBA_CACHE_LOCATOR_CLASSES", raising=False)

    entrypoint.configure_frozen_numba_cache()

    assert sys.frozen is True
    assert os.environ["NUMBA_CACHE_LOCATOR_CLASSES"] == "UserWideCacheLocator"


def test_frozen_entrypoint_dispatches_private_render_child(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    child_module = types.ModuleType("rhetoric.render_subprocess")
    child_module.main = lambda argv: calls.append(argv) or 17
    monkeypatch.setitem(sys.modules, "rhetoric.render_subprocess", child_module)
    monkeypatch.setattr(sys, "argv", ["rhetoric", "--rhetoric-render-subprocess", "--job", "job.json"])
    monkeypatch.setattr(entrypoint.multiprocessing, "freeze_support", lambda: None)

    assert entrypoint.main() == 17
    assert calls == [["--job", "job.json"]]
