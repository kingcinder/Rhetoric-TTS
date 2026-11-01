# Licensing & Anti-Piracy — Feature Scope

Status: **serial-number product gate adopted** (2026-10-23), **verification
core compiled** (2026-10-29, §10). This document describes the offline
verification contract and the licensed/unlicensed behavior.

---

## 1. Goals and honest threat model

Rhetoric is distributed as Python source plus a built wheel. Any
client-side license check in readable Python can be bypassed by a determined
user editing one file. **This design does not pretend otherwise.** What it
delivers, in order of value:

1. **A clean purchase path** — activation is paste-a-serial-number, works fully
   offline, and says so in the privacy policy truthfully.
2. **Casual-copy friction** — a copied install without a valid serial number
   remains visible but its functional features are inert.
3. **An audit trail** — every install reports its license state through the
   doctor and About panel.
4. **One product gate** — every functional entry point uses the same
   licensed/unlicensed check.

Non-goals: DRM, obfuscation, tamper-resistance, network license servers,
phone-home validation. A phone-home check would contradict the suite's
offline guarantee and its privacy posture — rejected up front.

## 2. Module layout

New package, following the existing small-module conventions (Qt-free policy
code, app_paths-managed persistence, cli.py owns command wiring):

```
src/the_oracle/licensing/
├── __init__.py     # public surface: current_license(), verify_token(), LicenseStatus
├── keys.py         # embedded verify keys + key-id registry (ONLY place key material lives)
├── tokens.py       # token parse/verify over a versioned, canonical-payload envelope
├── machine.py      # machine fingerprint: SHA-256 of OS machine id — hash only, never raw
├── store.py        # token persistence, repo-local (no XDG user dir exists); atomic write
└── policy.py       # licensed/unlicensed gate; single source
```

Vendor-only tooling lives in `../oracle-license-generator/`, a sibling
directory outside the Git repository:

```
license_sign.py   # vendor-only minting CLI; not uploaded with the product repo
```

The signing key enters the release process through an environment variable
(`ORACLE_LICENSE_SIGNING_KEY`); losing it means key rotation (supported, see
below), not disaster. A GUI slice later adds a small `gui_license.py`
(activation + About panel) following the `gui_ingest.py` injected-Qt pattern —
out of scope for the first slice.

Import discipline: `the_oracle.licensing` imports stdlib plus the vendored
`the_oracle._ed25519` only — no third-party crypto dependency exists (decision
§3). It must never import huggingface_hub, torch, or anything heavy, and it
must never run at import time — `cli.main()` and `MainWindow` call
`current_license()` lazily at feature gates, so GUI launch stays fast and an
unlicensed install never blocks startup.

## 3. Key and token model

**Crypto choice — DECIDED (2026-09-25): Option B, vendored pure-Python
Ed25519** (`the_oracle/_ed25519.py`, RFC 8032, pinned to the spec's §7.1 test
vectors; verify in the client, sign only in the vendor script). Rationale: no
new dependency for offline installs, nothing compiled to bundle, fully
auditable; verification runs once per activation and once per doctor run, so
the speed cost is irrelevant. The pynacl swap path is contained to this one
module plus `keys.py`'s import. (Option A remains viable if a future need —
high-volume revocation lists, say — makes C-speed verification real.)

An HMAC-SHA256 stdlib-only scheme was considered and rejected: the verify
key must be embedded in the client, so key extraction forges licenses. With
asymmetric signing, extraction buys the attacker nothing.

**Token format** (`tokens.py` owns; versioned envelope):

```
ORACLE1.<base64url(payload)>.<base64url(signature)>
```

Payload is canonical JSON (sorted keys, compact separators, UTF-8) so the
signature is byte-stable across platforms:

```json
{
  "v": 1,
  "key_id": "k1",
  "lic_id": "UUID",
  "licensee": "optional name or email — the customer's own choice",
  "machine_hash": "optional sha256 — present only for machine-locked seats",
  "iat": 1780000000,
  "exp": null
}
```

`exp: null` is a perpetual license. Verification order: envelope shape →
key_id known → signature over canonical payload → `exp` → machine binding.
Any failure yields a typed `LicenseStatus`, never an exception at the call
site.

**Key rotation:** `keys.py` holds an ordered registry of `(key_id, verify_key)`.
Tokens carry their key_id. Rotation = embed the new key, keep the old one
verifying for one release cycle, then drop it. A token failing *all* known
keys is "invalid", not "needs rotation".

