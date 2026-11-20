"""Frozen Linux entry point for the desktop GUI and CLI."""

import sys
import multiprocessing
import os


def configure_frozen_numba_cache() -> None:
    # Numba sees PyInstaller's module paths as virtual files. Use its user-wide
    # locator, which keys compiled caches to the frozen executable instead.
    sys.frozen = True
    os.environ.setdefault("NUMBA_CACHE_LOCATOR_CLASSES", "UserWideCacheLocator")


def main() -> int:
    configure_frozen_numba_cache()
    multiprocessing.freeze_support()
    if len(sys.argv) > 1 and sys.argv[1] == "--rhetoric-render-subprocess":
        from rhetoric.render_subprocess import main as render_subprocess_main

        return render_subprocess_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] != "gui":
        from rhetoric.cli import main as cli_main

        return cli_main()

    from rhetoric.app_gui import launch_gui

    launch_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
