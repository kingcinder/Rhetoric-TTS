"""Frozen Linux entry point for the desktop GUI and CLI."""

import sys
import multiprocessing


def main() -> int:
    multiprocessing.freeze_support()
    if len(sys.argv) > 1 and sys.argv[1] != "gui":
        from rhetoric.cli import main as cli_main

        return cli_main()

    from rhetoric.app_gui import launch_gui

    launch_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
