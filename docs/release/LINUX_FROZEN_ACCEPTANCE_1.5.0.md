# Frozen Linux Artifact Acceptance — Rhetoric 1.5.0

- **Date:** 2026-11-14
- **Artifacts:** run 43621773933, head `cf2dfd0` (`rhetoric-1.5.0-x86_64.AppImage`,
  `rhetoric_1.5.0_amd64.deb`, `checksums-1.5.0.sha256`, `sbom.json`,
  `update-manifest.json`)
- **Environment:** Docker `ubuntu:24.04`, no Python, git, or compilers. The
  container ran with no GPU device.
- **Verdict:** install, EULA, unlicensed state, and uninstall are verified. The
  full lifecycle (activation with a production serial, cold model download,
  render, save/reopen, upgrade, rollback, library swap) is **not** verified.

## Checksums

```text
$ sha256sum -c checksums-1.5.0.sha256
rhetoric-1.5.0-x86_64.AppImage: OK
rhetoric_1.5.0_amd64.deb: OK
sbom.json: OK
```

## .deb

```text
$ dpkg -i rhetoric_1.5.0_amd64.deb
INSTALL_OK
$ sha256sum /opt/rhetoric/usr/lib/rhetoric/_internal/EULA.md
d4f73f5644b930d218d6c0d17e2314a1079c9d072ae9bb35961fd1dc6a2b732e
```

The installed EULA digest equals the repository `EULA.md`.

**Finding (P1, fixed in source, rebuilt artifact still to verify):** this build
declared no `Depends`. On a clean Ubuntu 24.04 the first start aborted with
`ImportError: libGL.so.1`, then `libpulse.so.0`, then the Qt xcb platform
plugin. Installing this set made the frozen app start and stay up:

```text
libgl1 libegl1 libxkbcommon0 libxkbcommon-x11-0 libdbus-1-3 libfontconfig1
libglib2.0-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1
libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xfixes0
libxcb-xinerama0 libxcb-sync1 libxcb-xkb1 libx11-xcb1 libxrender1 libxi6
libxtst6 libsm6 libice6 libnss3 libnspr4 libcups2 libpulse0 libgomp1
```

`scripts/build_frozen_linux.py` now writes that list as the package `Depends`;
`tests/test_frozen_linux_packaging.py` pins it. The checked artifacts predate
that change, so they still need the libraries installed by hand.

## GUI under Xvfb (1280x800)

- Start: EULA dialog with the full agreement, `I Accept` / `Decline`.
- Accept: `Activate Rhetoric` dialog — "Paste the serial number you received
  after purchase", offline verification against keys embedded in the install,
  `Activate` / `Cancel`. This is the unlicensed state: the activation path is
  the only action offered.
- Cancel: the main window opens in its unlicensed presentation (tutorial step
  1 of 8, script/cast/render panels visible).
- Screenshots were captured during the run but are not committed; the container
  and commands above reproduce them.

## Uninstall

```text
$ dpkg -r rhetoric
RM_EXIT=0
$ find /opt/rhetoric
find: '/opt/rhetoric': No such file or directory
```

The application tree is removed. Per-user settings and data under
`~/.config/rhetoric` and `~/.local/share/rhetoric` are kept (not created in the
clean uninstall check; present after a GUI run, as designed for upgrade and
license retention).

## AppImage

```text
$ APPIMAGE_EXTRACT_AND_RUN=1 DISPLAY=:99 ./rhetoric-1.5.0-x86_64.AppImage start
APPIMAGE_ALIVE
```

FUSE is not available in the container, so the extract-and-run path was used.
With the library set above the window stayed up for the 15 s check; the log had
only UTF-8 locale and PipeWire warnings. The AppImage declares no dependencies,
so the same library set is a documented prerequisite (see
[System Requirements](SYSTEM_REQUIREMENTS.md)).

## Not verified (owner or next run)

1. **Activation:** no production serial was available, and the release build is
   expected to refuse dev-build throwaway keys. Test with a real serial.
2. **Cold model download:** size, time, interrupted resume, low-disk refusal,
   and the offline bundle were not exercised.
3. **First render, project save/reopen, settings persistence.**
4. **Upgrade from the legacy data layout and rollback** (update-manifest check
   is a static file; no update was applied).
5. **LGPL replace-the-library check** in the installed artifact.
6. **Screenshots in the release record** (captured locally, not committed).
