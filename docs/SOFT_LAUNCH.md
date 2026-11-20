# Rhetoric 1.5.0 — Commercial Release Gate

Status as of **2026-11-19**: the project `.venv` soft-launch gate reports
**ready, 0 blockers, 1 weak-copyleft warning**. This is not commercial
clearance. The exact RC13 offline kit passed a network-disabled clean install
on Ubuntu 24.04.5 amd64. Owner desktop GUI review, human listening, and
hosted CI against an owner-selected source revision, and independent counsel
review remain open; release signing and publication also require owner
authorization. Windows is **unsupported** for this release.
`python scripts/soft_launch.py --check` is the authority for the automated
gate. Exact-candidate evidence and owner actions are tracked in
[`release/V100A_SHIP_TODAY_CHECKLIST.md`](release/V100A_SHIP_TODAY_CHECKLIST.md).

## Product model

Rhetoric is offered as a one-time serial-number license. There is no
subscription, community edition, trial, or optional activation. Without a
valid serial, the application remains visible but functional features are
inert except activation, status, help, documentation, doctor, and quit.
Activation verifies the serial offline.

The storefront and payment workflow are deferred, so this repository does not
provide a purchase or serial-request path. Pricing and final commercial terms
require owner approval; the EULA and proposed third-party license decisions
require qualified-counsel review. The application must not be distributed
while the release gate is blocked.

## System requirements

- Linux x86_64 is the intended qualification target and is not yet qualified.
  Windows x86_64 is unsupported.
- Python 3.11 or 3.12.
- `ffmpeg` on `PATH`.
- Git, to fetch the release branch and updates.
- Disk space for the pinned models (several GB) and renders.
- Optional: an NVIDIA GPU with a suitable PyTorch/CUDA runtime, or a
  Vulkan-capable GPU for the opt-in audio.cpp backend.

## Install

```bash
git clone --branch release/1.5.0-final https://github.com/kingcinder/Rhetoric-TTS.git
cd Rhetoric-TTS
./rhetoric install
./rhetoric start
```

On Windows:

```powershell
git clone --branch release/1.5.0-final https://github.com/kingcinder/Rhetoric-TTS.git
cd Rhetoric-TTS
.\rhetoric.ps1 install
.\rhetoric.ps1 start
```

`./rhetoric install` creates the venv, installs the pinned runtime, registers the
launcher, and runs the doctor. `./rhetoric doctor` is the first stop for any
problem. The doctor's `--json` report is machine-readable.

## Serial-number licensing

Rhetoric uses a one-time serial-number purchase. There is no subscription,
Community edition, trial, or optional activation. Without a valid serial,
product features remain inert except activation, status, help, documentation,
doctor, and quit. Activation verifies the serial offline and contacts no
server.

The storefront and payment workflow are deferred. Do not direct customers to
email for a purchase or serial request. The owner mints serials after an
authorized sale using the sibling `rhetoric-license-generator/license_sign.py`;
the production signing seed stays in the owner's secret manager. See
[LICENSING_OPS.md](LICENSING_OPS.md)
for custody and test-key procedures.

`RHETORIC1` is the token prefix from the 2026-11-12 rename onward.
`ORACLE1` is the historical token prefix for 1.5.0 and remains accepted for
compatibility. Neither is the product name.

## Support

Compose a bug report, package it with the redacted diagnostics, and attach the
zip to the issue or email you send:

```bash
rhetoric bug-report new --title "..." --summary "..." --step "..."
rhetoric bug-report show <report-id>       # read exactly what will be shared
rhetoric bug-report package <report-id>    # Output/rhetoric-report-<id>.zip
rhetoric bug-report issue <report-id>      # prefilled issue + email links
```

In the GUI this is **Help → Report a Problem…**. Drafts stay in
`support_reports/` (newest 25); nothing is uploaded, and deleting one is
explicit. The full workflow is in [SUPPORT.md](SUPPORT.md).

