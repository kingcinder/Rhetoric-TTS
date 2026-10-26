from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).parents[1]
SHIMS = {
    "oracle": "rhetoric",
    "oracle.ps1": "rhetoric.ps1",
    "bootstrap_oracle_tts.sh": "bootstrap_rhetoric.sh",
    "doctor_oracle_tts.sh": "doctor_rhetoric.sh",
    "install_oracle_tts.sh": "install_rhetoric.sh",
    "run_oracle_tts.sh": "run_rhetoric.sh",
    "uninstall_oracle_tts.sh": "uninstall_rhetoric.sh",
    "bootstrap_oracle_tts.ps1": "bootstrap_rhetoric.ps1",
    "doctor_oracle_tts.ps1": "doctor_rhetoric.ps1",
    "install_oracle_tts.ps1": "install_rhetoric.ps1",
    "run_oracle_tts.ps1": "run_rhetoric.ps1",
    "uninstall_oracle_tts.ps1": "uninstall_rhetoric.ps1",
}


def test_legacy_launcher_and_installer_names_forward_with_notice() -> None:
    for legacy, current in SHIMS.items():
        source = ROOT / legacy
        assert source.is_file(), f"missing legacy shim: {legacy}"
        text = source.read_text(encoding="utf-8")
        assert current in text, f"{legacy} does not forward to {current}"
        assert "legacy" in text.lower(), f"{legacy} has no compatibility notice"



def test_powershell_wrapper_dispatches_when_python_is_only_a_single_command(tmp_path: Path) -> None:
    """The fallback candidate is a scalar in PowerShell and must not be indexed as a string."""
    import os
    import shutil
    import subprocess
    import sys

    import pytest

    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if powershell is None:
        pytest.skip("PowerShell is unavailable")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python").symlink_to(sys.executable)
    result = subprocess.run(
        [powershell, "-NoProfile", "-File", str(ROOT / "bootstrap_rhetoric.ps1"), "--help"],
        cwd=ROOT,
        env={**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "usage: manage_install.py bootstrap" in result.stdout
