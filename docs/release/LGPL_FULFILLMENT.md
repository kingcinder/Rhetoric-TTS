# LGPL fulfillment — Rhetoric 1.5.0

Rhetoric is a proprietary application. It ships three components under the
GNU Lesser General Public License. This document records how each
obligation is fulfilled: the notices, the source offer, and the library
replacement / relink path for every install form Rhetoric ships in.

## Covered components

| Component | Version as shipped | License | How it ships |
| --- | --- | --- | --- |
| Qt libraries via PySide6 / shiboken6 | 6.8.2.1 (Qt 6.8.2) | LGPL-3.0 | Dynamically linked shared libraries, loose files in every install form |
| libsndfile | 1.2.2 | LGPL-2.1 | Shared library inside the `soundfile` wheel (`_soundfile_data/`); its own COPYING (LGPL-2.1 text) travels in the wheel |
| libsoxr | 0.1.3 | LGPL-2.1 | Statically linked into the `soxr` extension module; the soxr wheel carries libsoxr's COPYING.LGPL |

No other LGPL component is bundled. ffmpeg is host-provided, not bundled;
its license is determined by the host's own build.

## Notices

`THIRD_PARTY_NOTICES.md` (generated from `src/the_oracle/third_party.py`)
names all three components with their versions and licenses, and the full
LGPL-2.1 and LGPL-3.0 texts accompany the distribution.

## Source offer

The complete corresponding source for the exact shipped versions is
available at:

- Qt 6.8.2: https://download.qt.io/official_releases/qt/6.8/6.8.2/ and
  PySide6 6.8.2.1: https://code.qt.io/cgit/pyside/pyside-setup.git/ (tag
  v6.8.2.1)
- libsndfile 1.2.2: https://github.com/libsndfile/libsndfile/releases/tag/1.2.2
- libsoxr 0.1.3: https://sourceforge.net/projects/soxr/files/ (soxr-0.1.3)

In addition, for three years from the date of this release, anyone who
received Rhetoric 1.5.0 may obtain the same source on physical media for
no more than the cost of distribution by contacting the support address
in `PRIVACY.md`. This paragraph is the written offer under
LGPL-3.0 §6 / LGPL-2.1 §6(c) for recipients who do not use the links
above.

## Replacement / relink instructions

### Qt (all install forms)

The Qt libraries are ordinary files; nothing in Rhetoric verifies their
signatures or prevents their replacement.

Replace the Qt libraries **as a set** (all `libQt6*.so.6` together, one
version throughout): Qt itself refuses to mix versions across its
modules at runtime, so a partial swap aborts by Qt's own design.

- *Frozen AppImage:* run `./Rhetoric-1.5.0-x86_64.AppImage
  --appimage-extract` and replace the `libQt6*.so.6` files under
  `squashfs-root/usr/lib/rhetoric/_internal/PySide6/Qt/lib/` with builds
  of the same Qt major version (6.8.x), then run `squashfs-root/AppRun`
  directly or repack with `appimagetool`. (The `libQt6*.so.6` entries
  directly under `_internal/` are symlinks into that directory.)
- *Frozen .deb / one-folder:* replace the same files in the installed
  `_internal/PySide6/Qt/lib/` tree.
- *Venv / source install:* replace the `libQt6*.so.6` files in
  `.venv/lib/python3.12/site-packages/PySide6/Qt/lib/`.

Verified 2026-11-11: both the frozen Linux tree and a venv install run
with their shipped Qt 6.8.2 library set replaced by Qt 6.8.3 builds
(library-replacement test log kept with the release evidence).

### libsndfile

Replace `_soundfile_data/libsndfile_x86_64.so` (Linux) or
`libsndfile_x64.dll` (Windows) inside the installed `soundfile` package
with a build of the same ABI (libsndfile.so.1). The Python wrapper loads
whatever library file is present at that path.

### libsoxr (statically linked — relink path)

libsoxr is linked into the `soxr` extension module itself, so the
relink path is a rebuild of that module against the user's own libsoxr:

1. Build libsoxr (source above) with the modification of your choice.
2. Build the `soxr` Python package (https://github.com/dofuuz/python-soxr,
   version 1.1.0) against that library.
3. Replace the installed `soxr` package directory in the install tree
   (`.venv/lib/python3.12/site-packages/soxr/` or the frozen tree's
   `_internal/soxr/`) with the rebuilt one.

The extension module is a loose file in every install form; no other
part of Rhetoric needs to change.

## Owner decision record

Complying as-is (option (a) of `docs/legal/LICENSE_DECISIONS_PROPOSED.md`)
was adopted by the owner on 2026-11-11 and recorded in
`scripts/license_review.json`. Independent counsel ratification is tracked
separately with the EULA counsel review and does not block the mechanics
above.
