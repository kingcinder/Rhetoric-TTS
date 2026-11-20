from __future__ import annotations

import ast
from pathlib import Path


def test_frozen_bundle_collects_requests_distribution_metadata() -> None:
    spec_path = Path(__file__).resolve().parents[1] / "packaging" / "linux" / "rhetoric.spec"
    tree = ast.parse(spec_path.read_text(encoding="utf-8"))
    metadata_names = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "copy_metadata"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }

    assert "requests" in metadata_names, (
        "diffusers checks requests package metadata at runtime, so the frozen "
        "bundle must include its dist-info"
    )


def test_frozen_bundle_collects_runtime_model_and_dictionary_assets() -> None:
    spec_path = Path(__file__).resolve().parents[1] / "packaging" / "linux" / "rhetoric.spec"
    tree = ast.parse(spec_path.read_text(encoding="utf-8"))
    data_packages = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "collect_data_files"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }

    assert {"perth", "symspellpy"} <= data_packages, (
        "the offline runtime needs Perth's pretrained watermark and SymSpell's "
        "dictionary data"
    )
