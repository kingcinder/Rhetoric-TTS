# SentencePiece issue #1269 — decision note (2026-11-20)

Status re-checked 2026-11-20 against the upstream repository. No decision is made here; the release owner decides.

## What the issue is

- Upstream: google/sentencepiece issue #1269, published 2026-06-10. CWE-125 out-of-bounds read in the `precompiled_charsmap` Darts trie: a crafted trie root unit (bit 31 set in its label) passes the trie validator, then drives the traversal far past the array on `Encode`, crashing the process (SIGSEGV). CVSS 3.1 AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H — denial of service only, local attack, requires the attacker to supply the model file. No CVE covers this root-node bypass.
- Affected: sentencepiece 0.2.1 (the latest release at report time) and then-current HEAD.
- Not to be confused with CVE-2026-1260 (heap corruption via null-terminated `string_view` in `PrefixMatcher`), which is a different defect and is patched in 0.2.1. RC13 is not affected by CVE-2026-1260.

## Upstream fix status

- The fix shipped in sentencepiece **0.2.2** (2026-07-12). Release notes: "Model loading verifies darts-clone trie offsets to prevent segfaults on corrupted or malicious model files." Upstream regression test `RejectCorruptedModel1269` in `src/invalid_model_test.cc` verifies that `SentencePieceProcessor::Load` rejects a corrupted trie root instead of faulting. Hardening commit d685ef31 ("Sentencepiece security hardening fixes") carries the validator, recursion-depth limits, and the invalid-model tests.
- Latest PyPI release is **0.2.3** (2026-11-04/05). Vulnerability trackers list 0 known vulnerabilities for 0.2.2 and 0.2.3.
- The GitHub issue page as fetched 2026-11-20 showed no explicit "Closed" marker in the retrieved text, so formal issue closure is not confirmed from that fetch; the fix is nevertheless released and regression-tested upstream.

## RC13 status

- Bundled SentencePiece source in RC13 is **0.2.1** (`audio.cpp/external/sentencepiece/VERSION.txt`; `third_party/darts_clone/darts.h` SHA-256 `39a33ec8d08269edf8d1115cdfa8237eac47a9eaa02df49537fed25f085f8fc5`). Fix commit d685ef31 is **absent** from RC13 source (per `candidate-rc13/audiocpp-source-security-audit.json`, checked 2026-11-20).
- Exposure: the supported/bundled Chatterbox route does **not** load SentencePiece `.model` files — it uses `tokenizer.json` (`audio.cpp/model_specs/chatterbox.json`; `audio.cpp/src/models/chatterbox/text_tokenizer.cpp`; the wrapper does not pass a model-spec override). Residual scope: the generic audio.cpp CLI supports other model families and a model-spec override, so a user who manually loads an untrusted `.model` file can crash the process (DoS only). The C++ binary was not vulnerability-scanned.

## Option A — Record the release owner's supported model scope

Document that the only supported tokenization route is the bundled Chatterbox path (`tokenizer.json`); loading untrusted SentencePiece `.model` files through the generic CLI is out of scope and unsupported. No code change, no rebuild, no requalification. The residual stays documented: the generic CLI keeps the DoS exposure for anyone who loads an untrusted model, and no claim is made that the C++ binary is vulnerability-free. Cost: documentation only. Risk: the exposure remains in the shipped binary for out-of-scope use.

## Option B — Backport the upstream hardening and requalify a replacement candidate

Backport the upstream darts-clone trie-offset verification (0.2.2 / commit d685ef31, including the `RejectCorruptedModel1269` regression test) into RC13's bundled SentencePiece 0.2.1 source, rebuild audio.cpp, and requalify a **replacement candidate** — full render matrix, byte verification, and clean-install proof — before it can ship. The replacement candidate gets its own evidence set and checklist entries; RC13's evidence does not transfer. (The owner may instead choose a full upgrade of the bundled SentencePiece to 0.2.2 or 0.2.3 as the way to carry the hardening; that is a variant of this option, not a separate one.) Cost: real engineering plus a full requalification cycle; any backport must be verified not to change supported-route behavior. Risk: requalification finds new deltas, and the release slips.

## Decision required

Owner picks A or B (or the 0.2.2/0.2.3 upgrade variant of B). This note records the facts and the trade-offs only.
