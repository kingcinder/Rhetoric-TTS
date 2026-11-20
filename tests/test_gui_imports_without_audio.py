from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_importing_gui_does_not_initialize_microphone_backend() -> None:
    repo = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo / "src")
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import rhetoric.app_gui; "
            "assert 'sounddevice' not in sys.modules",
        ],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        timeout=12,
        check=False,
    )

    assert result.returncode == 0, result.stderr
