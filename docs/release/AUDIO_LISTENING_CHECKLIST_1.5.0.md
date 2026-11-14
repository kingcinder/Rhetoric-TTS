# Audio Listening Checklist — Rhetoric 1.5.0

**Verdict: PENDING.** This sheet is for an independent human reviewer. Automated
metrics are recorded below only so the listener knows what was already checked;
they are not a verdict and must not be copied into one.

- Reviewer:
- Review date:
- Candidate commit:
- Playback chain (headphones/speakers, volume):
- Corpus packet location:

For each case, listen to the whole file and answer every line. Record defects
with timestamps. A case passes only if every line is "yes" except where noted.

## Case 1 — Short dialogue

- File / SHA-256: `sha256 0c13f8b349fc5421f7e990bddc07e3023494e3a22d75871004cc6aed390dcadb` (16.22 s)
- [ ] Words are intelligible; no missing or invented phrases
- [ ] Speaker identity and turn assignment are correct
- [ ] Pauses and transitions are usable; no clipped syllables
- [ ] No unexpected clipping, long silence, clicks, or severe artifacts
- [ ] Usable for the stated dialogue-rendering workflow
- Verdict (PASS / FAIL / PASS WITH NOTES):
- Timestamped defects:

## Case 2 — Long multi-speaker dialogue

- File / SHA-256: `sha256 e32fb36f01a4759acd721e73426a802f53945917c430a0d52c33daed41fbb0a0` (38.83 s)
- [ ] Words are intelligible; no missing or invented phrases
- [ ] Speaker identity and turn assignment are correct, including every switch
- [ ] Pauses and transitions are usable; no clipped syllables
- [ ] No unexpected clipping, long silence, clicks, or severe artifacts
- [ ] Usable for the stated dialogue-rendering workflow
- Verdict (PASS / FAIL / PASS WITH NOTES):
- Timestamped defects:

## Case 3 — SRT-timed dialogue

- File / SHA-256: `sha256 ac800d0e8d8956dc63ebd0d752877913915da14b92f257b89c2c343e101e9a78` (13.06 s)
- [ ] Words are intelligible; no missing or invented phrases
- [ ] Timing follows the SRT cues without swallowed or overlapping syllables
- [ ] Speaker identity and turn assignment are correct
- [ ] Pauses and transitions are usable; no clipped syllables
- [ ] No unexpected clipping, long silence, clicks, or severe artifacts
- [ ] Usable for the stated dialogue-rendering workflow
- Verdict (PASS / FAIL / PASS WITH NOTES):
- Timestamped defects:

## Case 4 — CJK text (judge this one first)

- File / SHA-256: `sha256 1b5bcdee168fd5285783239bb560f6b126edaced4e4d27afd758b82461457fd8` (4.10 s)
- Automated note (not a verdict): per-sentence stems run 0.74–1.00 s against
  3.0–4.6 s for the English/Arabic cases; speech may be severely rushed.
- [ ] Words are intelligible; no missing or invented phrases
- [ ] Pace is usable (the specific concern for this case)
- [ ] Speaker identity is correct
- [ ] No unexpected clipping, long silence, clicks, or severe artifacts
- [ ] Usable for the stated dialogue-rendering workflow
- Verdict (PASS / FAIL / PASS WITH NOTES):
- Timestamped defects:

## Case 5 — Right-to-left text (Arabic)

- File / SHA-256: `sha256 7167a92d4cbefbda13cae5da15a653fd1273e483d8c905657cf1c854c690b52e` (17.18 s)
- [ ] Words are intelligible; no missing or invented phrases
- [ ] Right-to-left text is spoken in the intended order
- [ ] Speaker identity and turn assignment are correct
- [ ] Pauses and transitions are usable; no clipped syllables
- [ ] No unexpected clipping, long silence, clicks, or severe artifacts
- [ ] Usable for the stated dialogue-rendering workflow
- Verdict (PASS / FAIL / PASS WITH NOTES):
- Timestamped defects:

## Case 6 — Messy input requiring correction

- File / SHA-256: `sha256 87583d51a42458e997ced59dcec9898d010c26de015d828cdce33bfabd691264` (28.02 s)
- Automated note (not a verdict): correction fixed capitalization, punctuation
  and some spelling; doubled words and "teh" were not fixed; "havent" became
  "haven". Judge the delivered text, not the intended text.
- [ ] Words are intelligible; no missing or invented phrases
- [ ] Speaker identity and turn assignment are correct
- [ ] Pauses and transitions are usable; no clipped syllables
- [ ] No unexpected clipping, long silence, clicks, or severe artifacts
- [ ] Usable for the stated dialogue-rendering workflow
- Verdict (PASS / FAIL / PASS WITH NOTES):
- Timestamped defects:

## Reviewer sign-off

- Overall verdict (PASS / FAIL / PASS WITH NOTES):
- Cases blocked or not reviewed:
- Reviewer signature / date:
