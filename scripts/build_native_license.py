#!/usr/bin/env python3
"""Build the compiled license core and install it beside the licensing package.

The Rust crate lives in ``crates/rhetoric_native``; ``rhetoric._native`` loads
the artifact as ``rhetoric_native``. Two build kinds exist:

* ``--dev`` (the default) compiles with ``--features test-keys``, which embeds
  the published RFC 8032 test key and mirrors the key registry the test suite
  injects. This is what local checkouts and CI use.
* ``--release`` compiles without that feature: the artifact trusts only the
  compiled-in production key and ignores any caller-supplied key table. This is
  the artifact that ships.

Run it after touching the crate's sources; nothing else in the build does.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CRATE_DIR = REPO_ROOT / "crates" / "rhetoric_native"
PACKAGE_DIR = REPO_ROOT / "src" / "rhetoric" / "_native"

#: Modules whose bytes are hashed into the compiled manifest. They are the
#: files that carry the license gates themselves: patching a gate changes a
#: protected file, and an unattested build refuses to report a valid serial.
PROTECTED_MODULES: tuple[str, ...] = (
    "licensing/__init__.py",
    "licensing/keys.py",
    "licensing/machine.py",
    "licensing/policy.py",
    "licensing/store.py",
    "licensing/tokens.py",
    "audio/export_flac.py",
    "cli.py",
    "pipeline.py",
    "render_subprocess.py",
)

#: Library basename cargo produces per platform, and the import suffix Python
#: accepts for an abi3 extension on that platform.
ARTIFACTS = {
    "linux": ("librhetoric_native.so", "rhetoric_native.abi3.so"),
    "darwin": ("librhetoric_native.dylib", "rhetoric_native.abi3.so"),
    "win32": ("rhetoric_native.dll", "rhetoric_native.pyd"),
}


def _platform() -> str:
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "darwin"
    if sys.platform in {"win32", "cygwin"}:
        return "win32"
    raise SystemExit(f"unsupported platform for the license core: {sys.platform}")


def _artifact_names() -> tuple[str, str]:
    return ARTIFACTS[_platform()]


def write_manifest(package_root: Path, output: Path) -> Path:
    """Write a sha256sum-style manifest for :data:`PROTECTED_MODULES`.

    ``package_root`` is the installed ``rhetoric`` directory. Entries are
    relative to it because the runtime hands that same directory to the core,
    which reads and hashes the files itself — a patched install cannot simply
    report the digests it prefers.
    """
    missing = [relative for relative in PROTECTED_MODULES if not (package_root / relative).is_file()]
    if missing:
        raise SystemExit(
            "cannot attest a package missing protected modules: " + ", ".join(missing)
        )
    lines = []
    for relative in PROTECTED_MODULES:
        digest = hashlib.sha256((package_root / relative).read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}\n")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(lines), encoding="utf-8", newline="\n")
    return output


def build(*, release: bool, attest: bool) -> Path:
    """Compile the crate and copy the library into the Python package."""
    cargo = shutil.which("cargo")
    if cargo is None:
        raise SystemExit(
            "cargo was not found on PATH. Install a Rust toolchain "
            "(https://rustup.rs) or skip this step: the pure-Python verifier "
            "remains the fallback."
        )
    command = [cargo, "build", "--locked"]
    if release:
        command.append("--release")
    else:
        command += ["--features", "test-keys"]
    source_name, target_name = _artifact_names()
    profile_dir = "release" if release else "debug"
    artifact = CRATE_DIR / "target" / profile_dir / source_name
    environment = os.environ.copy()
    manifest: Path | None = None
    if attest:
        manifest = write_manifest(
            REPO_ROOT / "src" / "rhetoric",
            CRATE_DIR / "target" / "integrity-manifest.txt",
        )
        environment["RHETORIC_ATTEST_MANIFEST"] = str(manifest)
    else:
        # Never inherit a manifest from an outer build: an unattested artifact
        # must not pick up enforcement left behind by an earlier one.
        environment.pop("RHETORIC_ATTEST_MANIFEST", None)

    print(" ".join(command), flush=True)
    result = subprocess.run(command, cwd=CRATE_DIR, check=False, env=environment)
    if result.returncode != 0:
        raise SystemExit(f"cargo build failed with exit code {result.returncode}")
    if not artifact.is_file():
        raise SystemExit(f"cargo build succeeded but produced no {artifact}")

    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    destination = PACKAGE_DIR / target_name
    shutil.copy2(artifact, destination)
    # Remove the other platform's stale artifact if this checkout ever saw one.
    for _, name in ARTIFACTS.values():
        stale = PACKAGE_DIR / name
        if stale != destination and stale.exists():
            stale.unlink()
    attested = (
        f", {len(PROTECTED_MODULES)} modules attested" if manifest is not None else ", no attestation"
    )
    print(
        f"installed {destination.relative_to(REPO_ROOT)} "
        f"({'release' if release else 'dev'} build{attested})"
    )
    return destination


def status() -> int:
    """Report what is installed without rebuilding; 0 when an artifact exists."""
    _, target_name = _artifact_names()
    artifact = PACKAGE_DIR / target_name
    if not artifact.is_file():
        print("no compiled license core installed (pure-Python fallback active)")
        return 1
    print(f"compiled license core installed: {artifact.relative_to(REPO_ROOT)}")
    try:
        sys.path.insert(0, str(REPO_ROOT / "src"))
        from rhetoric import _native

        if _native.attestation_enforced():
            print("attestation: enforced")
        else:
            print("attestation: not enforced (development build)")
    except Exception as error:  # pragma: no cover - diagnostic only
        print(f"attestation: unknown ({type(error).__name__}: {error})")
    newest_source = max(
        [path.stat().st_mtime for path in (CRATE_DIR / "src").rglob("*.rs")]
        + [CRATE_DIR.joinpath("Cargo.toml").stat().st_mtime]
    )
    if artifact.stat().st_mtime < newest_source:
        print("stale: crate sources are newer than the installed artifact")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--release",
        action="store_true",
        help="build the shippable artifact (production keys only, no test key)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report whether the installed artifact is present and current",
    )
    parser.add_argument(
        "--attest",
        dest="attest",
        action="store_true",
        default=None,
        help="compile in the SHA-256 manifest of the protected modules (default for --release)",
    )
    parser.add_argument(
        "--no-attest",
        dest="attest",
        action="store_false",
        help="build without a manifest, disabling integrity enforcement",
    )
    args = parser.parse_args(argv)
    if args.check:
        return status()
    attest = args.release if args.attest is None else args.attest
    if args.release and not attest:
        print(
            "warning: this release build carries no integrity manifest, so it "
            "will not enforce attestation",
            file=sys.stderr,
        )
    build(release=args.release, attest=attest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
