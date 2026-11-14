# System Requirements and Qualification — Rhetoric 1.5.0

These are the current engineering requirements. A platform or backend is not
qualified until its installed-artifact and real-render checks are recorded in
[Final Release Readiness](FINAL_RELEASE_READINESS.md).

| Area | Requirement / status |
|---|---|
| Operating system | Linux x86_64 is the intended qualification target. The `.deb` declares the Qt/X11 library dependencies and apt installs them; the AppImage requires the same libraries to be present. Install, EULA, unlicensed state, and uninstall are verified in a clean Ubuntu 24.04 container; the rest of the lifecycle is open ([evidence](LINUX_FROZEN_ACCEPTANCE_1.5.0.md)). |
| Windows | Experimental; the paid-offer status is unchanged. Hosted Windows CI and a Windows 11 guest installer acceptance plus ten consecutive GUI certifications passed at `17fdab9` ([evidence](WINDOWS_GUEST_ACCEPTANCE_1.5.0.md)). Installers are unsigned. |
| Python | 3.11 or 3.12, enforced by the managed installer. |
| Media tools | `ffmpeg` on `PATH`; missing-tool acceptance remains part of the install walkthrough. |
| CPU inference | PyTorch Chatterbox CPU path is the default; exact release output still requires the fixed-corpus and human listening review. |
| NVIDIA GPU / CUDA | Experimental; matching-hardware production rendering and resource measurements are not qualified. |
| Vulkan GPU | Experimental audio.cpp backend; matching-hardware production rendering is not qualified. |
| RAM | Minimum not established. Measure peak use on qualified hardware before publishing a numeric minimum. |
| Disk | Minimum not established. The model set and first-run download require several GB; cold download, resume, and low-disk refusal remain unverified. |
| Network | Required for first-run model downloads; a correctly provisioned offline installation does not need it. Model download sends ordinary connection metadata to its provider; telemetry is not configured. |

For installation and first use, see [Quick Start](QUICK_START.md). For offline
installation and updates, see the [release runbook](../SOFT_LAUNCH.md) and
[upgrade guide](../UPGRADING.md).
