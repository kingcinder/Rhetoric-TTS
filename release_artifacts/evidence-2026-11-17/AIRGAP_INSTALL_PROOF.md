# Air-gap install proof — RC1

- Candidate source: `32ac9df7200e5fedf04dfd01c0edb55be642dd50`; public release label V1.00a; engineering version 1.5.0; Ubuntu 24.04 amd64.
- Archive SHA-256: `00e0caa5a15af0757e56e69a5baf5d19044ab13b5a0d18cb7f729d04294f4b28`; package SHA-256: `51cd9f263f4d5f134c8da3ee2ab98ca39fc9e43cd2617383556916d64a994931`.
- Test target: fresh cached `ubuntu:24.04` Docker container, started with `--network none`; kit mounted read-only.
- Integrity: all 116 entries in `/kit/SHA256SUMS` verified before installation. The outer archive checksum and Zstandard stream were independently verified.
- Install: bundled runtime packages and Rhetoric installed from the kit; `/usr/bin/rhetoric --version` returned `rhetoric 1.5.0`; `--help` completed; desktop entry and seeded CPU model cache were checked.
- Activation: no serial was present. `license-status` returned JSON `state=no_token` and exit 1, as expected. No activation or render bypass was attempted.
- Uninstall: passed; Debian package, executable, `/opt/rhetoric` and desktop entry were absent afterward, while the seeded CPU model cache remained. Projects/settings/recordings/license retention and reinstall/upgrade were not tested.
- Network: Docker used the network namespace `none` from container start. This proves no network path was configured, not packet-capture absence of traffic.
- Interactive GUI, doctor workflow, activation, audio rendering, and first-user project/settings lifecycle remain unverified.

Detailed final-candidate output: `release_artifacts/evidence-2026-11-17/airgap-install-uninstall-32ac9df.log`. The first stopped attempt for the superseded candidate is preserved in `airgap-install-uninstall.log`.
