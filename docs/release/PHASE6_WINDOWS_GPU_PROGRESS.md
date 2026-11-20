# Phase 6 Windows and GPU Progress — 1.5.0 RC

**Current status (2026-11-14):** Windows is experimental and excluded from the proposed paid offer. At `17fdab9` every hosted Windows job passed (both Python versions, the installer end-to-end, and the ten consecutive six-theme certification step on each), and a Windows 11 Pro guest passed installer acceptance, activation and ten consecutive certifications ([evidence](WINDOWS_GUEST_ACCEPTANCE_1.5.0.md)); the installer is unsigned. CUDA and Vulkan are experimental, and matching-hardware GPU production rendering remains unverified. The GUI wizard, backend/device pickers, tooltips, menu action, CLI help, documentation, and both EULA copies now label the GPU paths experimental. The canonical Linux/offscreen full test suite passed; that run is not Windows or GPU qualification.

> Historical progress below describes a previous release-candidate state. Its metrics and CI results are not current-head evidence.

Previous progress notes are retained in [`archive/PHASE6_WINDOWS_GPU_PROGRESS_HISTORICAL.md`](archive/PHASE6_WINDOWS_GPU_PROGRESS_HISTORICAL.md).
