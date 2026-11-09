"""The automated-updates opt-out setting: default on, persists, normalizes."""
from __future__ import annotations

from pathlib import Path

import pytest

from the_oracle import gui_settings


@pytest.fixture()
def settings_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    target = tmp_path / "app-settings.json"
    monkeypatch.setattr(gui_settings, "app_settings_path", lambda: target)
    return target


def test_automatic_updates_default_enabled(settings_file: Path) -> None:
    assert gui_settings.load_app_settings()["automatic_updates_enabled"] is True


def test_opt_out_persists_across_save_and_load(settings_file: Path) -> None:
    gui_settings.save_app_settings({"automatic_updates_enabled": False})
    assert gui_settings.load_app_settings()["automatic_updates_enabled"] is False
    gui_settings.save_app_settings({"automatic_updates_enabled": True})
    assert gui_settings.load_app_settings()["automatic_updates_enabled"] is True


def test_opt_out_normalizes_hand_edited_values(settings_file: Path) -> None:
    settings_file.write_text('{"automatic_updates_enabled": "false"}', encoding="utf-8")
    assert gui_settings.load_app_settings()["automatic_updates_enabled"] is False
    settings_file.write_text('{"automatic_updates_enabled": "off"}', encoding="utf-8")
    assert gui_settings.load_app_settings()["automatic_updates_enabled"] is False
    settings_file.write_text('{"automatic_updates_enabled": true}', encoding="utf-8")
    assert gui_settings.load_app_settings()["automatic_updates_enabled"] is True
    settings_file.write_text('{"automatic_updates_enabled": ', encoding="utf-8")
    assert gui_settings.load_app_settings()["automatic_updates_enabled"] is True
