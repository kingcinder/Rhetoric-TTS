"""Validate a static update manifest without downloading or replacing files.

Thin CLI over :mod:`rhetoric.update_manifest` — the shared validation
core the in-app updater also uses, so release-side and app-side checks
can never drift apart.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from rhetoric.update_manifest import (
        ManifestError,
        load_manifest,
        update_available,
        verify_artifact,
    )
except ImportError:  # source checkout without the package installed
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from rhetoric.update_manifest import (
        ManifestError,
        load_manifest,
        update_available,
        verify_artifact,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--artifact-dir", type=Path, default=None)
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--current-version", default=None)
    args = parser.parse_args(argv)
    try:
        payload = load_manifest(args.manifest)
        if args.current_version is not None:
            print("update available" if update_available(args.current_version, payload) else "already current")
        if args.artifact is not None:
            if args.artifact_dir is None:
                parser.error("--artifact-dir is required with --artifact")
            verify_artifact(payload, args.artifact_dir, args.artifact)
            print(f"verified: {args.artifact}")
        print(json.dumps({"version": payload["version"], "rollback": payload.get("rollback", "")}, indent=2))
        return 0
    except ManifestError as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
