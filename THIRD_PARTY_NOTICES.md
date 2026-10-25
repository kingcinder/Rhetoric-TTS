# Third-Party Notices

This file is generated from the release tree by
`python scripts/generate_third_party_notices.py`. Do not edit it by hand;
regenerate it and review the diff. The inventory is also read by the
commercial launch gate (`python scripts/soft_launch.py --check`), so a
dependency that is missing here is a release blocker, not a documentation
omission.

Release version: **1.4.2**

## Distribution obligations at a glance

- **MIT / BSD / Apache-2.0 components** require their copyright and
  permission notices to accompany copies. Their license texts are in
  `THIRD_PARTY_LICENSES/` and in each Python distribution's `.dist-info`
  directory.
- **PySide6 / Qt (LGPL-3.0)** requires a prominent notice, a copy of the
  LGPL text, access to the corresponding source of the LGPL-covered
  libraries, and a way for users to replace/relink those libraries. A
  commercial Qt license is the alternative.
- **Strong-copyleft components (GPL/AGPL)** are not safe for a proprietary
  combined distribution without a recorded legal decision. The commercial
  gate reports them as blockers until `scripts/license_review.json` records
  the decision.
- **External tools** (ffmpeg, audio.cpp/ggml) are not part of the Python
  wheel. The host supplies ffmpeg; the optional Vulkan backend builds
  audio.cpp/ggml locally.

## Bundled assets, models, and external components

