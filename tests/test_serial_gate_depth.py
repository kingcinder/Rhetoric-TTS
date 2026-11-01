"""Independent gates: export and the render child refuse without a serial.

One patched call site must not be enough. The pipeline's entry check lives in
``pipeline._require_license``; these two gates live in different modules and
call ``current_license`` directly, so disabling either one still leaves a gate
that fails closed.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from the_oracle.licensing import LicenseStatus
from the_oracle.licensing.policy import LicenseRequired

UNLICENSED_DETAIL = "No serial number is activated."


def _unlicensed(*_args: object, **_kwargs: object) -> LicenseStatus:
    return LicenseStatus(ok=False, state="no_token", detail=UNLICENSED_DETAIL)


def _valid(*_args: object, **_kwargs: object) -> LicenseStatus:
    return LicenseStatus(ok=True, state="valid", licensee="Tester")


def test_export_refuses_to_write_without_a_serial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from the_oracle.audio import export_flac

    monkeypatch.setattr("the_oracle.licensing.current_license", _unlicensed)
    target = tmp_path / "out.flac"
    with pytest.raises(LicenseRequired, match="serial number"):
        export_flac.write_flac(target, np.zeros(2205, dtype=np.float32), 22050, {})
    assert not target.exists()


def test_export_writes_when_the_serial_is_valid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from the_oracle.audio import export_flac

    monkeypatch.setattr("the_oracle.licensing.current_license", _valid)
    target = tmp_path / "out.flac"
    written = export_flac.write_flac(target, np.zeros(2205, dtype=np.float32), 22050, {})
    assert written == target
    assert target.is_file()


def test_export_stamps_the_license_id_without_touching_caller_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Leaked renders are attributable by licence id, not by customer name."""
    from the_oracle.audio import export_flac
    from the_oracle.audio.flac_tags import read_vorbis_comments

    licensed = LicenseStatus(
        ok=True,
        state="valid",
        licensee="Tester",
        lic_id="22222222-2222-4222-8222-222222222222",
    )
    monkeypatch.setattr("the_oracle.licensing.current_license", lambda *_a, **_k: licensed)
    metadata = {"TITLE": "Scene"}
    target = tmp_path / "tagged.flac"

    export_flac.write_flac(target, np.zeros(2205, dtype=np.float32), 22050, metadata)

    comments = read_vorbis_comments(target)
    assert comments["RHETORIC_LICENSE"] == [licensed.lic_id]
    assert comments["TITLE"] == ["Scene"]
    assert metadata == {"TITLE": "Scene"}


def test_render_child_refuses_without_a_serial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from the_oracle import render_subprocess

    monkeypatch.setattr("the_oracle.licensing.current_license", _unlicensed)
    job = tmp_path / "job.json"
    job.write_text("{}", encoding="utf-8")
    result = tmp_path / "result.json"

    assert render_subprocess.run_job(job, result) == 1
    payload = json.loads(result.read_text(encoding="utf-8"))
    assert payload["ok"] is False
    assert "serial number" in payload["error"]


def test_preview_child_refuses_without_a_serial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from the_oracle import render_subprocess

    monkeypatch.setattr("the_oracle.licensing.current_license", _unlicensed)
    job = tmp_path / "preview.json"
    job.write_text("{}", encoding="utf-8")
    result = tmp_path / "result.json"

    assert render_subprocess.run_preview_job(job, result) == 1
    payload = json.loads(result.read_text(encoding="utf-8"))
    assert payload["ok"] is False
    assert "serial number" in payload["error"]


def test_render_child_reaches_its_own_job_when_licensed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A licensed child fails on the malformed job, not on the gate."""
    from the_oracle import render_subprocess

    monkeypatch.setattr("the_oracle.licensing.current_license", _valid)
    job = tmp_path / "job.json"
    job.write_text("{not json", encoding="utf-8")
    result = tmp_path / "result.json"

    assert render_subprocess.run_job(job, result) == 1
    payload = json.loads(result.read_text(encoding="utf-8"))
    assert payload["ok"] is False
    assert "serial number" not in payload["error"]
