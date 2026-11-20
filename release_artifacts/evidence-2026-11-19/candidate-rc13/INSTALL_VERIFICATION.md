# RC13 offline installation/runtime verification

- Kit: `../../linux-frozen-rc13-20261119/Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz`
- Archive SHA-256: `b1fcd5e4f8880776e4ae076aae5466adf48fa5e025d4dc5daf24ad8b10a97f8d`
- Embedded Debian package SHA-256: `8883329c3f8c340b2b6e6757aa3d10e38dd6fafe1bc3169e6cd08d41f82fe992`
- Installed package version: `1.5.0` (`amd64`)
- Clean test host: blank Ubuntu 24.04.5 LTS amd64 container (`amd64`, `x86_64`), with no Rhetoric package before install; Docker network mode `none`.
- Installer: the exact candidate kit's `install.sh`; package, 94 offline runtime
  debs, voices, audio.cpp binary, pinned Hugging Face cache, and 2.09 GB Vulkan
  GGUF were supplied by the mounted kit.
- Result: installer exited 0, verified all 129 kit `SHA256SUMS` entries,
  installed all package/runtime resources, and `dpkg-query` reported `1.5.0`.
- The actual installed GUI executable remained running for 20 seconds in Qt
  offscreen mode; the expected timeout exit was 124. The startup log reports
  that the clean container has no PipeWire multimedia library/audio session,
  Qt switched its non-UTF locale to `C.UTF-8`, and the offscreen platform does
  not support `propagateSizeHints`. It did not crash. A visible desktop review
  remains pending.
- CPU and Vulkan audio renders used the installed frozen Rhetoric render
  subprocess. The Vulkan route reported `AMD Radeon RX 5700 XT (RADV NAVI10)`.
- Model cache for the qualification container was mounted read-only from the
  prior local qualification cache; no network access was available.

Full installer output and exit status are in `fresh-install.log` and
`fresh-install.exit`; GUI startup output and expected timeout status are in
`fresh-gui-start.log` and `fresh-gui-start.exit`. Structured evidence is
`clean-install-verification.json`.

The package version remains `1.5.0`, matching the project's existing packaging
scheme. The candidate is still unsigned and unpublished.
