"""Legacy path values inside settings are rewritten to the current homes.

The rename migrated data folders but not path values stored inside settings
files. The owner's live settings held four former-name paths, so GUI renders
wrote into a legacy Documents folder while he looked in the current Output
folders. Migration happens on load (and is persisted by the next save), never
by hand-editing the file.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rhetoric.gui_settings import (
    app_settings_path,
    load_app_settings,
    load_gui_settings,
    save_app_settings,
    save_gui_settings,
)
from rhetoric.platform_support import app_data_dir
from tests.helpers import isolate_user_config


@pytest.fixture()
def isolated_homes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    isolate_user_config(monkeypatch, tmp_path / "config")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    return app_data_dir()


def _write_app_settings(payload: dict) -> None:
    path = app_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_the_owners_four_legacy_values_are_rewritten_on_load(isolated_homes: Path) -> None:
    legacy_docs = "/home/cody/Documents/the oracle tts"
    _write_app_settings(
        {
            "default_input_dir": f"{legacy_docs}/Input",
            "default_output_dir": f"{legacy_docs}/Output",
            "gui": {
                "version": 1,
                "project": {"output_dir": f"{legacy_docs}/Output"},
                "speakers": {"A": {"reference_path": "/media/x/Seashells/Cody.wav"}},
            },
            "recording_settings": {
                "output_dir": "/home/cody/.local/share/the_oracle/Seashells"
            },
        }
    )

    loaded = load_app_settings()

    assert loaded["default_input_dir"] == str(isolated_homes / "Input")
    assert loaded["default_output_dir"] == str(isolated_homes / "Output")
    assert loaded["gui"]["project"]["output_dir"] == str(isolated_homes / "Output")
    # The old per-user data dir maps to its "rhetoric" sibling in place (the
    # folder the rename actually moved the data to), independent of XDG_DATA_HOME.
    recorder_dir = loaded["recording_settings"]["output_dir"]
    assert recorder_dir.endswith("/rhetoric/Seashells")
    assert "the_oracle" not in recorder_dir.lower()
    # A current-home reference path is untouched.
    assert loaded["gui"]["speakers"]["A"]["reference_path"] == "/media/x/Seashells/Cody.wav"


def test_the_migrated_values_persist_through_a_save(isolated_homes: Path) -> None:
    _write_app_settings(
        {
            "default_output_dir": "/home/cody/Documents/the oracle tts/Output",
        }
    )

    save_app_settings(load_app_settings())

    saved = json.loads(app_settings_path().read_text(encoding="utf-8"))
    assert saved["default_output_dir"] == str(isolated_homes / "Output")
    assert "the oracle" not in json.dumps(saved).lower()


def test_profile_output_dir_is_migrated_on_load_and_save(
    isolated_homes: Path, tmp_path: Path
) -> None:
    profile = tmp_path / "profile.json"
    save_gui_settings(
        profile,
        {
            "version": 1,
            "project": {
                "output_dir": "/home/cody/Documents/the oracle tts/Output",
                "output_filename": "take.flac",
            },
            "speakers": {"A": {"reference_path": "/media/x/Cody.wav"}},
        },
    )

    loaded = load_gui_settings(profile)

    assert loaded["project"]["output_dir"] == str(isolated_homes / "Output")


def test_unrelated_paths_are_left_alone(isolated_homes: Path) -> None:
    _write_app_settings(
        {
            "default_output_dir": "/media/cody/Data/Audio Output",
            "audio_cpp_cli": "/opt/audiocpp/bin/audiocpp_cli",
        }
    )

    loaded = load_app_settings()

    assert loaded["default_output_dir"] == "/media/cody/Data/Audio Output"
    assert loaded["audio_cpp_cli"] == "/opt/audiocpp/bin/audiocpp_cli"
