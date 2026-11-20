from pathlib import Path

from rhetoric import platform_support


def test_app_config_dir_uses_xdg_on_non_windows(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(platform_support, "is_windows", lambda: False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    assert platform_support.app_config_dir() == tmp_path / "rhetoric"


def test_app_config_dir_uses_appdata_on_windows(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(platform_support, "is_windows", lambda: True)
    monkeypatch.setenv("APPDATA", str(tmp_path))

    assert platform_support.app_config_dir() == tmp_path / "rhetoric"
    assert platform_support.managed_launcher_dir() == tmp_path / "Python" / "Scripts"


def test_app_data_dir_uses_xdg_data_home(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(platform_support, "is_windows", lambda: False)
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert platform_support.app_data_dir() == tmp_path / "rhetoric"


def test_venv_entrypoint_path_switches_per_platform(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(platform_support, "is_windows", lambda: True)
    assert platform_support.venv_entrypoint_path(tmp_path, "rhetoric").name == "rhetoric.exe"

    monkeypatch.setattr(platform_support, "is_windows", lambda: False)
    assert platform_support.venv_entrypoint_path(tmp_path, "rhetoric").as_posix().endswith("/.venv/bin/rhetoric")


def test_invalid_windows_path_parts_flags_reserved_characters() -> None:
    assert platform_support.invalid_windows_path_parts("Input/What is, reality?.txt") == ["What is, reality?.txt"]
    assert platform_support.invalid_windows_path_parts("Input/portable_name.txt") == []
