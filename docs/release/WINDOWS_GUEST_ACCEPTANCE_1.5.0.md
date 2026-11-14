# Windows 11 guest acceptance — Rhetoric 1.5.0

**Date:** 2026-11-14 · **Head:** `17fdab9` (`release/1.5.0-final`)
**Hosted CI at this head:** run [43605100480](https://github.com/kingcinder/Rhetoric-TTS/actions/runs/43605100480) — every job green, including `windows-latest / py3.11`, `windows-latest / py3.12`, each Windows ten-consecutive-certification step, and `Windows installer end to end`.

This record closes the installer-acceptance half of the Windows gate on the
local QEMU/KVM Windows 11 Pro guest described in [WINDOWS_VM.md](../WINDOWS_VM.md).
It is an engineering acceptance of an **unsigned** build on a VM. It is not a
claim of general Windows support, and it does not change the paid-offer
decision, which the EULA and the owner still scope to Linux.

## Artifact

Built on the guest from the exact tree of `17fdab9` (`git archive HEAD`, no
working-tree edits) with PyInstaller 6.16.0 and Inno Setup 6.7.4:

| | |
|---|---|
| File | `rhetoric-1.5.0-windows-unsigned.exe` |
| Size | 253,632,148 bytes |
| SHA-256 | `81e154a533ba2a287f7af2c7cdf4bf8a21edda8ca5c68106eb4ff5135169454d` |
| Inno compile | 312.8 s (`Successful compile`) |

The frozen bundle includes `_internal\EULA.md`, `_internal\rhetoric\EULA.md`,
`_internal\LICENSE`, `THIRD_PARTY_LICENSES\`, and
`docs\release\LGPL_FULFILLMENT.md`, as `packaging/windows/build.ps1` requires.

## Install acceptance

Silent install: `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /DIR=C:\RhetoricInstalled`.

- Exit code **0** in **65.5 s**.
- `Rhetoric.exe` 84,858,233 bytes; `_internal\EULA.md` and
  `_internal\rhetoric\EULA.md` 27,712 bytes each; `_internal\LICENSE` present.
- `eula_acceptance.json` (`accepted_at` 2026-11-14 07:38:12) holds an
  `eula_sha256` equal to the SHA-256 of the installed EULA text, so the app's
  first-run EULA gate is satisfied by the installer's license page.
- Start Menu: `…\Programs\Rhetoric\Rhetoric.lnk`.
- Uninstall entry: `Rhetoric 1.5.0` in the per-user uninstall key
  (`PrivilegesRequired=lowest`; no elevation).

## Activation and first window

The license store is repo-local, so the repo's valid `k2` token (no expiry)
was copied beside the installed executable.

- `current_license(C:\RhetoricInstalled)` → `ok=True`, `state=valid`, `key_id=k2`.
- Frozen GUI with a clean redirected profile and `QT_QPA_PLATFORM=offscreen`:
  - `C:\RhetoricInstalled\Output\logs\gui_launch_timing.json`:
    `qt_app_created` 0.011 s, **`mainwindow_built` 2.535 s**.
  - `%APPDATA%\rhetoric\Output\logs\gui_startup_timing.json`:
    `mainwindow_init_begin` 2.10 s, `mainwindow_init_end` 2.52 s.
  - `gui_prewarm_timing.json`: **`prewarm_success: true`** (engine, pipeline,
    emotion and repair threads ready).

## Phase 4 acceptance set

The serial-gate acceptance files named in
[PHASE4_SERIAL_GATE_PROGRESS.md](PHASE4_SERIAL_GATE_PROGRESS.md), run on the
guest with Python 3.12.10, offscreen:

```
104 passed in 43.64s   (exit 0)
```

Files: `test_eula_acceptance`, `test_serial_gate_product`,
`test_licensing_policy_enforcement`, `test_render_report`,
`test_license_state_render`, `test_gui_license`, `test_doctor_licensing`,
`test_cli_bug_report`, `test_support_diagnostics`, `test_gui_crash`.

## Ten consecutive six-theme certifications

`scripts/certify_gui.py --aspects contrast,chrome,studio,wizard`, run serially
ten times, stopping on the first failure, **no retries**:

| run | exit | seconds |
|---|---|---|
| 1 | 0 | 28.1 |
| 2 | 0 | 22.2 |
| 3 | 0 | 22.2 |
| 4 | 0 | 22.4 |
| 5 | 0 | 22.6 |
| 6 | 0 | 22.6 |
| 7 | 0 | 22.7 |
| 8 | 0 | 22.6 |
| 9 | 0 | 22.5 |
| 10 | 0 | 22.1 |

Every log carries all four "All good across all 6 themes" aspect summaries,
with per-theme OK lines for contrast ratios, studio/wizard theming and section
rendering. Raw logs:
`C:\Rhetoric\gui-certification-runs\run-{1..10}.txt` (UTF-16LE, PowerShell
`Tee-Object`); SHA-256 of `run-1.txt` is
`e5818bb797ad2e22f60df8b561c2b61af681212cd798610c86111b58c94bee5a`.

Non-fatal, Windows-only warnings in every run: PySide6 ships no font directory
(`QFontDatabase: Cannot find font directory`), and the throwaway Qt config root
survives five reap attempts (already listed in
[WINDOWS_VM.md](../WINDOWS_VM.md)). Neither changes an exit code or a
certification verdict.

## What this does not establish

- **Signed distribution.** The installer is explicitly unsigned; SmartScreen
  behaviour on a real user's machine is unobserved.
- **Physical hardware.** The run is a QEMU/KVM guest (8 vCPU, 8 GB RAM,
  Windows 11 Pro build 26200), not a clean physical Windows 11 machine.
- **GPU paths.** CUDA and the Vulkan `audio.cpp` backend were not exercised.
- **Human audio review** of a Windows render.
