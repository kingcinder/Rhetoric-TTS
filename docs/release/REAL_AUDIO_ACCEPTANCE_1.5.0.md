# Real Audio Acceptance — Rhetoric 1.5.0

**Status: AUTOMATED CORPUS COMPLETE 2026-11-11; human listening verdict
still PENDING.** The six fixed-corpus production renders below were made
from release/1.5.0-final @ b9e6171 (host CPU build, seed 1500, production
settings). Earlier 1.4.2 outputs are historical and do not qualify this
candidate.

## Required automated corpus

Record each render's source commit, command, backend, runtime, output path,
SHA-256, decode result, sample rate, channels, duration, peak/clipping,
silence gaps, loudness (LUFS), and deterministic comparison result.

| Case | Status |
|---|---|
| Short dialogue | RENDERED 2026-11-11 — 16.22 s, 24 kHz mono FLAC, decode clean, peak under clipping, LUFS −19.86, watermark detector 1.0, sha256 0c13f8b349fc5421f7e990bddc07e3023494e3a22d75871004cc6aed390dcadb |
| Long multi-speaker dialogue | RENDERED 2026-11-11 — 38.83 s, decode clean, LUFS −20.52, watermark 1.0, sha256 e32fb36f01a4759acd721e73426a802f53945917c430a0d52c33daed41fbb0a0 |
| SRT-timed dialogue | RENDERED 2026-11-11 — 13.06 s, decode clean, LUFS −20.36, watermark 1.0, sha256 ac800d0e8d8956dc63ebd0d752877913915da14b92f257b89c2c343e101e9a78 |
| CJK text | RENDERED 2026-11-11 — 4.10 s, decode clean, LUFS −20.33, watermark 1.0, sha256 1b5bcdee168fd5285783239bb560f6b126edaced4e4d27afd758b82461457fd8. NOTE: per-sentence stems run 0.74–1.00 s against 3.0–4.6 s for the English/Arabic cases — speech is likely severely rushed; the human listener is asked to judge this case first. |
| Right-to-left text | RENDERED 2026-11-11 — 17.18 s, decode clean, LUFS −21.72, watermark 1.0, sha256 7167a92d4cbefbda13cae5da15a653fd1273e483d8c905657cf1c854c690b52e |
| Messy input requiring correction | RENDERED 2026-11-11 — 28.02 s, decode clean, LUFS −19.53, watermark 1.0, sha256 87583d51a42458e997ced59dcec9898d010c26de015d828cdce33bfabd691264. Correction log: capitalization, punctuation, and some spelling fixed; doubled words and "teh" NOT fixed; "havent" became "haven" — partial correction, recorded as-is for the listener's judgment. |

Corpus inputs, outputs, and the listening sheet live with the release
evidence (`audio-corpus-1.5.0` on the build host; packet copy in the
operator's workspace). Fixed seed 1500 was used for every case; renders
are one-shot production runs, not byte-reproduced duplicates.

For fixed-seed runs, record whether identical inputs produce identical output
bytes or explain the expected nondeterministic fields. Confirm the Perth
watermark with a supported detector; decode success alone does not prove it.

## Independent listening checklist

The verdict must be supplied by an independent human reviewer. Record
reviewer, review date, candidate commit, output hashes, and defects. For each
case, check:

- words are intelligible, with no missing or invented phrases;
- speaker identity and turn assignment are correct;
- pauses and transitions are usable and do not clip syllables;
- no unexpected clipping, long silence, clicks, or severe artifacts;
- the result is usable for the stated dialogue-rendering workflow.

**Human verdict: PENDING.** Do not replace this field with automated metrics
or a model-generated assessment.
