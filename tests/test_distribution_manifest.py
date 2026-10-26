from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_sdist_manifest_tracks_current_customer_docs_and_excludes_test_helpers() -> None:
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    assert "prune tests" in manifest
    assert "exclude scripts/ci_smoke_render.py" in manifest
    assert "include docs/SOFT_LAUNCH_PLAN.md" not in manifest
    for relative in (
        "docs/SUPPORT.md",
        "docs/release/QUICK_START.md",
        "docs/release/SYSTEM_REQUIREMENTS.md",
        "docs/release/KNOWN_ISSUES.md",
        "docs/release/PRODUCT_OFFER.md",
    ):
        assert f"include {relative}" in manifest