**Machine binding — decision point.** V1 recommendation: **not
machine-locked** (per-seat honor system; `machine_hash` field exists but is
unpopulated). Machine-locked tokens require the buyer to run
`rhetoric machine-id` and include the hash at purchase, which adds
support friction for negligible deterrent gain in v1. `machine.py` ships in
v1 (the fingerprint is one stdlib call per OS: `/etc/machine-id` /
Windows `MachineGuid` / macOS `IOPlatformUUID` — hashed, raw value never
stored or logged) so opting in later is a vendor-side token field, zero
client releases. Store only the hash: this is a deliberate privacy
decision, and it is what lets the privacy policy say the license contains
no personal data unless the customer typed some in.

## 4. Licensed and unlicensed states

`policy.py` is the single source the GUI, CLI, pipeline, and doctor read:

| State | Behavior |
|---|---|
| unlicensed | The application is visible but functional features refuse with a serial-number message. Activation, status, help, documentation, and quit remain available. |
| licensed | A verified, unexpired serial number enables the full product. |

Serial numbers are perpetual by default. Expired, malformed, unknown-key,
tampered, and machine-mismatched values are unlicensed. No workflow silently
downgrades to a usable state.

Enforcement surface is deliberately soft: `policy.require(entitlement)`
raises a typed `LicenseRequired` that the CLI and GUI catch and render as a
clean purchase-path message. There is no enforcement deeper than feature
boundaries, by design (see §1).

## 5. What the doctor must say

New `licensing` check in `scripts/doctor.py`, under the same constraints as
every other check (read-only, idempotent, history-independent — pinned by
`test_doctor_read_only.py`, `test_doctor_idempotence.py`,
`test_doctor_report_is_history_independent.py`):

- **No token installed** → `ok=true`, informational: "not activated —
  serial number required for features". Unlicensed is a *valid state*; the doctor never fails
  an install for lacking a license and never suggests purchasing as a
  "problem".
- **Valid token** → `ok=true`, informational: licensed, licensee (as the
  customer entered it), key_id, expiry if any, machine-locked yes/no.
