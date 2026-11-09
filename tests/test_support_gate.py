"""Support-gate enforcement at the submission boundary (headless, no Qt).

The pure verdict matrix lives in tests/test_update_service.py; here the
session-aware helper is pinned: it must not fetch when the session is
already conclusive, must fetch once when it is not, and must block when
the user opted out (without fetching at all).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from the_oracle import gui_settings, update_service
from the_oracle.support import gate


@pytest.fixture()
def settings_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    target = tmp_path / "app-settings.json"
    monkeypatch.setattr(gui_settings, "app_settings_path", lambda: target)
    return target


@pytest.fixture()
def session(monkeypatch: pytest.MonkeyPatch) -> update_service.UpdateSession:
    fresh = update_service.UpdateSession()
    monkeypatch.setattr(update_service, "SESSION", fresh)
    return fresh


def _record(session: update_service.UpdateSession, status: str) -> None:
    session.record(update_service.UpdateCheckResult(status=status, current_version="1.5.0"))


def test_block_helper_allows_current_session_without_fetching(settings_file, session, monkeypatch):
    _record(session, "current")
    calls: list[int] = []
    monkeypatch.setattr(update_service, "check_for_update", lambda **kw: calls.append(1))
    verdict = gate.support_submission_block()
    assert verdict.allowed
    assert calls == []


def test_block_helper_blocks_opt_out_without_fetching(settings_file, session, monkeypatch):
    gui_settings.save_app_settings({"automatic_updates_enabled": False})
    _record(session, "current")
    calls: list[int] = []
    monkeypatch.setattr(update_service, "check_for_update", lambda **kw: calls.append(1))
    verdict = gate.support_submission_block()
    assert not verdict.allowed
    assert "updates_disabled" in verdict.reasons
    assert calls == []


def test_block_helper_checks_once_when_session_inconclusive(settings_file, session, monkeypatch):
    def fake_check(**kw):
        return _record(session, "current") or update_service.UpdateCheckResult(
            status="current", current_version="1.5.0")

    monkeypatch.setattr(update_service, "check_for_update", fake_check)
    verdict = gate.support_submission_block()
    assert verdict.allowed


def test_block_helper_blocks_when_fresh_check_finds_update(settings_file, session, monkeypatch):
    def fake_check(**kw):
        session.record(update_service.UpdateCheckResult(
            status="update_available", current_version="1.5.0", remote_version="9.9.9"))
        return session.last_result

    monkeypatch.setattr(update_service, "check_for_update", fake_check)
    verdict = gate.support_submission_block()
    assert not verdict.allowed
    assert "update_pending" in verdict.reasons
