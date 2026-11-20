# Rhetoric Release Artifact Signing

Release artifacts use a dedicated local OpenPGP signing identity. This identity
is separate from the Ed25519 activation-license seed in
`~/secrets/rhetoric-seed.gpg`.

## Create and record the release identity

The active default GPG home (`/home/cody/.gnupg`) contains one secret key, but its public UID is `RedTeam Harness <redteam@harness.local>`, not a Featherline Studios or Rhetoric release identity. It is explicitly excluded from release use. No matching owner release key was found in this keyring; other keyrings, hardware-backed signers, backups, and external secrets were not inspected. See `release_artifacts/evidence-2026-11-19/candidate-rc13/signing-keyring-check.json`. Choose the display identity and expiry with the owner before running
key generation. Keep the private key in the GPG keyring or a hardware-backed
signer; back it up using an owner-controlled protected method. Do not export a
private key into the repository, build tree, installer, or a command log.

Example after the owner chooses the identity and expiry:

```bash
gpg --quick-generate-key 'Featherline Studios Rhetoric Release' ed25519 sign 2y
gpg --fingerprint --list-secret-keys
```

Record the full primary fingerprint locally. Verify it independently before
using it, and distribute the fingerprint through an owner-controlled channel.
Public signing or publication remains a separate explicit owner decision.

## Sign an immutable artifact

Import/select the approved key in the local GPG keyring, then run:

```bash
python3 scripts/sign_release_artifact.py sign \
  --artifact /path/to/Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz \
  --fingerprint FULL_PRIMARY_FINGERPRINT
```

The helper writes an armored detached `.asc` signature and a JSON record beside
the artifact. It records the artifact size and SHA-256, signs the exact file,
checks the signature against the requested full fingerprint, and rechecks the
artifact bytes. It refuses to overwrite an existing signature or metadata
file. Signing never modifies the artifact itself.

## Verify offline

Receive the artifact, detached signature, and public key through the delivery
channel. Before installing, authenticate the fingerprint independently, import
the public key, and run:

```bash
gpg --import featherline-release-signing-key.asc
python3 scripts/sign_release_artifact.py verify \
  --artifact Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz \
  --signature Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz.asc \
  --fingerprint FULL_PRIMARY_FINGERPRINT
```

The tool reports the verified hash and byte size. A signature file or bundled
public key alone does not authenticate the signer; compare the fingerprint
against the owner-controlled value first.

## Current state

- Local GPG is available. The default keyring contains a non-release RedTeam Harness key; it is not the owner-approved Rhetoric signer.
- The RC13 Rhetoric V1.00a candidate remains unsigned. This tooling change does not
  sign, modify, rebuild, or publish it.
