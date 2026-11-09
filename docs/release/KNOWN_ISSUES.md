# Known Issues — Rhetoric 1.5.0

This is the current engineering-candidate issue list, not a claim that the
release has passed every acceptance gate.

- **Human audio review is outstanding.** Automated CPU synthesis produced a
  valid FLAC, but intelligibility and audible quality have not been reviewed.
- **Windows is experimental and excluded from the proposed paid offer** until
  GUI certification and native installer acceptance pass.
- **CUDA and Vulkan are experimental.** Matching-hardware production rendering
  and resource measurements are not qualified.
- **First model use requires a large download** unless a correctly prepared
  offline bundle is used. The provider receives ordinary connection metadata.
- **Japanese conversion is not included in the managed installation.** Text
  normalization and multilingual paths have not been exhaustively qualified.
- **The EULA was finalized by the owner on 2026-11-08** and validated against Washington primary sources (docs/release/EULA_WA_VALIDATION.md); independent counsel review has not been obtained, and pricing and purchase terms are not approved.
- **Dependency review is scoped.** A 2026-11-08 `pip-audit` of the
  development environment (174 packages) found one transitive vulnerability:
  msgpack 1.2.1 (CVE-2026-114613, fixed in 1.2.3), pulled in by
  librosa/CacheControl. Rhetoric's own code does not import msgpack and never
  deserializes MessagePack data; the floor should be raised when the engine
  dependency chain next updates. Locally sourced or non-PyPI packages were
  skipped and are not thereby proven free of vulnerabilities.
- **Installed lifecycle qualification remains open.** Clean-machine
  installation, cold model download, project save/reopen, update, rollback,
  and uninstall need direct acceptance evidence.
- **Hosted CI for this release branch must be checked at its pushed commit.**
  Earlier run IDs and commit-specific reports belong to superseded candidates.
  At 5446d39 (run 42576825781) every functional job passed: Ubuntu and
  Windows suites on both Pythons, the Vulkan no-skip suite, frozen
  packaging, the license core, and the Windows installer end-to-end.
  The suite-counts job passes only at a head whose counts are recorded
  in scripts/suite_counts_baseline.json.
- **The automated update channel has not carried a release yet.** The
  channel, opt-out, and support gate are implemented and tested
  (docs/release/UPDATE_CHANNEL.md), but no 1.5.x GitHub release with an
  update manifest has been published, so the in-app check currently finds
  no channel and support submission follows the gate's remedy path.

See [Final Release Readiness](FINAL_RELEASE_READINESS.md) for the current
evidence and outstanding acceptance gates. Report a reproducible issue with
the in-app **Help → Report a Problem…** flow or follow [Support](../SUPPORT.md).
Review diagnostics before sharing them.
