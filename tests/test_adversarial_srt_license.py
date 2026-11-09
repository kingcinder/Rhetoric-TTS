"""Adversarial pins for the subtitle ingester and the license token parser.

Both surfaces consume files a user can download or receive from anyone:
subtitle files from the open internet, and license tokens by email. The
pins are behavioral boundaries, verified against the current code: hostile
timings must degrade into clamped output, markup must never survive into
speech text, and malformed tokens must be rejected, never crash.
"""
from __future__ import annotations

import re

import pytest

from the_oracle import srt_ingest
from the_oracle.licensing import tokens


def test_reversed_and_overlapping_cues_never_produce_bad_pauses():
    text = (
        "1\n00:00:10,000 --> 00:00:05,000\nReversed cue.\n\n"
        "2\n00:00:06,000 --> 00:00:07,000\nOverlapping cue.\n\n"
        "3\n01:00:00,000 --> 01:00:02,000\nFar future cue.\n"
    )
    script, cue_count, _speakers = srt_ingest.srt_to_dialogue_text(text)
    assert cue_count == 3
    for match in re.finditer(r"\[pause=(-?\d+)\]", script):
        assert 0 <= int(match.group(1)) <= 2000


def test_out_of_range_clock_fields_do_not_crash():
    # Minutes of 99 are not valid SRT, but the tolerant parser accepts the
    # shape; conversion must still complete.
    text = "1\n00:99:00,000 --> 00:99:02,000\nNinety-nine minutes.\n"
    script, cue_count, _ = srt_ingest.srt_to_dialogue_text(text)
    assert cue_count == 1
    assert "Ninety-nine minutes." in script


def test_markup_bomb_is_stripped_from_speech_text():
    payload = "<b>" * 100 + "Hello" + "</b>" * 100
    text = f"1\n00:00:01,000 --> 00:00:02,000\n{payload}\n"
    script, _, _ = srt_ingest.srt_to_dialogue_text(text)
    assert "Hello" in script
    assert "<b>" not in script


def test_many_cues_parse_completely():
    blocks = [
        f"{i}\n00:{i // 60:02d}:{i % 60:02d},000 --> 00:{i // 60:02d}:{i % 60:02d},500\nLine {i}.\n"
        for i in range(600)
    ]
    cues = srt_ingest.parse_srt("\n".join(blocks))
    assert len(cues) == 600


@pytest.mark.parametrize("junk", [
    "",
    "ORACLE1",
    "ORACLE1.",
    "ORACLE1..",
    "ORACLE2.aaaa.bbbb",
    "ORACLE1.!!!.???",
    "ORACLE1." + "A" * 100000 + ".BBBB",
    "ORACLE1.ééé.ééé",
    "not-a-token",
    "ORACLE1.AAAA.BBBB.extra",
])
def test_license_token_parse_rejects_junk_without_raising(junk: str):
    assert tokens.parse(junk) is None
