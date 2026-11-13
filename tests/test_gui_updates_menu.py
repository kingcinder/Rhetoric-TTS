"""Fix B (2026-11-12): the automated-updates opt-out lives in the Settings
menu, not in Shared Render Settings (owner order: it has nothing to do with
rendering). The support gate keeps reading the same
``automatic_updates_enabled`` settings key; only the control's location
changed."""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from rhetoric.gui_settings import load_app_settings
from tests.test_app_gui_profiles import _build_window


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app


def _settings_menu(window):  # noqa: ANN001, ANN202 - test helper
    for action in window.menuBar().actions():
        if action.text() == "Settings":
            return action.menu()
    raise AssertionError("Settings menu not found")


def test_updates_opt_out_is_a_settings_menu_action(
    qt_app, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    window, _paths = _build_window(monkeypatch, tmp_path)
    action = window.automated_updates_action
    assert action.isCheckable()
    assert action.text() == "Turn off automated updates"
    assert action.objectName() == "automated_updates_opt_out"
    assert action in _settings_menu(window).actions()
    # The old render-panel checkbox is gone.
    assert not hasattr(window, "automated_updates_check")
    # Default: updates enabled -> opt-out unchecked.
    assert action.isChecked() is False
    # The owner's support warning survives in full, as the tooltip.
    assert "will not be able to submit bug tickets" in action.toolTip()


def test_updates_opt_out_initial_state_follows_saved_setting(
    qt_app, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    window, _paths = _build_window(
        monkeypatch, tmp_path, preseed_app_settings={"automatic_updates_enabled": False}
    )
    assert window.automated_updates_action.isChecked() is True


def test_updates_opt_out_toggle_persists_the_gate_key(
    qt_app, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    window, _paths = _build_window(monkeypatch, tmp_path)
    window.automated_updates_action.setChecked(True)
    assert load_app_settings()["automatic_updates_enabled"] is False
    window._on_automated_updates_toggled(False)
    assert load_app_settings()["automatic_updates_enabled"] is True
