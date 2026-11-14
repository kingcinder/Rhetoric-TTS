"""The legacy output sweep moves working material, never audio, never overwrites."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cleanup_legacy_output.py"


def _tool():
    spec = importlib.util.spec_from_file_location("cleanup_legacy_output", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _legacy_output(root: Path) -> Path:
    output = root / "Output"
    (output / "cache").mkdir(parents=True)
    (output / "cache" / "segment.bin").write_bytes(b"cache")
    (output / "logs").mkdir()
    (output / "logs" / "render.log").write_text("log", encoding="utf-8")
    (output / "stems").mkdir()
    (output / "stems" / "stem.wav").write_bytes(b"wav")
    (output / "render_plan.json").write_text("{}", encoding="utf-8")
    (output / "take.flac").write_bytes(b"audio")
    (output / "notes.txt").write_text("keep", encoding="utf-8")
    return output


def test_dry_run_prints_the_plan_and_moves_nothing(tmp_path: Path) -> None:
    tool = _tool()
    output = _legacy_output(tmp_path)
    destination = tmp_path / "render-work"

    assert tool.main(["--source", str(output), "--dest", str(destination)]) == 0

    assert (output / "cache" / "segment.bin").exists()
    assert (output / "render_plan.json").exists()
    assert not destination.exists()


def test_apply_moves_only_working_material_and_writes_a_restore_log(tmp_path: Path) -> None:
    tool = _tool()
    output = _legacy_output(tmp_path)
    destination = tmp_path / "render-work"

    assert tool.main(["--source", str(output), "--dest", str(destination), "--apply"]) == 0

    moved = tool.destination_for(output, destination)
    assert (moved / "cache" / "segment.bin").read_bytes() == b"cache"
    assert (moved / "stems" / "stem.wav").exists()
    assert (moved / "render_plan.json").exists()
    assert not (output / "cache").exists()
    # Finished audio and unrelated files stay in the output folder.
    assert (output / "take.flac").read_bytes() == b"audio"
    assert (output / "notes.txt").read_text(encoding="utf-8") == "keep"

    entries = [
        json.loads(line)
        for line in (destination / "RESTORE_LOG.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert {Path(entry["source"]).name for entry in entries} == {
        "cache",
        "logs",
        "stems",
        "render_plan.json",
    }
    for entry in entries:
        assert Path(entry["destination"]).exists()
        assert not Path(entry["source"]).exists()


def test_a_second_apply_never_overwrites_and_stays_a_no_op(tmp_path: Path) -> None:
    tool = _tool()
    output = _legacy_output(tmp_path)
    destination = tmp_path / "render-work"

    assert tool.main(["--source", str(output), "--dest", str(destination), "--apply"]) == 0
    log = (destination / "RESTORE_LOG.jsonl").read_text(encoding="utf-8")

    # Recreate one item with different bytes; the existing destination wins.
    (output / "cache").mkdir()
    (output / "cache" / "new.bin").write_bytes(b"new")
    assert tool.main(["--source", str(output), "--dest", str(destination), "--apply"]) == 0

    assert (output / "cache" / "new.bin").exists()
    assert (destination / "RESTORE_LOG.jsonl").read_text(encoding="utf-8") == log
