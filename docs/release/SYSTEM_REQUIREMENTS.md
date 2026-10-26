# System Requirements and Qualification — Rhetoric 1.5.0

These are the current engineering requirements. A platform or backend is not
qualified until its installed-artifact and real-render checks are recorded in
[Final Release Readiness](FINAL_RELEASE_READINESS.md).

| Area | Requirement / status |
|---|---|
| Operating system | Linux x86_64 is the intended qualification target; clean installed-artifact acceptance is open. |
| Windows | Unsupported and excluded from the proposed paid offer until the ten-run GUI certification and installer acceptance pass. |
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
