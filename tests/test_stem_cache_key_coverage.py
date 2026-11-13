"""Every input that changes the audio participates in the stem cache key.

A cached stem may only satisfy a render that asked for the same audio. The key
is built by ``build_chunk_hash``: speaker, the repaired (post-correction) text,
the engine key (backend + model variant), the voice settings, the engine
version, the reference clip's content hash, and the sampling seed.

Correction mode is covered through the text: the key hashes the repaired text
that synthesis actually receives, so any correction that changes what is spoken
changes the key, and a correction that yields identical text cannot change the
audio.
"""

from __future__ import annotations

import pytest

from rhetoric.utils.hashing import build_chunk_hash

BASE = {
    "speaker": "A",
    "repaired_text": "hello there",
    "engine_key": "chatterbox:standard",
    "engine_params": {"language": "en", "cfg_weight": 0.5, "temperature": 0.8},
    "engine_version": "1.0.0",
    "reference_audio_hash": "ref-hash",
    "seed": 1,
}


def test_identical_inputs_share_a_key() -> None:
    assert build_chunk_hash(**BASE) == build_chunk_hash(**BASE)


@pytest.mark.parametrize(
    ("label", "change"),
    [
        ("text", {"repaired_text": "hello there!"}),
        ("speaker", {"speaker": "B"}),
        ("model variant", {"engine_key": "chatterbox:multilingual"}),
        ("backend", {"engine_key": "vulkan:chatterbox:standard"}),
        ("voice settings", {"engine_params": {**BASE["engine_params"], "cfg_weight": 0.7}}),
        ("engine version", {"engine_version": "1.0.1"}),
        ("reference clip", {"reference_audio_hash": "other-ref-hash"}),
        ("seed", {"seed": 2}),
        ("no seed vs seed", {"seed": None}),
    ],
)
def test_every_audio_input_changes_the_key(label: str, change: dict) -> None:
    changed = {**BASE, **change}
    assert build_chunk_hash(**changed) != build_chunk_hash(**BASE), label
