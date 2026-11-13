# Generic Voices — Attribution

The clips in this folder are **bundled generic voice references** for The
Rhetoric's "Default Voices" picker. They are **not** user recordings; they are
third-party reference clips redistributed with permission under their
respective licenses. Rhetoric renders every voice through Chatterbox voice
cloning, so these clips condition the model the same way any user-recorded
reference does.

Language note: a reference clip conditions the model on the *speaker's
timbre*, and the cloned voice then speaks the rendered text. English clips
yield English narration without accent influence; clips recorded in other
languages yield that speaker's voice with a corresponding accent — pick
accordingly. English-conditioned clips are listed first in the voice picker
and are the CLI's default fallback.

## audio.cpp demo voices (Apache License 2.0)

Copyright 2026 ShugoAI LLC — source:
[audio.cpp](https://github.com/0xShug0/audio.cpp) (`webui/voice/`), license
https://www.apache.org/licenses/LICENSE-2.0. The demo clips' own prompt
texts (see `audio.cpp/webui/voice/prompt_text`) confirm the languages below.

| This file | Source file (audio.cpp `webui/voice/`) | Speaker |
|---|---|---|
| `english_male_1.wav` | `demo_01_man.wav` | male, English ("Cemo") |
| `confidant_chinese_male_1.wav` | `demo_3_man.wav` | male, Chinese |
| `chinese_male_2.wav` | `zh-Bowen_man.wav` | male, Chinese |
| `chinese_female_1.wav` | `demo_02_woman.wav` | female, Chinese |
| `exuberant_chinese_female.wav` | `ref-w1.wav` | Chinese (gender unlabeled in source) |
