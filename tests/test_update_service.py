"""Headless tests for the manifest core, the update service, and the gate.

No live network: every fetch is an injected fake serving a local fixture.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from rhetoric import update_manifest as um
from rhetoric import update_service as us
from rhetoric.support import gate


def _manifest(tmp_path: Path, version: str = "9.9.9", artifact_bytes: bytes = b"new appimage bytes"):
    name = "Rhetoric-9.9.9.AppImage"
    payload = {
        "format": 1,
        "version": version,
        "artifacts": [
            {"name": name, "sha256": hashlib.sha256(artifact_bytes).hexdigest(), "size": len(artifact_bytes)}
        ],
        "rollback": "Install the previous verified artifact.",
    }
    return payload, name, artifact_bytes


def _fetcher_for(payload, artifact_bytes: bytes, fail: bool = False):
    def fetch(url: str) -> bytes:
        if fail:
            raise OSError("network is unreachable")
        if url.endswith("update-manifest.json"):
            return json.dumps(payload).encode()
        return artifact_bytes
    return fetch


# --- manifest core hardening ---

def test_manifest_rejects_bool_size():
    payload, name, _ = _manifest(Path("."))
    payload["artifacts"][0]["size"] = True
    with pytest.raises(um.ManifestError):
        um.validate_manifest(payload)


def test_manifest_rejects_duplicate_and_escaping_names():
    payload, name, _ = _manifest(Path("."))
    payload["artifacts"].append(dict(payload["artifacts"][0]))
    with pytest.raises(um.ManifestError, match="duplicate"):
        um.validate_manifest(payload)
    payload, name, _ = _manifest(Path("."))
    payload["artifacts"][0]["name"] = "../escape.AppImage"
    with pytest.raises(um.ManifestError, match="plain file name"):
        um.validate_manifest(payload)


def test_version_compare_is_numeric_and_never_downgrades():
    assert um.is_newer_version("1.10.0", "1.9.0") is True
    assert um.is_newer_version("1.5.0", "1.5.0") is False
    assert um.is_newer_version("1.4.9", "1.5.0") is False
    assert um.update_available("1.5.0", {"version": "1.5.1"}) is True


def test_parse_manifest_rejects_garbage():
    with pytest.raises(um.ManifestError):
        um.parse_manifest(b"not json")
    with pytest.raises(um.ManifestError):
        um.parse_manifest(b'{"format": 2, "version": "1.0", "artifacts": []}')


# --- update service ---

def test_check_detects_update_and_records_session(tmp_path):
    payload, name, data = _manifest(tmp_path)
    session = us.UpdateSession()
    result = us.check_for_update("1.5.0", fetcher=_fetcher_for(payload, data),
                                 url="https://example.test/update-manifest.json", session=session)
    assert result.status == us.STATUS_UPDATE_AVAILABLE
    assert result.remote_version == "9.9.9"
    assert session.gate_status() == "update_available"


def test_check_offline_is_silent_error_not_exception(tmp_path):
    payload, name, data = _manifest(tmp_path)
    session = us.UpdateSession()
    result = us.check_for_update("1.5.0", fetcher=_fetcher_for(payload, data, fail=True),
                                 url="https://example.test/x.json", session=session)
    assert result.status == us.STATUS_ERROR
    assert session.gate_status() == "check_failed"


def test_download_verifies_sha_and_rejects_corrupt(tmp_path):
    payload, name, data = _manifest(tmp_path)
    good = us.download_artifact(payload, name, tmp_path / "dl",
                                fetcher=_fetcher_for(payload, data),
                                url="https://example.test/update-manifest.json")
    assert good.read_bytes() == data
    bad_fetcher = _fetcher_for(payload, b"corrupted bytes......")
    with pytest.raises(um.ManifestError):
        us.download_artifact(payload, name, tmp_path / "dl2",
                             fetcher=bad_fetcher,
                             url="https://example.test/update-manifest.json")


def test_appimage_apply_and_rollback_copy(tmp_path, monkeypatch):
    payload, name, data = _manifest(tmp_path)
    target = tmp_path / "Rhetoric.AppImage"
    target.write_bytes(b"old version")
    target.chmod(0o755)
    downloaded = tmp_path / name
    downloaded.write_bytes(data)
    env = {"APPIMAGE": str(target)}
    assert us.install_kind(env) == "appimage"
    rollback = us.apply_appimage_update(downloaded, environ=env)
    assert target.read_bytes() == data
    assert rollback.read_bytes() == b"old version"


def test_run_automated_update_honors_opt_out(tmp_path):
    session = us.UpdateSession()
    result = us.run_automated_update({"automatic_updates_enabled": False},
                                     current_version="1.5.0", session=session)
    assert result.status == us.STATUS_DISABLED
    assert session.gate_status() == "disabled"


def test_run_automated_update_source_install_notifies_only(tmp_path):
    payload, name, data = _manifest(tmp_path)
    session = us.UpdateSession()
    result = us.run_automated_update({"automatic_updates_enabled": True},
                                     current_version="1.5.0",
                                     fetcher=_fetcher_for(payload, data),
                                     url="https://example.test/update-manifest.json",
                                     session=session, environ={})
    assert result.status == us.STATUS_UPDATE_AVAILABLE
    assert "./rhetoric update" in result.message
    assert result.applied_artifact == ""


# --- support gate matrix ---

def test_gate_blocks_opted_out():
    result = gate.evaluate_support_gate(automatic_updates_enabled=False, update_status="current")
    assert not result.allowed
    assert "updates_disabled" in result.reasons


def test_gate_blocks_outdated_and_unchecked():
    outdated = gate.evaluate_support_gate(automatic_updates_enabled=True, update_status="update_available")
    assert not outdated.allowed and "update_pending" in outdated.reasons
    unchecked = gate.evaluate_support_gate(automatic_updates_enabled=True, update_status="not_checked")
    assert not unchecked.allowed and "not_checked" in unchecked.reasons


def test_gate_passes_opted_in_and_current():
    result = gate.evaluate_support_gate(automatic_updates_enabled=True, update_status="current")
    assert result.allowed


def test_gate_message_states_exact_remedy():
    result = gate.evaluate_support_gate(automatic_updates_enabled=False, update_status="update_available")
    text = result.message.lower()
    assert "cannot submit bug tickets" in text
    assert "turn automated updates back on" in text
    assert "fully update rhetoric" in text
    assert "automatic bug catcher" in text
