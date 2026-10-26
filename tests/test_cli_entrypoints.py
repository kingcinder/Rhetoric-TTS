from __future__ import annotations

import tomllib
from pathlib import Path


def test_rhetoric_and_legacy_entrypoints_share_cli_target() -> None:
    project = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = project["project"]["scripts"]
    assert project["project"]["name"] == "rhetoric"
    assert scripts["rhetoric"] == "the_oracle.cli:main"
    assert scripts["the-oracle"] == scripts["rhetoric"]


def test_render_report_help_does_not_refer_to_a_superseded_edition(capsys) -> None:
    import pytest

    from the_oracle import cli

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--help"])
    assert exit_info.value.code == 0
    output = capsys.readouterr().out
    assert "Studio:" not in output
