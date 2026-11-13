"""Fix A (2026-11-12): the audio.cpp per-synthesis timeout has a floor, and
every subprocess budget carries a fixed startup allowance so model load and
shader compilation are never charged to a synthesis.

Background: a persisted ``audio_cpp_timeout: 3`` in saved settings made every
chunk of a GUI render die on the per-synthesis timeout (batch of 4 -> 12s,
zero syntheses finished, PartialRenderError). A warm synthesis alone takes
~3s on the reference GPU and a cold process spends ~10-14s loading the model
and compiling shaders before the first request runs."""
from __future__ import annotations

import subprocess

import pytest

from rhetoric.gui_settings import _normalize_audio_cpp_timeout
from rhetoric.tts_engines import vulkan_backend
from rhetoric.tts_engines.vulkan_backend import (
    MIN_SYNTHESIS_TIMEOUT_SECONDS,
    STARTUP_ALLOWANCE_SECONDS,
    AudioCppVulkanEngine,
)

_FLOOR_INT = int(MIN_SYNTHESIS_TIMEOUT_SECONDS)


def test_constructor_timeout_below_floor_is_raised() -> None:
    engine = AudioCppVulkanEngine(timeout=3)
    assert engine.timeout == MIN_SYNTHESIS_TIMEOUT_SECONDS


def test_constructor_timeout_above_floor_is_kept() -> None:
    engine = AudioCppVulkanEngine(timeout=120)
    assert engine.timeout == 120.0


def test_env_timeout_below_floor_is_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RHETORIC_AUDIOCPP_TIMEOUT", "3")
    engine = AudioCppVulkanEngine()
    assert engine.timeout == MIN_SYNTHESIS_TIMEOUT_SECONDS


def test_env_timeout_above_floor_is_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RHETORIC_AUDIOCPP_TIMEOUT", "900")
    engine = AudioCppVulkanEngine()
    assert engine.timeout == 900.0


def test_batch_timeout_adds_startup_allowance_once() -> None:
    engine = AudioCppVulkanEngine(timeout=3)
    assert engine._batch_timeout(4) == (
        STARTUP_ALLOWANCE_SECONDS + MIN_SYNTHESIS_TIMEOUT_SECONDS * 4
    )
    # An empty/degenerate count still gets one synthesis budget.
    assert engine._batch_timeout(0) == (
        STARTUP_ALLOWANCE_SECONDS + MIN_SYNTHESIS_TIMEOUT_SECONDS
    )


def _capture_run(monkeypatch: pytest.MonkeyPatch) -> dict:
    captured: dict = {}

    def fake_run(command, **kwargs):  # noqa: ANN001, ANN202 - test double
        captured.update(kwargs)
        return subprocess.CompletedProcess(
            args=command, returncode=0, stdout="", stderr=""
        )

    monkeypatch.setattr(vulkan_backend.subprocess, "run", fake_run)
    return captured


def test_run_command_default_budget_includes_startup_allowance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = _capture_run(monkeypatch)
    engine = AudioCppVulkanEngine(timeout=3)
    engine._run_command(["audiocpp_cli"])
    assert captured["timeout"] == (
        STARTUP_ALLOWANCE_SECONDS + MIN_SYNTHESIS_TIMEOUT_SECONDS
    )


def test_run_command_explicit_timeout_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _capture_run(monkeypatch)
    engine = AudioCppVulkanEngine(timeout=3)
    engine._run_command(["audiocpp_cli"], timeout=999)
    assert captured["timeout"] == 999


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (3, _FLOOR_INT),
        (1, _FLOOR_INT),
        ("45", _FLOOR_INT),
        (120, 120),
        (None, None),
        (0, None),
        (-5, None),
        ("abc", None),
    ],
)
def test_normalize_audio_cpp_timeout_floor(value, expected) -> None:  # noqa: ANN001, ANN202
    assert _normalize_audio_cpp_timeout(value) == expected
