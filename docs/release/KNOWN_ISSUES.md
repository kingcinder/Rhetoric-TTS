# Known Issues — Rhetoric 1.5.0

This is the current engineering-candidate issue list, not a claim that the
release has passed every acceptance gate.

- **Human audio review is outstanding.** Automated CPU synthesis produced a
  valid FLAC, but intelligibility and audible quality have not been reviewed.
- **Windows is unsupported and excluded from the proposed paid offer** until
  GUI certification and native installer acceptance pass.
- **CUDA and Vulkan are experimental.** Matching-hardware production rendering
  and resource measurements are not qualified.
- **First model use requires a large download** unless a correctly prepared
  offline bundle is used. The provider receives ordinary connection metadata.
- **Japanese conversion is not included in the managed installation.** Text
  normalization and multilingual paths have not been exhaustively qualified.
- **The EULA is a draft.** Commercial distribution remains blocked pending
  owner and counsel review; pricing and purchase terms are not approved.
- **Dependency review is scoped.** `pip-audit` found no known vulnerabilities
  in its auditable installed dependency set. Locally sourced or non-PyPI
  packages were skipped and are not thereby proven free of vulnerabilities.
- **Installed lifecycle qualification remains open.** Clean-machine
  installation, cold model download, project save/reopen, update, rollback,
  and uninstall need direct acceptance evidence.
- **Hosted CI for this release branch must be checked at its pushed commit.**
  Earlier run IDs and commit-specific reports belong to superseded candidates.

See [Final Release Readiness](FINAL_RELEASE_READINESS.md) for the current
evidence and outstanding acceptance gates. Report a reproducible issue with
the in-app **Help → Report a Problem…** flow or follow [Support](../SUPPORT.md).
Review diagnostics before sharing them.