- **Failure states** → `ok=false` with the remedy inline: malformed token
  (`re-enter the activation token`), signature invalid or unknown key_id
  (`token is not a genuine Rhetoric license`), unreadable store file
  (permissions fix), expired (renewal contact — **never** "go online to
  verify"; see §6).
- Verification is a pure function of (token bytes, embedded keys, wall
  clock). The clock is the only external input; a token that crosses its
  `exp` between runs legitimately changes the report, the same way any
  time-derived check does. Nothing else in the check touches mutable state,
  which is what the history-independence pin actually requires.

## 6. What the offline guarantee must say

The licensing unit is **fully offline by construction** — the offline
guarantee test file (`tests/test_offline_guarantee.py`) gains these pins:

1. **Activation and verification perform zero network I/O**: with
   `socket.socket` monkeypatched to raise, mint→store→verify→`current_license()`
   succeeds end to end.
2. **No heavyweight imports**: importing `the_oracle.licensing` never imports
   huggingface_hub or any ML dependency — same import-time discipline the
   offline policy already enforces elsewhere (`offline.py` owns the marker;
   licensing reads it, never writes it, never triggers a download).
3. **Doctor licensing check runs on offline installs** and its failure
   remedies never instruct a network action — an expired serial number's
   remedy is a reissue contact, stated as such.
4. **Deactivation is local**: removing the token file moves the seat; there
   is no server to tell. (Machine-locked re-issue is a vendor email action,
   out of client scope.)

The privacy policy (separate unit) can then truthfully state: *activation
never contacts a server; the license file contains no personal data unless
you typed it in; the machine fingerprint, when used, is stored only as a
hash and never leaves the machine.* That sentence is a design constraint on
this unit, not a later promise to retrofit.

## 7. Test plan (promised, per existing discipline)

- `tests/test_licensing_tokens.py` — mint→verify roundtrip; tampered payload
  rejected; wrong-key token rejected; unknown key_id rejected; `exp`
  boundary (before/after, with a frozen clock); canonical-JSON
  byte-stability across key-order shuffles.
- `tests/test_licensing_store.py` — atomic write (no partial token on
  simulated crash), corrupted file → typed error status, not a crash.
- `tests/test_licensing_offline.py` — the §6 pins (1) and (2), in the same
  mutation-proven style as the existing guarantee tests.
- `tests/test_doctor_licensing.py` — read-only + idempotent with a license
  present; unlicensed install reports `ok=true`; each §5 failure state
  renders its remedy. Mutations: flip the signature check and the exp
  check, confirm the net catches both.
- Rotation test: mint under key 1, add key 2, verify token still passes;
  drop key 1, same token now reports unknown-key.

## 8. Rollout order (each step its own bounded unit)

1. ~~Crypto decision + dependency pin~~ **DONE 2026-09-25** — decided §3
   Option B (vendored pure-Python Ed25519); no dependency was added, so the
   offline bundle is unchanged and `dependency_pins` gained nothing new to
   police.
2. **`licensing/` core** — tokens, keys, policy, store + the §7 unit tests.
3. **CLI surface** — `rhetoric activate <token>`, `rhetoric
   license-status`, `rhetoric machine-id`; the vendor-only signer in the
   sibling `oracle-license-generator/` directory.
4. **Doctor check** — §5 + doctor tests.
5. **Offline-guarantee pins** — §6 tests, mutation-proven.
6. **GUI slice** — `gui_license.py` (activation dialog + About panel),
   separate session, following the injected-Qt patch-surface pattern.
7. **Privacy policy unit** — consumes §6's final sentence; separate scope.

## 9. Open decisions (owner: you)

1. ~~Crypto~~ **DECIDED 2026-09-25**: vendored pure-Python Ed25519 (see §3).
2. ~~Machine-locked seats in v1~~ **resolved by implementation**: tokens are
   not machine-locked in v1 (the `machine_hash` field and `machine.py` ship,
   so opting in later is a vendor-side token field — zero client releases).
3. Serial scope defaults are proposed in the EULA counsel packet: one named
   licensee, own machines, no machine binding, current-major-version scope,
   and non-transferable.
4. Only one-time serial numbers exist; subscriptions are not supported.
   Perpetual serial numbers are the default; an expiry is used only when the
   owner deliberately mints one.

## 10. Compiled verification core (2026-10-29)

Status: **implemented**. §1's non-goal list said "no obfuscation, no
tamper-resistance"; this section deliberately narrows that, and says exactly by
how much.

### 10.1 What changed

`verify_token` now delegates to `rhetoric_native`, a Rust extension
(`crates/rhetoric_native`, built by `scripts/build_native_license.py`) loaded
through `the_oracle._native`. The pure-Python verifier remains as the reference
and the fallback for a checkout without the build. Both paths are pinned to
identical `LicenseStatus` values across the full case matrix in
`tests/test_native_core.py`, so the compiled core can never *change* a verdict —
it only moves where the verdict is computed.

The production registry (`k2`) is compiled into the binary. `production_keys()`
exposes those bytes for a test-time pin against `keys.py`, because no test holds
the signing seed.

### 10.2 Why this raises the cost — and where it stops

Be precise about the guarantee, because the honest answer is that **no local
scheme is uncrackable**:

- What is now expensive: a bypass is no longer a one-line edit to readable
  Python. The decoder, the canonicalisation, the signature check, the expiry and
  machine-binding rules, and the key registry all live in compiled code that is
  rebuilt (new addresses, new inlining) on every release.
- What is still cheap for an attacker: patching the *call site* — replacing the
  import of `_native` or short-circuiting `verify_token` in Python. No amount of
  crypto fixes that, because the attacker owns the process. The defence is
  economic, not cryptographic: make each bypass path non-obvious, multiply
  independent call sites, and change the binary every release.
- What was explicitly rejected: phone-home validation (breaks the offline
  guarantee in §6 and the privacy posture), and anti-debugging tricks
  (`ptrace` checks, timing checksums). Those are theatre — they annoy paying
  users and cost a competent reverser minutes.

### 10.3 Build kinds

| Command | Feature | Trust anchors | Use |
| --- | --- | --- | --- |
| `scripts/build_native_license.py` | `test-keys` | `k2` + the published RFC 8032 test key | local dev, CI, the suite |
| `scripts/build_native_license.py --release` | none | `k2` only | shipped artifacts |

A release build ignores any caller-supplied key table: the parameter exists in
the signature so the Python side has one call shape, but the non-test build path
never reads it. `cargo build` with no features is the release build, so a
forgotten flag fails closed (unknown key, never "trusts anything").

`scripts/build_native_license.py --check` reports whether the installed artifact
is present and newer than the crate sources; source checkouts without Rust keep
working through the Python fallback.

### 10.4 Not done yet (ranked by value per unit of work)

1. ~~**Integrity attestation** — embed a build-time manifest of SHA-256 digests
   of the protected Python modules in the native core, have it re-hash them at
   the license gate, and refuse `valid` on a mismatch.~~ **DONE 2026-11-01** — see
   §11.
2. ~~**Multiple independent gates** — the doctor, the CLI and the pipeline
   already call `current_license()`; adding the export and render paths to that
   set makes a single patched call site insufficient.~~ **DONE 2026-11-01** — see
   §11.3.
3. **License-derived asset key** — encrypt one asset the pipeline genuinely
   needs (a prompt pack or a model config) under a key derived from the serial.
   A cracker must then reverse *what* the key unlocks, not just flip a boolean.
   Largest architectural change; only worth it if piracy is measured.
4. ~~**Stripped release binaries** — `strip = "symbols"` and LTO in the release
   profile.~~ **DONE 2026-11-01**: thin LTO, one codegen unit, stripped symbols.
   `panic = "abort"` is deliberately NOT set — a Rust panic must surface as a
   Python exception instead of killing the desktop process.

None of these make the software uncrackable; together they make a crack a
per-release maintenance burden rather than a one-afternoon edit. That is the
realistic ceiling for offline software, and the pricing/licensing strategy
should assume it.

## 11. Integrity attestation and gate depth (2026-11-01)

Status: **implemented**.

### 11.1 The manifest

`scripts/build_native_license.py --attest` hashes `PROTECTED_MODULES` — the
modules that carry the gates: `licensing/*.py`, `pipeline.py`,
`render_subprocess.py`, `audio/export_flac.py`, `cli.py` — into a sha256sum-style
file, points `RHETORIC_ATTEST_MANIFEST` at it, and cargo rebuilds. `build.rs`
turns that file into a Rust static (`MANIFEST`), so the expected digests are
compiled into the binary rather than shipped next to it.

At runtime the core **reads and hashes the files itself**; Python supplies only
the package directory. A patched install therefore cannot pass the digests it
would prefer — it would have to patch the check as well.

`--release` attests by default. `--no-attest` exists for a diagnostic build and
prints a warning; `--check` reports `attestation: enforced` or `not enforced (development build)`.

### 11.2 Enforcement

`licensing.current_license()` runs the check before reading the token store and
returns `state="integrity"` (with the reinstall remedy) on any mismatch. It is
memoised once per process, so a render does not re-hash the package per gate.
The check lives there rather than in `policy` because every gate resolves
`current_license` — a gate patched to skip the policy helper still receives an
`integrity` status.

### 11.3 Gate depth

`audio/export_flac.write_flac` and `render_subprocess.run_job` /
`run_preview_job` call `current_license()` directly. They deliberately do **not**
call `policy.require`: one shared helper is one place to patch, and these sites
are in different modules from the pipeline's entry check. Producing a file now
requires passing the pipeline gate *and* the output gate; the GUI's child
process must pass its own gate in addition to the parent's.

### 11.4 Limits (read before claiming more than this)

- `enforced: false` means *no manifest was compiled in* — a development build or
  a source checkout. It is never evidence that files are clean, and
  `tests/test_native_attestation.py` pins that reading.
- The **PyInstaller rehearsal build** (`packaging/linux/rhetoric.spec`) archives
  modules into `PYZ-00.pyz`, so there are no loose `.py` files to hash, and the
  spec does not bundle the extension. The attested distribution path is the
  wheel / offline-bundle install, where modules are real files. If a frozen
  bundle ever did carry an attested core, every entry would read as missing and
  the install would report `integrity` — fail-closed, not silent. A
  frozen-archive manifest would need a separate digest of the archive itself;
  it is not implemented.
- The compiled extension must ship in the wheel
  (`[tool.setuptools.package-data] the_oracle._native`). Without it an install
  falls back to the Python verifier and no attestation runs.
- A patched `licensing/__init__.py` can skip the check entirely. That is the
  same economic argument as §10.2: it raises cost, it is not a boundary.

### 11.5 Forensic licence tag in exported audio

`write_flac` stamps the verified `lic_id` into the FLAC Vorbis comments as
`RHETORIC_LICENSE`. It is the opaque licence UUID — never the licensee's name
or email — and it changes nothing the customer can do, so it costs no
usability. It makes a leaked render attributable to the licence it came from,
which deters sharing and supports takedowns. `metadata` is copied before the
tag is added; callers' dictionaries are never mutated.

### 11.6 Release pipelines carry the core

`scripts/release.py` builds the attested release core before it packs the
wheel and fails the release when cargo cannot produce it. A wheel without the
extension would silently fall back to the pure-Python verifier — the opposite
of what a release artifact is for — so the build refuses instead. CI has a
dedicated `native-license-core` job that builds the core, runs the parity,
attestation and gate tests, then proves `--attest` yields
`attestation: enforced`.
