# Candidate secret scan

Final candidate source `32ac9df7200e5fedf04dfd01c0edb55be642dd50`: Gitleaks exit 0, zero findings on the exact offline kit with `--max-target-megabytes 5` and redacted JSON. Files larger than 5 MiB, including compiled binaries and models, were skipped. This is a scoped secret scan, not a malware or binary security audit.

Evidence: `kit-secret-scan-32ac9df.log`, `kit-secret-scan-32ac9df.json`. The earlier `kit-secret-scan.log` records a stopped unrestricted attempt against the superseded candidate; it is not treated as a result.
