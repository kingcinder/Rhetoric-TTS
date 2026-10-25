"""Run a smoke-render script with a CI license status (CI-only wrapper).

CI has no serial number, so the production license gate would stop the render
at prepare_plan. This patches a valid status onto the same seam that
tests/conftest.py uses, then runs the target script unchanged via runpy. The
production gate in the_oracle.licensing is not modified.

Usage: python scripts/ci_smoke_render.py scripts/smoke_render.py
"""

from __future__ import annotations

import runpy
import sys

from the_oracle import licensing
from the_oracle.licensing.tokens import LicenseStatus


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        raise SystemExit("usage: ci_smoke_render.py <script.py>")
    target = argv[1]
    licensing.current_license = lambda *a, **k: LicenseStatus(
        ok=True, state="valid", licensee="CI smoke render", key_id="ci"
    )
    sys.argv = [target]
    runpy.run_path(target, run_name="__main__")


if __name__ == "__main__":
    main(sys.argv)
