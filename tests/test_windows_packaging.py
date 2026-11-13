"""Windows packaging: the frozen bundle must carry its EULA text, and the
installer must behave like a regular Windows program.

Regression guard for the 2026-11-12 guest diagnosis: the Windows build
collected no package data, so the installed bundle contained no EULA.md
anywhere. The first-run EULA lookup returned None, the acceptance dialog
function returned False without ever showing a dialog, and Rhetoric.exe
exited silently ~3s after launch on a fresh profile. Copying EULA.md into
the install root made the same exe open the license dialog and stay
alive, proving the missing data file was the whole failure.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_windows_build_collects_package_data_and_root_eula() -> None:
    build = (REPO_ROOT / "packaging" / "windows" / "build.ps1").read_text(encoding="utf-8")
    # The Linux spec's collect_data_files("the_oracle") is where the
    # packaged EULA.md comes from; the Windows build must mirror it.
    assert "--collect-data" in build and "the_oracle" in build
    # The spec's root-level docs, including the fallback EULA copy.
    for doc in ("LICENSE", "PRIVACY.md", "EULA.md", "THIRD_PARTY_NOTICES.md"):
        assert doc in build
    # A bundle without the EULA text must fail the build, not ship.
    assert "EULA.md" in build and "missing" in build


def test_windows_installer_is_a_regular_program_installer() -> None:
    iss = (REPO_ROOT / "packaging" / "windows" / "Rhetoric.iss").read_text(encoding="utf-8")
    # No blocking custom popup: it hung even /VERYSILENT installs.
    assert "InitializeSetup" not in iss
    assert "MsgBox" not in iss
    # No EXPERIMENTAL branding in customer-visible names.
    assert "EXPERIMENTAL" not in iss
    assert 'DefaultGroupName=Rhetoric' in iss
    # EULA acceptance belongs on the standard Inno license page, and the
    # installer records that acceptance for the app (build.ps1 passes the
    # digest of the exact EULA text).
    assert "LicenseFile=" in iss
    assert "EulaSha256" in iss
    assert "eula_acceptance.json" in iss
