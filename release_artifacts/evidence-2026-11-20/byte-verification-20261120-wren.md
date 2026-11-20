# Rhetoric RC13 byte verification — 2026-11-20 (Wren)

Verified live on codypc against the canonical checkout
`/media/cody/Data/DOCUMENTS_PROJECT_FILES/Rhetoric`, branch `V1.00a-beta_build`,
HEAD `49f0678`. Reference: `release_artifacts/evidence-2026-11-19/candidate-rc13/build-identity.json`.

## Verdict: all hashes matched. No mismatches.

## 1. RC13 candidate hashes (vs build-identity.json)

| File | Bytes | SHA-256 recomputed | Recorded | Result |
|---|---|---|---|---|
| `release_artifacts/linux-frozen-rc13-20261119/Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz` | 4985608078 | `b1fcd5e4f8880776e4ae076aae5466adf48fa5e025d4dc5daf24ad8b10a97f8d` | `b1fcd5e4f8880776e4ae076aae5466adf48fa5e025d4dc5daf24ad8b10a97f8d` | MATCH |
| `release_artifacts/linux-frozen-rc13-20261119/rhetoric_1.5.0_amd64.deb` (standalone) | 472970192 | `8883329c3f8c340b2b6e6757aa3d10e38dd6fafe1bc3169e6cd08d41f82fe992` | `8883329c3f8c340b2b6e6757aa3d10e38dd6fafe1bc3169e6cd08d41f82fe992` | MATCH |
| `release_artifacts/linux-frozen-rc13-20261119/sbom.json` | 21665 | `6b9de3cd09c2fde9031fd5df0bfb7cce9bc861c70e67558b4153a2121ae51311` | `6b9de3cd09c2fde9031fd5df0bfb7cce9bc861c70e67558b4153a2121ae51311` | MATCH |

## 2. Archive integrity

- `gzip -t` on the RC13 tar.gz: PASS (`GZIP_OK`).
- `tar -tzf` listing: 146 entries (130 files, 16 directories). Contents include
  `kit/install.sh`, `kit/uninstall.sh`, `kit/manifest.json`, `kit/SHA256SUMS`,
  `kit/models/SHA256SUMS`, `kit/rhetoric_1.5.0_amd64.deb`,
  `kit/runtime-debs/` (94 runtime .deb files), `kit/audio.cpp/bin/audiocpp_cli`,
  `kit/models/Chatterbox-GGUF/chatterbox-q8_0.gguf` and the hf_cache model files,
  plus the Seashells voice files.

## 3. Embedded .deb inside the tar.gz

Streamed `kit/rhetoric_1.5.0_amd64.deb` out of the archive and hashed it in flight
(no extraction to disk):

- Embedded .deb SHA-256: `8883329c3f8c340b2b6e6757aa3d10e38dd6fafe1bc3169e6cd08d41f82fe992`
- Identical to the standalone .deb and to the recorded value: MATCH.

## 4. Kit SHA256SUMS streaming verification

Method: a Python `tarfile` stream (`r|gz`) read every archive member once and
hashed it in 1 MB chunks, comparing against `kit/SHA256SUMS` (129 entries) and
`kit/models/SHA256SUMS` (10 entries). No archive contents were extracted to disk.

- Expected entries (unique): 129
- Matched: 129
- Mismatched: 0
- Missing from the tar: 0
- Tar files without a checksum entry: 1 — `kit/SHA256SUMS` itself, which is
  expected (a checksums file cannot contain its own hash).
- Note: `kit/SHA256SUMS` already covers the 10 model files (with `models/`
  prefixes), and `kit/models/SHA256SUMS` lists the same 10 files with identical
  hashes, so the unique-entry count is 129, not 139.

## 5. Debian package identity

`dpkg-deb --info` on the RC13 .deb:

- Package: `rhetoric`
- Version: `1.5.0`
- Architecture: `amd64`
- Size: 472970192 bytes; control archive 432 bytes
- Section: sound; Priority: optional; Maintainer: Rhetoric
- Description: Rhetoric local text-to-speech application — Frozen application;
  models are downloaded after activation.

## 6. Older candidates RC1 / RC2

Under `release_artifacts/linux-rc-32ac9df/`:

| File | Sidecar SHA-256 | `sha256sum -c` | `zstd -t` |
|---|---|---|---|
| `Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc1.tar.zst` | `00e0caa5a15af0757e56e69a5baf5d19044ab13b5a0d18cb7f729d04294f4b28` | OK | OK (5877800960 bytes decompressed) |
| `Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc2.tar.zst` | `1ee5a60ac905b1da5a81db3fba773d6575abab8e965fe1286a074e66066c7ace` | OK | OK (5943572480 bytes decompressed) |

Note: an initial RC2 `sha256sum -c` run from inside `linux-rc-32ac9df/` reported
`FAILED open or read` because the RC2 sidecar lists a repo-root-relative path
(`release_artifacts/linux-rc-32ac9df/...`). That was an invocation error, not a
hash problem. Re-run from the repo root: OK.

## 7. Disk and method notes

- Free space at verification time: `/` 43G free (91% used);
  `/media/cody/Data` 57G free (94% used).
- No multi-GB temp files were written. Verification streamed the archive
  (hash passes, `gzip -t`, tar listing, one Python streaming pass). Only small
  files were written to `/tmp` (contents list, the two SHA256SUMS extracts,
  `/tmp/rc13-kit-verify.json`).
- Nothing was rebuilt. No other Rhetoric copies on the machine were touched.

## 8. Commands used

```sh
sha256sum Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz rhetoric_1.5.0_amd64.deb sbom.json
gzip -t Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz
tar -tzf Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc13.tar.gz
sha256sum -c Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc1.tar.zst.sha256
sha256sum -c release_artifacts/linux-rc-32ac9df/Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc2.tar.zst.sha256
zstd -t Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc1.tar.zst
zstd -t Rhetoric-V1.00a-Ubuntu24.04-amd64-AirGap-rc2.tar.zst
dpkg-deb --info release_artifacts/linux-frozen-rc13-20261119/rhetoric_1.5.0_amd64.deb
python3 /tmp/rc13-verify.py   # streaming tarfile SHA-256 verification of all 129 kit entries
```

## Conclusion

RC13 bytes are exactly as recorded in `build-identity.json`: tar.gz, standalone
.deb, embedded .deb, and SBOM all match; gzip integrity passes; all 129 kit
checksum entries verify in-stream with zero mismatches; the .deb is
`rhetoric` 1.5.0 amd64. RC1 and RC2 also match their sidecars and pass `zstd -t`.
