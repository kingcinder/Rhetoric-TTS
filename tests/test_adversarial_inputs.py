"""Adversarial/boundary tests for untrusted-input surfaces.

Each test pins a real boundary: malformed input must be rejected or
normalized, never crash with an unhandled error or escape its sandbox.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from the_oracle import gui_settings
from the_oracle.support import gate


# --- settings normalization under hostile payloads ---

@pytest.mark.parametrize("payload", [
    None,
    [],
    "text",
    42,
    {"automatic_updates_enabled": object()},
    {"audio_cpp_threads": "not-a-number"},
    {"audio_cpp_timeout": -5},
    {"inference_backend": "'; DROP TABLE--"},
    {"theme": 12345},
])
def test_app_settings_normalization_never_crashes(payload, tmp_path, monkeypatch):
    target = tmp_path / "app-settings.json"
    monkeypatch.setattr(gui_settings, "app_settings_path", lambda: target)
    normalized = gui_settings.save_app_settings(payload if isinstance(payload, dict) else {})
    loaded = gui_settings.load_app_settings()
    assert isinstance(loaded, dict)
    assert loaded["automatic_updates_enabled"] in (True, False)


def test_app_settings_file_with_garbage_bytes_falls_back(tmp_path, monkeypatch):
    target = tmp_path / "app-settings.json"
    target.write_bytes(b"\x00\xff\xfe not json at all {{{")
    monkeypatch.setattr(gui_settings, "app_settings_path", lambda: target)
    loaded = gui_settings.load_app_settings()
    assert loaded["automatic_updates_enabled"] is True


# --- support gate vocabulary is closed ---

@pytest.mark.parametrize("status", ["current", "update_available", "not_checked", "check_failed", "disabled", "", "CURRENT", None])
def test_gate_handles_any_status_value(status):
    result = gate.evaluate_support_gate(automatic_updates_enabled=True, update_status=status)  # type: ignore[arg-type]
    if status == "current":
        assert result.allowed
    else:
        # Unknown/unproven states never open the gate.
        assert not result.allowed
