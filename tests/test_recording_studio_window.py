from __future__ import annotations

import os
import subprocess
import sys
import textwrap


def test_recording_studio_is_a_maximizable_top_level_window(tmp_path):
    script = textwrap.dedent(
        """\
        import sys
        from pathlib import Path
        from types import ModuleType

        sys.modules["sounddevice"] = ModuleType("sounddevice")
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication, QWidget
        from rhetoric.gui_recording import RecordingStudioDialog

        root = Path(sys.argv[1])
        voices, inputs = root / "Seashells", root / "Input"
        voices.mkdir(parents=True)
        inputs.mkdir()
        app = QApplication.instance() or QApplication([])
        parent = QWidget()
        dialog = RecordingStudioDialog(root, voices, inputs, parent=parent)
        try:
            assert dialog.windowFlags() & Qt.WindowType.WindowType_Mask == Qt.WindowType.Window
            assert dialog.windowFlags() & Qt.WindowType.WindowMaximizeButtonHint
            available = app.primaryScreen().availableGeometry()
            dialog.showMaximized()
            app.processEvents()
            assert dialog.isMaximized()
            assert dialog.frameGeometry().size() == available.size()
        finally:
            dialog.close()
            parent.close()
        """
    )
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_recording_studio_reads_live_input_files_on_each_open(tmp_path):
    script = textwrap.dedent(
        """\
        import sys
        from pathlib import Path
        from types import ModuleType

        sys.modules["sounddevice"] = ModuleType("sounddevice")
        from PySide6.QtWidgets import QApplication
        from rhetoric.app_paths import resolve_default_input_dir
        from rhetoric.gui_recording import RecordingStudioDialog

        root = Path(sys.argv[1])
        repo = root / "repo"
        repo_input = repo / "Input"
        app_input = root / "appdata" / "Input"
        repo_input.mkdir(parents=True)
        app_input.mkdir(parents=True)
        (repo / "pyproject.toml").touch()
        (app_input / "deleted-from-repo.txt").write_text("stale", encoding="utf-8")
        remembered = app_input / "remaining.txt"
        remembered.write_text("stale remembered copy", encoding="utf-8")
        (repo_input / "README.md").write_text("Input instructions", encoding="utf-8")
        script_path = repo_input / "remaining.txt"
        script_path.write_text("first version", encoding="utf-8")
        selected_input = resolve_default_input_dir(app_input, app_input, repo)
        assert selected_input == repo_input

        app = QApplication.instance() or QApplication([])
        first = RecordingStudioDialog(repo, root / "Seashells", selected_input)
        try:
            first.apply_setup_preferences({"input_file": str(remembered)})
            names = [first.script_combo.itemText(i) for i in range(first.script_combo.count())]
            assert names == ["<no script - type your own lines>", "remaining.txt"]
            assert first.script_combo.currentData() == str(script_path)
            assert first.prompt_area.toPlainText() == "first version"
        finally:
            first.close()

        script_path.write_text("edited after closing", encoding="utf-8")
        second = RecordingStudioDialog(repo, root / "Seashells", selected_input)
        try:
            second.apply_setup_preferences({"input_file": str(remembered)})
            assert second.script_combo.currentData() == str(script_path)
            assert second.prompt_area.toPlainText() == "edited after closing"
        finally:
            second.close()
        """
    )
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
