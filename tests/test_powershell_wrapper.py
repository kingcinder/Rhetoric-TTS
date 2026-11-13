from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).parents[1]


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