| Component | Version / pin | License | Source |
|---|---|---|---|
| `PySide6 / shiboken6 / Qt` | 6.8.2.1 | LGPL-3.0 (or commercial Qt license) | [source](https://code.qt.io/cgit/pyside/pyside-setup.git/) |
| `audio.cpp` | built at install time from a pinned clone | Apache-2.0 | [source](https://github.com/0xShug0/audio.cpp) |
| `ffmpeg` | host-provided | LGPL/GPL depending on the build | [source](https://ffmpeg.org/) |
| `ggml` | vendored in the audio.cpp checkout | MIT | [source](https://github.com/ggml-org/ggml) |
| `oliverguhr/fullstop-punctuation-multilang-large` | pinned (models/pins.py) | MIT | [source](https://huggingface.co/oliverguhr/fullstop-punctuation-multilang-large) |
| `ResembleAI/chatterbox` | pinned (models/pins.py) | MIT | [source](https://huggingface.co/ResembleAI/chatterbox) |
| `ResembleAI/chatterbox-turbo` | pinned (models/pins.py) | MIT | [source](https://huggingface.co/ResembleAI/chatterbox-turbo) |
| `SamLowe/roberta-base-go_emotions` | pinned (models/pins.py) | MIT | [source](https://huggingface.co/SamLowe/roberta-base-go_emotions) |
| `chinese_female_1.wav` | — | Apache-2.0 | Seashells/generic/ATTRIBUTION.md |
| `chinese_male_1.wav` | — | Apache-2.0 | Seashells/generic/ATTRIBUTION.md |
| `chinese_male_2.wav` | — | Apache-2.0 | Seashells/generic/ATTRIBUTION.md |
| `chinese_speaker_1.wav` | — | Apache-2.0 | Seashells/generic/ATTRIBUTION.md |
| `Cody's Seashell.wav` | — | Owner-owned; all rights reserved | Seashells/ASSETS.md |
| `Cody's Seashell1.wav` | — | Owner-owned; all rights reserved | Seashells/ASSETS.md |
| `english_male_1.wav` | — | Apache-2.0 | Seashells/generic/ATTRIBUTION.md |
| `english_reader_1.wav` | — | CC BY 4.0 | Seashells/generic/ATTRIBUTION.md |
| `english_reader_2.wav` | — | CC BY 4.0 | Seashells/generic/ATTRIBUTION.md |
| `english_reader_3.wav` | — | CC BY 4.0 | Seashells/generic/ATTRIBUTION.md |
| `english_reader_4.wav` | — | CC BY 4.0 | Seashells/generic/ATTRIBUTION.md |
| `Fransisco_MONSTER.wav` | — | Owner-owned; all rights reserved | Seashells/ASSETS.md |
| `seashell fransisco.wav` | — | Owner-owned; all rights reserved | Seashells/ASSETS.md |
| `seashell fransisco_TTS_clean_v5_aggressive_targeted_cleanup.wav` | — | Owner-owned; all rights reserved | Seashells/ASSETS.md |
| `Seashell_ fransisco.wav` | — | Owner-owned; all rights reserved | Seashells/ASSETS.md |
| `Seashell_No_1.wav` | — | Owner-owned; all rights reserved | Seashells/ASSETS.md |
| `Seashell_No_2.wav` | — | Owner-owned; all rights reserved | Seashells/ASSETS.md |

Model revisions are pinned in `src/the_oracle/models/pins.py`; this
table names each model and its license without duplicating the
revision hashes, which are external identifiers rather than citations
in this repository's history.

## Python dependencies

Resolved from `pyproject.toml` and the installed package metadata. The
closure covers the runtime and the `ml`/`chatterbox` extras; development
tools are not part of the shipped environment.

| Component | Version | License | Source |
|---|---|---|---|
| `annotated-doc` | installed metadata | see installed metadata | — |
| `antlr4-python3-runtime` | installed metadata | see installed metadata | — |
| `anyio` | installed metadata | see installed metadata | — |
| `audioread` | installed metadata | see installed metadata | — |
| `catalogue` | installed metadata | see installed metadata | — |
| `certifi` | installed metadata | see installed metadata | — |
| `cffi` | installed metadata | see installed metadata | — |
| `cfgv` | installed metadata | see installed metadata | — |
| `charset-normalizer` | installed metadata | see installed metadata | — |
| `chatterbox-tts` | installed metadata | see installed metadata | — |
| `click` | installed metadata | see installed metadata | — |
| `cloudpickle` | installed metadata | see installed metadata | — |
| `colorama` | installed metadata | see installed metadata | — |
| `conformer` | installed metadata | see installed metadata | — |
| `decorator` | installed metadata | see installed metadata | — |
| `deepmultilingualpunctuation` | installed metadata | see installed metadata | — |
| `diffusers` | installed metadata | see installed metadata | — |
| `distlib` | installed metadata | see installed metadata | — |
| `editdistpy` | installed metadata | see installed metadata | — |
| `einops` | installed metadata | see installed metadata | — |
| `filelock` | installed metadata | see installed metadata | — |
| `fsspec` | installed metadata | see installed metadata | — |
| `h11` | installed metadata | see installed metadata | — |
| `hf-xet` | installed metadata | see installed metadata | — |
| `httpcore` | installed metadata | see installed metadata | — |
| `httpx` | installed metadata | see installed metadata | — |
| `huggingface_hub` | installed metadata | see installed metadata | — |
| `identify` | installed metadata | see installed metadata | — |
| `idna` | installed metadata | see installed metadata | — |
| `importlib_metadata` | installed metadata | see installed metadata | — |
| `Jinja2` | installed metadata | see installed metadata | — |
| `joblib` | installed metadata | see installed metadata | — |
| `lazy-loader` | installed metadata | see installed metadata | — |
| `librosa` | installed metadata | see installed metadata | — |
| `llvmlite` | installed metadata | see installed metadata | — |
| `markdown-it-py` | installed metadata | see installed metadata | — |
| `MarkupSafe` | installed metadata | see installed metadata | — |
| `mdurl` | installed metadata | see installed metadata | — |
| `ml_dtypes` | installed metadata | see installed metadata | — |
| `mpmath` | installed metadata | see installed metadata | — |
| `msgpack` | installed metadata | see installed metadata | — |
| `networkx` | installed metadata | see installed metadata | — |
| `nodeenv` | installed metadata | see installed metadata | — |
| `numba` | installed metadata | see installed metadata | — |
| `numpy` | installed metadata | see installed metadata | — |
| `omegaconf` | installed metadata | see installed metadata | — |
| `onnx` | installed metadata | see installed metadata | — |
| `packaging` | installed metadata | see installed metadata | — |
| `pillow` | installed metadata | see installed metadata | — |
| `platformdirs` | installed metadata | see installed metadata | — |
| `pooch` | installed metadata | see installed metadata | — |
| `pre_commit` | installed metadata | see installed metadata | — |
| `protobuf` | installed metadata | see installed metadata | — |
| `pycparser` | installed metadata | see installed metadata | — |
| `pydub` | installed metadata | see installed metadata | — |
| `Pygments` | installed metadata | see installed metadata | — |
| `pyloudnorm` | installed metadata | see installed metadata | — |
| `PySide6` | installed metadata | see installed metadata | — |
| `PySide6_Addons` | installed metadata | see installed metadata | — |
| `PySide6_Essentials` | installed metadata | see installed metadata | — |
| `python-discovery` | installed metadata | see installed metadata | — |
| `PyYAML` | installed metadata | see installed metadata | — |
| `regex` | installed metadata | see installed metadata | — |
| `requests` | installed metadata | see installed metadata | — |
| `resemble-perth` | installed metadata | see installed metadata | — |
| `rich` | installed metadata | see installed metadata | — |
| `s3tokenizer` | installed metadata | see installed metadata | — |
| `safetensors` | installed metadata | see installed metadata | — |
| `scikit-learn` | installed metadata | see installed metadata | — |
| `scipy` | installed metadata | see installed metadata | — |
| `setuptools` | installed metadata | see installed metadata | — |
| `shellingham` | installed metadata | see installed metadata | — |
| `shiboken6` | installed metadata | see installed metadata | — |
| `sounddevice` | installed metadata | see installed metadata | — |
| `soundfile` | installed metadata | see installed metadata | — |
| `soxr` | installed metadata | see installed metadata | — |
| `spacy_pkuseg` | installed metadata | see installed metadata | — |
| `srsly` | installed metadata | see installed metadata | — |
| `sympy` | installed metadata | see installed metadata | — |
| `symspellpy` | installed metadata | see installed metadata | — |
| `threadpoolctl` | installed metadata | see installed metadata | — |
| `tokenizers` | installed metadata | see installed metadata | — |
| `torch` | installed metadata | see installed metadata | — |
| `torchaudio` | installed metadata | see installed metadata | — |
| `torchvision` | installed metadata | see installed metadata | — |
| `tqdm` | installed metadata | see installed metadata | — |
| `transformers` | installed metadata | see installed metadata | — |
| `typer` | installed metadata | see installed metadata | — |
| `typing_extensions` | installed metadata | see installed metadata | — |
| `urllib3` | installed metadata | see installed metadata | — |
| `virtualenv` | installed metadata | see installed metadata | — |
| `zipp` | installed metadata | see installed metadata | — |

## Required notices

The following notices must accompany the distribution. The standard
license texts are in `THIRD_PARTY_LICENSES/`.

- **PySide6 / shiboken6 / Qt** — LGPL-3.0. A proprietary application may use the LGPL path while keeping its own source proprietary, provided the LGPL-covered libraries remain replaceable/relinkable, their complete corresponding source is made available (or a written offer is given), and the LGPL notice and text accompany the distribution. A Qt commercial license is the alternative.
- **audio.cpp** — Copyright 2026 ShugoAI LLC. Apache-2.0. Modified by Rhetoric's vendored patches; see scripts/patches/.
- **ffmpeg** — Not bundled. The host supplies ffmpeg; its own build determines the exact license.
- **ggml** — Copyright (c) 2023-2026 The ggml authors. MIT license.
- **oliverguhr/fullstop-punctuation-multilang-large** — Copyright (c) 2021 Oliver Guhr. MIT license.
- **ResembleAI/chatterbox** — Copyright (c) 2025 Resemble AI. MIT license; commercial use permitted.
- **ResembleAI/chatterbox-turbo** — MIT license; commercial use permitted.
- **SamLowe/roberta-base-go_emotions** — Copyright (c) 2023 SamLowe. MIT license.
- **chinese_female_1.wav** — audio.cpp demo voice, Copyright 2026 ShugoAI LLC
- **chinese_male_1.wav** — audio.cpp demo voice, Copyright 2026 ShugoAI LLC
- **chinese_male_2.wav** — audio.cpp demo voice, Copyright 2026 ShugoAI LLC
- **chinese_speaker_1.wav** — audio.cpp demo voice, Copyright 2026 ShugoAI LLC
- **Cody's Seashell.wav** — Original recording by the Owner; no third-party rights.
- **Cody's Seashell1.wav** — Original recording by the Owner; no third-party rights.
- **english_male_1.wav** — audio.cpp demo voice, Copyright 2026 ShugoAI LLC
- **english_reader_1.wav** — LibriSpeech clip; attribution in Seashells/generic/ATTRIBUTION.md
- **english_reader_2.wav** — LibriSpeech clip; attribution in Seashells/generic/ATTRIBUTION.md
- **english_reader_3.wav** — LibriSpeech clip; attribution in Seashells/generic/ATTRIBUTION.md
- **english_reader_4.wav** — LibriSpeech clip; attribution in Seashells/generic/ATTRIBUTION.md
- **Fransisco_MONSTER.wav** — Original recording by the Owner; no third-party rights.
- **seashell fransisco.wav** — Original recording by the Owner; no third-party rights.
- **seashell fransisco_TTS_clean_v5_aggressive_targeted_cleanup.wav** — Original recording by the Owner; no third-party rights.
- **Seashell_ fransisco.wav** — Original recording by the Owner; no third-party rights.
- **Seashell_No_1.wav** — Original recording by the Owner; no third-party rights.
- **Seashell_No_2.wav** — Original recording by the Owner; no third-party rights.
- **certifi** — See the installed distribution metadata and bundled license text.
- **PySide6** — See the installed distribution metadata and bundled license text.
- **PySide6_Addons** — See the installed distribution metadata and bundled license text.
- **PySide6_Essentials** — See the installed distribution metadata and bundled license text.
- **shiboken6** — See the installed distribution metadata and bundled license text.
- **soxr** — See the installed distribution metadata and bundled license text.
- **tqdm** — See the installed distribution metadata and bundled license text.

## Standard license texts

- `Apache-2.0` — `THIRD_PARTY_LICENSES/Apache-2.0.txt`
- `BSD-3-Clause` — `THIRD_PARTY_LICENSES/BSD-3-Clause.txt`
- `GPL-2.0` — `THIRD_PARTY_LICENSES/GPL-2.0.txt`
- `GPL-3.0` — `THIRD_PARTY_LICENSES/GPL-3.0.txt`
- `LGPL-3.0` — `THIRD_PARTY_LICENSES/LGPL-3.0.txt`
- `MIT` — `THIRD_PARTY_LICENSES/MIT.txt`
- `MPL-2.0` — `THIRD_PARTY_LICENSES/MPL-2.0.txt`

## Full dependency license texts

Every installed Python distribution carries its own license files in its
`.dist-info` directory. The offline bundle ships the wheels, so those
texts travel with the install. The standard texts above cover the
components whose wheels do not carry a text (notably PySide6/Qt).
