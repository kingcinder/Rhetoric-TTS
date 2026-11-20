from __future__ import annotations

import os
import ast
import subprocess
import sys
from pathlib import Path


def test_frozen_entrypoint_honors_pyinstaller_multiprocessing_children() -> None:
    repo = Path(__file__).resolve().parents[1]
    tree = ast.parse((repo / "packaging" / "linux" / "entrypoint.py").read_text(encoding="utf-8"))
    main_function = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    first_statement = main_function.body[0]

    assert isinstance(first_statement, ast.Expr)
    assert isinstance(first_statement.value, ast.Call)
    assert isinstance(first_statement.value.func, ast.Attribute)
    assert isinstance(first_statement.value.func.value, ast.Name)
    assert first_statement.value.func.value.id == "multiprocessing"
    assert first_statement.value.func.attr == "freeze_support"


def test_frozen_entrypoint_routes_cli_arguments_without_starting_gui() -> None:
    repo = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo / "src")
    env.pop("DISPLAY", None)
    env["QT_QPA_PLATFORM"] = "xcb"

    try:
        result = subprocess.run(
            [sys.executable, str(repo / "packaging" / "linux" / "entrypoint.py"), "--help"],
            cwd=repo,
            env=env,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except subprocess.TimeoutExpired:
        result = None

    assert result is not None, "CLI arguments started the GUI event loop"
    assert result.returncode == 0
    assert "usage: rhetoric" in result.stdout
    assert "could not connect to display" not in result.stderr
