# V1.00a updater and license-path audit — 2026-11-17

Scope: the exact Ubuntu 24.04 amd64 RC1 archive at source anchor
`32ac9df7200e5fedf04dfd01c0edb55be642dd50`. The archive is 4,742,706,176
bytes with SHA-256
`00e0caa5a15af0757e56e69a5baf5d19044ab13b5a0d18cb7f729d04294f4b28`; its
embedded `.deb` SHA-256 is
`51cd9f263f4d5f134c8da3ee2ab98ca39fc9e43cd2617383556916d64a994931`.
This is a source/path review, not a claim that all packaging variants are
secure.

## Update path

The kit installs `kit/rhetoric_1.5.0_amd64.deb`, a frozen `amd64` package. In
`src/rhetoric/update_service.py`, `run_automated_update()` only self-applies
when `install_kind()` returns `appimage`. Frozen installs receive a message to
download the release and update explicitly. The candidate contains no
AppImage, so its startup check cannot silently replace the installed package.
The manifest's size and SHA-256 checks provide integrity relative to that
manifest, but do not authenticate its publisher. The separate AppImage
self-apply route therefore must not be treated as authenticated by those
checks; it is outside this `.deb` candidate's install path.

Evidence: source review of `src/rhetoric/update_service.py` and
`src/rhetoric/update_manifest.py`; `tests/test_update_service.py` and
`tests/test_update_manifest.py` — **17 passed**. Rechecked the archive SHA,
the embedded package SHA, `zstd -t`, and all 131 tar entries; no absolute or
parent-traversal paths, links, devices, or FIFOs were present. The exact
archive contains no AppImage entry. No updater code changed, so RC1 bytes
remain unchanged.

## Offline activation

Release builds compile the native licensing core without the `test-keys`
feature (`scripts/build_native_license.py --release`). The production registry
in `src/rhetoric/licensing/keys.py` contains only production key `k2`. The
published test-vector key is injected by test fixtures and explicitly excluded
from release builds; a test-only token cannot activate this exact candidate.
No serial enforcement was modified or bypassed. Consequently, the exact
candidate's legitimate activation and invalid-token rejection still require
an owner-authorized validation serial and an installed run.

Evidence: source review of `scripts/build_native_license.py`,
`src/rhetoric/licensing/keys.py`, `tests/licensing_fixtures.py`, and
`tests/test_native_core.py`.
