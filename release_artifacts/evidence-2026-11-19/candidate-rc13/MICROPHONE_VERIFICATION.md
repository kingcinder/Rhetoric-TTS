# Recording Studio microphone verification (RC13)

The reported dropdown text, `(recording backend not installed)`, was caused by
the frozen Linux runtime. PyInstaller bundled `libportaudio.so.2` under
`_internal`, while `sounddevice` asked `ctypes.util.find_library("portaudio")`
to locate it by system library name. A fresh offline installation has no
system PortAudio entry, and the frozen runtime did not search its bundled
directory. The dialog consequently hid the import failure behind its generic
placeholder.

`src/rhetoric/audio/recorder.py` now redirects that lookup to the exact bundled
library during `sounddevice` import for frozen Linux only, then restores the
original lookup function. Normal source and system installs retain their
existing import behavior. The regression test in
`tests/test_recorder.py` covers the frozen runtime lookup.

Verification:

- Focused recording and frozen packaging tests: **48 passed in 20.21s**; full output is in `microphone-tests.log`.
- Built RC13's frozen application runtime contains the bundled
  `libportaudio.so.2` (SHA-256 `62eed4dd6a8e105e57bc34f7b1fa252123aec7e4c27b55ceece4d20aa6f9622b`).
- With `sys.frozen` and `_MEIPASS` set to RC13's exact `_internal` directory,
  `sounddevice` 0.5.6 initialized and PortAudio enumerated six inputs.
- The production `RecordingStudioDialog` displayed `default`, both HD-Audio
  ALC1220 inputs, USB PnP Audio, `pipewire`, and `pulse`; the microphone and
  sample-rate menus were usable and the Record button was enabled.
- The check only enumerated devices. It did not open a recording stream or
  capture microphone audio.

The fix is in the RC13 installer, not the previously installed RC12 package.
The exact RC13 offline kit's `install.sh` completed in a network-disabled
Ubuntu 24.04 amd64 qualification container and installed package version
`1.5.0`, the bundled audio.cpp CLI, and the Vulkan GGUF model.

## Current desktop launcher verification (2026-11-19)

The desktop entry points to `/home/cody/.local/bin/rhetoric gui`, whose wrapper
executes this checkout's `.venv/bin/rhetoric`. The source package's production
`RecordingStudioDialog` was initialized offscreen on that path. It listed the
same six inputs, exposed ten sample-rate options, and enabled the Record
button. The selected default device (PortAudio index 14) also opened and closed
at 44.1 kHz through `InputStream` successfully. No audio samples were read,
retained, or written. Recorder and Recording Studio tests passed: **30 passed
in 12.80s**. Exact results and source hashes are recorded in
`launcher-microphone-verification.json`.

The user's visible window was not inspected; the UI exercise was offscreen.
