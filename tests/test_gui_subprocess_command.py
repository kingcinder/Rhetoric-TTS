from __future__ import annotations

import sys

import pytest


@pytest.mark.parametrize(
    ("frozen", "platform_name", "expected"),
    [
        (
            False,
            "linux",
            ["python", "-m", "rhetoric.render_subprocess", "--job", "job.json"],
        ),
        (
            True,
            "linux",
            ["/opt/rhetoric/usr/bin/rhetoric", "--rhetoric-render-subprocess", "--job", "job.json"],
        ),
        (
            True,
            "win32",
            ["/opt/rhetoric/usr/bin/rhetoric", "-m", "rhetoric.render_subprocess", "--job", "job.json"],
        ),
    ],
)
def test_render_child_command_matches_runtime(
    monkeypatch: pytest.MonkeyPatch,
    frozen: bool,
    platform_name: str,
    expected: list[str],
) -> None:
    monkeypatch.setattr(sys, "frozen", frozen, raising=False)
    monkeypatch.setattr(sys, "platform", platform_name)
    from rhetoric.gui_render import _render_subprocess_command

    command = _render_subprocess_command("python" if not frozen else expected[0], ["--job", "job.json"])

    assert command == expected


def test_vulkan_child_environment_uses_installed_radeon_icd(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    import os
    import rhetoric.gui_render as gui_render

    manifest = tmp_path / "radeon_icd.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gui_render, "_RADEON_ICD_MANIFEST", manifest)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("VK_ICD_FILENAMES", raising=False)
    monkeypatch.delenv("VK_DRIVER_FILES", raising=False)

    env = gui_render._render_child_environment(tmp_path, inference_backend="vulkan")

    assert env["VK_ICD_FILENAMES"] == str(manifest)


def test_vulkan_child_environment_preserves_explicit_icd_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    import rhetoric.gui_render as gui_render

    manifest = tmp_path / "radeon_icd.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gui_render, "_RADEON_ICD_MANIFEST", manifest)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("VK_ICD_FILENAMES", "/custom/icd.json")

    env = gui_render._render_child_environment(tmp_path, inference_backend="vulkan")

    assert env["VK_ICD_FILENAMES"] == "/custom/icd.json"


def test_vulkan_child_environment_preserves_explicit_driver_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    import rhetoric.gui_render as gui_render

    manifest = tmp_path / "radeon_icd.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gui_render, "_RADEON_ICD_MANIFEST", manifest)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("VK_ICD_FILENAMES", raising=False)
    monkeypatch.setenv("VK_DRIVER_FILES", "/custom/driver.json")

    env = gui_render._render_child_environment(tmp_path, inference_backend="vulkan")

    assert "VK_ICD_FILENAMES" not in env
    assert env["VK_DRIVER_FILES"] == "/custom/driver.json"


def test_cpu_child_environment_does_not_change_vulkan_icd(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    import rhetoric.gui_render as gui_render

    manifest = tmp_path / "radeon_icd.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gui_render, "_RADEON_ICD_MANIFEST", manifest)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("VK_ICD_FILENAMES", raising=False)
    monkeypatch.delenv("VK_DRIVER_FILES", raising=False)

    env = gui_render._render_child_environment(tmp_path, inference_backend="pytorch")

    assert "VK_ICD_FILENAMES" not in env


def test_offline_install_forces_model_libraries_offline_in_render_child(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    import rhetoric.gui_render as gui_render

    (tmp_path / ".rhetoric_offline").touch()
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "0")

    env = gui_render._render_child_environment(tmp_path, inference_backend="pytorch")

    assert env["HF_HUB_OFFLINE"] == "1"
    assert env["TRANSFORMERS_OFFLINE"] == "1"


def test_nonoffline_child_preserves_model_library_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    import rhetoric.gui_render as gui_render

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "0")

    env = gui_render._render_child_environment(tmp_path, inference_backend="pytorch")

    assert env["HF_HUB_OFFLINE"] == "0"
    assert env["TRANSFORMERS_OFFLINE"] == "0"
