"""EULA acceptance: the record is keyed to the exact text, fails closed, and a
declined dialog records nothing."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from rhetoric import eula_acceptance  # noqa: E402


@pytest.fixture()
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # Point the packaged copy at a location with no EULA so these tests drive
    # the root-fallback text they write themselves.
    monkeypatch.setattr(eula_acceptance, "__file__", str(tmp_path / "absent" / "eula_acceptance.py"))
    (tmp_path / eula_acceptance.EULA_FILENAME).write_text("EULA v1\n", encoding="utf-8")
    return tmp_path


def test_not_accepted_without_record(root: Path) -> None:
    assert eula_acceptance.is_accepted(root) is False


def test_record_then_accepted(root: Path) -> None:
    eula_acceptance.record_acceptance(root)
    assert eula_acceptance.is_accepted(root) is True


def test_changed_eula_asks_again(root: Path) -> None:
    eula_acceptance.record_acceptance(root)
    (root / eula_acceptance.EULA_FILENAME).write_text("EULA v2\n", encoding="utf-8")
    assert eula_acceptance.is_accepted(root) is False


def test_malformed_record_fails_closed(root: Path) -> None:
    eula_acceptance.acceptance_path(root).write_text("{not json", encoding="utf-8")
    assert eula_acceptance.is_accepted(root) is False


def test_acceptance_record_with_a_utf8_bom_is_accepted(root: Path) -> None:
    """An editor that saves the record with a BOM must not revoke acceptance."""
    path = eula_acceptance.record_acceptance(root)
    path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())

    assert eula_acceptance.is_accepted(root) is True


def test_wrong_shape_fails_closed(root: Path) -> None:
    eula_acceptance.acceptance_path(root).write_text(json.dumps(["x"]), encoding="utf-8")
    assert eula_acceptance.is_accepted(root) is False


def test_missing_eula_is_never_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(eula_acceptance, "__file__", str(tmp_path / "absent" / "eula_acceptance.py"))
    assert eula_acceptance.is_accepted(tmp_path) is False
    with pytest.raises(FileNotFoundError):
        eula_acceptance.record_acceptance(tmp_path)


def test_packaged_eula_matches_root_copy() -> None:
    """The copy shipped inside the package must equal the repo-root EULA."""
    packaged = eula_acceptance.eula_path(REPO_ROOT / "nonexistent")
    assert packaged.parent == REPO_ROOT / "src" / "rhetoric"
    assert packaged.read_bytes() == (REPO_ROOT / "EULA.md").read_bytes()


def test_record_stores_digest_of_current_text(root: Path) -> None:
    path = eula_acceptance.record_acceptance(root)
    stored = json.loads(path.read_text(encoding="utf-8"))
    _text, digest = eula_acceptance.eula_text_and_digest(root)
    assert stored["eula_sha256"] == digest
    assert os.path.exists(path)


def test_frozen_bundle_eula_found_via_meipass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """In a PyInstaller build __file__ is a pseudo-path; the bundle base
    (sys._MEIPASS) is where the collected EULA text actually lives."""
    import hashlib

    bundle = tmp_path / "bundle"
    (bundle / "rhetoric").mkdir(parents=True)
    (bundle / "rhetoric" / eula_acceptance.EULA_FILENAME).write_text("Frozen EULA\n", encoding="utf-8")
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle), raising=False)
    monkeypatch.setattr(eula_acceptance, "__file__", str(tmp_path / "archive" / "eula_acceptance.py"))
    current = eula_acceptance.eula_text_and_digest(tmp_path / "nowhere")
    assert current is not None
    text, digest = current
    assert text == "Frozen EULA\n"
    assert digest == hashlib.sha256(b"Frozen EULA\n").hexdigest()
