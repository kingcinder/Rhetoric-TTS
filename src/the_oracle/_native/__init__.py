"""Compiled license-verification core (see docs/LICENSING_DESIGN.md §10).

The extension module ``rhetoric_native`` is compiled from
``crates/rhetoric_native`` by ``scripts/build_native_license.py`` and installed
beside this file. Importing this package never raises and never runs at
``the_oracle.licensing`` import time: :func:`load` is called lazily by
``tokens.verify_token`` so a checkout that has not built the core keeps working
through the pure-Python reference implementation.

This is a cost barrier, not a trust boundary. Whoever can edit the install can
replace this module — what the compiled core buys is that a bypass is no longer
a one-line edit to readable Python, and that it must be rediscovered for every
release build.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from types import ModuleType

#: The extension's import path. Kept as a module (not a bare import) so a
#: missing build is an ordinary ``ImportError`` rather than a startup failure.
_MODULE_NAME = "the_oracle._native.rhetoric_native"

_loaded = False
_core: ModuleType | None = None


def load() -> ModuleType | None:
    """The compiled core, or ``None`` when this checkout has not built it."""
    global _loaded, _core
    if _loaded:
        return _core
    _loaded = True
    try:
        _core = importlib.import_module(_MODULE_NAME)
    except (ImportError, OSError):
        _core = None
    return _core


def available() -> bool:
    """True when the compiled core is importable in this environment."""
    return load() is not None


def accepts_test_keys() -> bool:
    """True for development builds, which mirror the injected key registry.

    Release builds compile the flag off and trust only their embedded
    production keys, so this is never true for a shipped artifact.
    """
    core = load()
    return bool(core is not None and getattr(core, "TEST_KEYS_ACCEPTED", False))


def attest(package_root: str | Path) -> dict[str, object] | None:
    """Check the installed modules against the manifest compiled into the core.

    Returns ``None`` when no core is built, otherwise the native verdict:
    ``{"enforced", "ok", "checked", "mismatched"}``. ``enforced=False`` means
    this artifact carries no manifest (a development build); it is never
    evidence that the files are clean.
    """
    core = load()
    if core is None:
        return None
    return core.attest(str(package_root))


def attestation_enforced() -> bool:
    """True when this artifact was built with an integrity manifest."""
    core = load()
    return bool(core is not None and getattr(core, "ATTESTATION_ENFORCED", False))
