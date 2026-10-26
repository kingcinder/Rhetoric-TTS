# Real Audio Acceptance — Rhetoric 1.5.0

**Status: PENDING.** No 1.5.0 fixed-corpus production render or human
listening verdict is recorded here. Earlier 1.4.2 outputs are historical and
do not qualify this candidate.

## Required automated corpus

Record each render's source commit, command, backend, runtime, output path,
SHA-256, decode result, sample rate, channels, duration, peak/clipping,
silence gaps, loudness (LUFS), and deterministic comparison result.

| Case | Status |
|---|---|
| Short dialogue | PENDING |
| Long multi-speaker dialogue | PENDING |
| SRT-timed dialogue | PENDING |
| CJK text | PENDING |
| Right-to-left text | PENDING |
| Messy input requiring correction | PENDING |

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
