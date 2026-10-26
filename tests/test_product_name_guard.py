from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
PUBLIC_TEXT = re.compile(r"\bThe Oracle\b|\bOracle TTS\b|Oracle alpha license", re.IGNORECASE)


def _customer_text_files() -> list[Path]:
    paths = [*ROOT.joinpath("src").rglob("*.py")]
    paths.extend(
        ROOT / relative
        for relative in (
            "README.md",
            "PRIVACY.md",
            "EULA-DRAFT.md",
            "THIRD_PARTY_NOTICES.md",
            "docs/SUPPORT.md",
            "docs/UPGRADING.md",
            "docs/TROUBLESHOOTING.md",
            "docs/SOFT_LAUNCH.md",
            "docs/LICENSING_OPS.md",
            "docs/release/QUICK_START.md",
            "docs/release/SYSTEM_REQUIREMENTS.md",
            "docs/release/KNOWN_ISSUES.md",
        )
    )
    paths.extend(path for path in ROOT.joinpath("packaging").rglob("*") if path.is_file())
    paths.extend(path for path in ROOT.glob("*.sh") if path.is_file())
    paths.extend(path for path in ROOT.glob("*.ps1") if path.is_file())
    return sorted(set(paths))


def test_customer_facing_text_uses_rhetoric_brand() -> None:
    findings: list[str] = []
    for path in _customer_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if PUBLIC_TEXT.search(line):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}: {line.strip()}")
    assert not findings, "Customer-facing Oracle branding remains:\n" + "\n".join(findings)


def test_python_string_literals_do_not_expose_the_former_product_name() -> None:
    import ast

    findings: list[str] = []
    for path in ROOT.joinpath("src").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        docstrings: set[int] = set()
        for parent in ast.walk(tree):
            if isinstance(parent, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and parent.body:
                first = parent.body[0]
                if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                    docstrings.add(id(first.value))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
                # These are persistent internal marker/command names, not product copy.
                if node.value in {"the-oracle", ".oracle-portable"} or node.value.startswith((".oracle-render-", ".oracle-preview-")):
                    continue
                if re.search(r"\bOracle\b", node.value, re.IGNORECASE):
                    findings.append(f"{path.relative_to(ROOT)}:{node.lineno}: {node.value}")
    assert not findings, "Customer-visible Oracle strings remain:\n" + "\n".join(findings)