For a bundle without a written report, `rhetoric support-bundle` still works:

```bash
rhetoric support-bundle
```

The bundle is written under `Output/` and is never uploaded. It contains the
app version and platform, whether `RHETORIC_*` variables are present (not their
values), the license state (never the serial number or licensee), redacted settings,
the newest redacted logs, and a doctor report. Crash reports are included only
with `--include-crash-reports` **and** when local crash-reporting consent is
on.

The bundle never includes dialogue files, manuscripts, rendered audio, voice
recordings, reference clips, serial numbers, or home-directory paths. The
report package adds `report.md`, `report.json`, and `diagnostics.json` to the
same bundle. Read the zip before sending it; redaction is best-effort.

For a render problem, include the project's `render_plan.json` and the exact
input text only if you are comfortable sharing them. They are never collected
automatically.

## Privacy

There is no telemetry, no analytics, no crash upload, and no phone-home. See
[PRIVACY.md](../PRIVACY.md). The licensing and crash packages are pinned to
import no network module at all.

## Updates

Updates are manual for an engineering checkout:

```bash
git pull
./rhetoric update
./rhetoric doctor
```

`./rhetoric update` keeps `Input/`, `Seashells/`, `Profiles/`, `Output/`, and
your settings. The [CHANGELOG](../CHANGELOG.md) is the source of truth for what
changed.

## Known limitations

- **Windows is experimental.** Hosted Windows CI and a clean Windows 11 guest
  installer acceptance plus ten consecutive GUI certifications passed at
  `17fdab9` ([evidence](release/WINDOWS_GUEST_ACCEPTANCE_1.5.0.md)); the
  installer is unsigned, and Windows remains excluded from the proposed paid
  offer.
- **First run downloads models.** The first render may need a multi-GB model
  download; the doctor announces it before it starts. Offline installs use the
  bundle instead.
- **Third-party obligations remain.** The soft-launch gate reports LGPL
  notice and replacement/source obligations for Qt and other weak-copyleft
  components. They require a documented fulfillment path before distribution.
- **The EULA was finalized by the owner on 2026-11-08.** It is adopted as EULA.md and validated against Washington primary sources (docs/release/EULA_WA_VALIDATION.md); independent counsel review remains outstanding and is still required before the release gate can be treated as commercially cleared.
- **A serial number gates functional features.** `render-report` and every
  other render or editing workflow require activation; help and status remain
  available without one.

## Owner go-live checklist

Run the gate and review each finding; an automated ready result is not
commercial clearance:

```bash
.venv/bin/python scripts/soft_launch.py --check
```

| Finding | Owner action |
|---|---|
| `eula` | The EULA is adopted and the automated check passes. Obtain independent counsel review before commercial clearance. |
| `license_policy` warning | Keep the notices and source-offer/replacement instructions current; the exact RC13 Qt library set was hash-matched to the previously replacement-tested set. See `release/LGPL_FULFILLMENT.md` and the RC13 release evidence. |
| `third_party_notices` | Keep generated notices current with `python scripts/generate_third_party_notices.py --check`; exact RC13 package notice evidence is in the release checklist. |
| `version` | Keep `__version__`, the README banner, and `CHANGELOG.md` in agreement (`scripts/release.py --check`). |
| `checksums` | The 1.5.0 manifest is generated locally and must be committed with the release record; rebuilds must not silently replace it. |
| `windows_scope` | Keep Windows explicitly unsupported until current-head qualification passes. |
| `support_bundle` | Keep `rhetoric.support_bundle` importable. |

Warnings (weak-copyleft LGPL/MPL packages such as PySide6, certifi, `orjson`,
`soxr`, and `tqdm`) do not block the gate, but their notice and
replacement/source obligations must be honored before distribution. The LGPL
obligation for PySide6/Qt is spelled out in
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

A green gate means the tracked tree has no known commercial blocker. It does
not replace counsel's review of the EULA or the dependency decisions.
