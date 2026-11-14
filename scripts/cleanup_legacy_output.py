#!/usr/bin/env python3
"""Move legacy render working material out of output folders.

Before 1.5.0, a render wrote ``cache/``, ``logs/``, ``stems/``, ``previews/``
and ``render_plan.json`` next to the finished audio. New renders keep that
material in the app's render-work home, so the output folder receives only the
finished FLAC. This tool sweeps the old copies from the repository ``Output/``
folder and the pre-rename ``Documents/the oracle tts/Output`` folder into
``<render-work>/legacy-import/``; finished audio, project files and anything
else are left untouched.

Dry run by default: nothing moves until ``--apply`` is passed. Existing
destinations are never overwritten -- the item is skipped and reported. Every
move is appended to ``RESTORE_LOG.jsonl`` in the destination with absolute
source and destination paths, so it can be reversed by hand
(``mv DESTINATION SOURCE``). Close the GUI first; it may hold files open.

Examples::

    python scripts/cleanup_legacy_output.py                 # show the plan
    python scripts/cleanup_legacy_output.py --apply         # move
    python scripts/cleanup_legacy_output.py \
        --source ~/some/Output --dest /tmp/render-work --apply
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORK_MATERIAL = ("cache", "logs", "stems", "previews", "render_plan.json")
RESTORE_LOG = "RESTORE_LOG.jsonl"


def default_sources() -> list[Path]:
    """The two output folders this sweep was written for, in order."""
    return [
        REPO_ROOT / "Output",
        Path.home() / "Documents" / "the oracle tts" / "Output",
    ]


def destination_for(source: Path, destination: Path) -> Path:
    """A per-source subfolder so two ``Output`` trees cannot collide."""
    label = f"{source.parent.name or 'output'}-{source.name}"
    safe = "".join(c if c.isalnum() or c in {"-", "_", "."} else "_" for c in label)
    return destination / safe.strip("_") or destination / "output"


def sweep(sources: list[Path], destination: Path, apply: bool) -> list[dict[str, str]]:
    """Move allowlisted working material; return one record per action.

    Each record has ``action`` (moved/skipped), ``source`` and ``destination``.
    """
    records: list[dict[str, str]] = []
    destination = destination.expanduser().resolve()
    for source in sources:
        source = source.expanduser().resolve()
        if not source.is_dir():
            continue
        for name in WORK_MATERIAL:
            item = source / name
            if not item.exists():
                continue
            target = destination_for(source, destination) / name
            if target.exists():
                records.append(
                    {"action": "skipped", "source": str(item), "destination": str(target)}
                )
                continue
            if apply:
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.move(str(item), str(target))
                except OSError as error:
                    records.append(
                        {
                            "action": "failed",
                            "source": str(item),
                            "destination": str(target),
                            "error": str(error),
                        }
                    )
                    continue
                with (destination / RESTORE_LOG).open("a", encoding="utf-8") as log:
                    log.write(
                        json.dumps(
                            {
                                "moved_at": datetime.now(timezone.utc).isoformat(),
                                "source": str(item),
                                "destination": str(target),
                            }
                        )
                        + "\n"
                    )
            records.append(
                {"action": "moved" if apply else "would-move", "source": str(item), "destination": str(target)}
            )
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--source",
        action="append",
        type=Path,
        default=None,
        help="Output folder to sweep (repeatable; defaults to the repository Output/ "
        "and ~/Documents/the oracle tts/Output).",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="Where to move the material (default: the app's render-work/legacy-import).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Move the files. Without this the tool only prints the plan.",
    )
    args = parser.parse_args(argv)

    destination = args.dest
    if destination is None:
        from rhetoric.app_paths import render_work_dir

        destination = render_work_dir() / "legacy-import"
    sources = args.source if args.source else default_sources()

    existing = [path for path in sources if path.expanduser().is_dir()]
    if not existing:
        print("No source output folders found; nothing to do.", file=sys.stderr)
        return 0

    records = sweep(existing, destination, args.apply)
    moved = [record for record in records if record["action"] in {"moved", "would-move"}]
    skipped = [record for record in records if record["action"] == "skipped"]
    failed = [record for record in records if record["action"] == "failed"]

    if not args.apply:
        print("DRY RUN (nothing moved; pass --apply to move)")
    for record in records:
        print(f"  {record['action']}: {record['source']} -> {record['destination']}")
        if record.get("error"):
            print(f"    error: {record['error']}")
    print(
        f"{len(moved)} item(s) {'moved' if args.apply else 'to move'}, "
        f"{len(skipped)} skipped (destination exists), {len(failed)} failed."
    )
    if args.apply and moved:
        print(f"Restore log: {destination.expanduser().resolve() / RESTORE_LOG}")
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
