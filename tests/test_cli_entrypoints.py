from __future__ import annotations

import tomllib
from pathlib import Path


def test_rhetoric_and_legacy_entrypoints_share_cli_target() -> None:
    project = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = project["project"]["scripts"]
    assert scripts["rhetoric"] == "the_oracle.cli:main"
    assert scripts["the-oracle"] == scripts["rhetoric"]
