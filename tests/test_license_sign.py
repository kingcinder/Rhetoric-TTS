"""The vendor signing utility must stay outside the repository and wheel."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_vendor_signer_is_not_in_the_repository() -> None:
    assert not (REPO_ROOT / "scripts" / "license_sign.py").exists()


def test_scripts_are_not_packaged_into_the_wheel() -> None:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.setuptools]" in pyproject
    for line in pyproject.splitlines():
        assert not (line.strip().startswith("packages") and "scripts" in line), line

    wheels = sorted((REPO_ROOT / "release_artifacts").glob("*.whl"))
    for wheel in wheels:
        import zipfile

        with zipfile.ZipFile(wheel) as archive:
            assert not any(name.startswith("scripts/") or "/scripts/" in name for name in archive.namelist()), wheel.name
