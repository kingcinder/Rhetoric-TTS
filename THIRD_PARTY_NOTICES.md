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
| `annotated-doc` | installed metadata | MIT | [source](https://github.com/fastapi/annotated-doc) |
| `antlr4-python3-runtime` | installed metadata | BSD-3-Clause | [source](http://www.antlr.org) |
| `anyio` | installed metadata | MIT | [source](https://anyio.readthedocs.io/en/latest/) |
| `audioread` | installed metadata | MIT | [source](https://github.com/beetbox/audioread/issues) |
| `catalogue` | installed metadata | MIT | [source](https://github.com/explosion/catalogue) |
| `certifi` | installed metadata | MPL-2.0 | [source](https://github.com/certifi/python-certifi) |
| `cffi` | installed metadata | MIT-0 | [source](https://cffi.readthedocs.io/) |
| `cfgv` | installed metadata | MIT | [source](https://github.com/asottile/cfgv) |
| `charset-normalizer` | installed metadata | MIT | [source](https://github.com/jawah/charset_normalizer/blob/master/CHANGELOG.md) |
| `chatterbox-tts` | installed metadata | MIT | [source](https://github.com/resemble-ai/chatterbox) |
| `click` | installed metadata | BSD-3-Clause | [source](https://click.palletsprojects.com/page/changes/) |
| `cloudpickle` | installed metadata | BSD-3-Clause | [source](https://github.com/cloudpipe/cloudpickle) |
| `conformer` | installed metadata | MIT | [source](https://github.com/lucidrains/conformer) |
| `decorator` | installed metadata | BSD-3-Clause | — |
| `deepmultilingualpunctuation` | installed metadata | MIT | [source](https://github.com/oliverguhr/deepmultilingualpunctuation) |
| `diffusers` | installed metadata | Apache-2.0 | [source](https://github.com/huggingface/diffusers) |
| `distlib` | installed metadata | PSF-2.0 | [source](https://github.com/pypa/distlib) |
| `editdistpy` | installed metadata | MIT | [source](https://github.com/mammothb/editdistpy/blob/master/CHANGELOG.md) |
| `einops` | installed metadata | MIT | [source](https://github.com/arogozhnikov/einops) |
| `filelock` | installed metadata | MIT | [source](https://py-filelock.readthedocs.io) |
| `fsspec` | installed metadata | BSD-3-Clause | [source](https://filesystem-spec.readthedocs.io/en/latest/changelog.html) |
| `h11` | installed metadata | MIT | [source](https://github.com/python-hyper/h11) |
| `hf-xet` | installed metadata | Apache-2.0 | [source](https://huggingface.co/docs/hub/xet/index) |
| `httpcore` | installed metadata | BSD-3-Clause | [source](https://www.encode.io/httpcore) |
| `httpx` | installed metadata | BSD-3-Clause | [source](https://github.com/encode/httpx/blob/master/CHANGELOG.md) |
| `huggingface_hub` | installed metadata | Apache-2.0 | [source](https://github.com/huggingface/huggingface_hub) |
| `identify` | installed metadata | MIT | [source](https://github.com/pre-commit/identify) |
| `idna` | installed metadata | BSD-3-Clause | [source](https://github.com/kjd/idna/blob/master/HISTORY.md) |
| `importlib_metadata` | installed metadata | Apache-2.0 | [source](https://github.com/python/importlib_metadata) |
| `Jinja2` | installed metadata | BSD-3-Clause | [source](https://jinja.palletsprojects.com/changes/) |
| `joblib` | installed metadata | BSD-3-Clause | [source](https://joblib.readthedocs.io) |
| `lazy-loader` | installed metadata | BSD-3-Clause | [source](https://scientific-python.org/specs/spec-0001/) |
| `librosa` | installed metadata | ISC | [source](https://librosa.org) |
| `llvmlite` | installed metadata | BSD-2-Clause AND Apache-2.0 WITH LLVM-exception | [source](http://llvmlite.readthedocs.io) |
| `markdown-it-py` | installed metadata | MIT | [source](https://markdown-it-py.readthedocs.io) |
| `MarkupSafe` | installed metadata | BSD-3-Clause | [source](https://palletsprojects.com/donate) |
| `mdurl` | installed metadata | MIT | [source](https://github.com/executablebooks/mdurl) |
| `ml_dtypes` | installed metadata | Apache-2.0 | [source](https://github.com/jax-ml/ml_dtypes) |
| `mpmath` | installed metadata | BSD-3-Clause | [source](http://mpmath.org/) |
| `msgpack` | installed metadata | Apache-2.0 | [source](https://msgpack.org/) |
| `networkx` | installed metadata | BSD-3-Clause | [source](https://networkx.org/) |
| `nodeenv` | installed metadata | BSD-3-Clause | [source](https://github.com/ekalinin/nodeenv) |
| `numba` | installed metadata | BSD-3-Clause | [source](https://numba.pydata.org) |
| `numpy` | installed metadata | BSD-3-Clause | [source](https://numpy.org) |
| `omegaconf` | installed metadata | BSD-3-Clause | [source](https://github.com/omry/omegaconf) |
| `onnx` | installed metadata | Apache-2.0 | [source](https://onnx.ai/) |
| `packaging` | installed metadata | Apache-2.0 OR BSD-2-Clause | [source](https://packaging.pypa.io/) |
| `pillow` | installed metadata | MIT-CMU | [source](https://pillow.readthedocs.io/en/stable/releasenotes/index.html) |
| `platformdirs` | installed metadata | MIT | [source](https://platformdirs.readthedocs.io/en/latest/changelog.html) |
| `pooch` | installed metadata | BSD-3-Clause | [source](https://www.fatiando.org/pooch) |
| `pre_commit` | installed metadata | MIT | [source](https://github.com/pre-commit/pre-commit) |
| `protobuf` | installed metadata | BSD-3-Clause | [source](https://developers.google.com/protocol-buffers/) |
| `pycparser` | installed metadata | BSD-3-Clause | [source](https://github.com/eliben/pycparser) |
| `pydub` | installed metadata | MIT | [source](http://pydub.com) |
| `Pygments` | installed metadata | BSD-2-Clause | [source](https://pygments.org) |
| `pyloudnorm` | installed metadata | MIT | [source](https://github.com/csteinmetz1/pyloudnorm) |
| `PySide6` | installed metadata | LGPL-3.0 | [source](https://pyside.org) |
| `PySide6_Addons` | installed metadata | LGPL-3.0 | [source](https://pyside.org) |
| `PySide6_Essentials` | installed metadata | LGPL-3.0 | [source](https://pyside.org) |
| `python-discovery` | installed metadata | MIT | [source](https://github.com/tox-dev/python-discovery/releases) |
| `PyYAML` | installed metadata | MIT | [source](https://pyyaml.org/) |
| `regex` | installed metadata | Apache-2.0 AND CNRI-Python | [source](https://github.com/mrabarnett/mrab-regex) |
| `requests` | installed metadata | Apache-2.0 | [source](https://requests.readthedocs.io) |
| `resemble-perth` | installed metadata | MIT | [source](https://github.com/resemble-ai/perth) |
| `rich` | installed metadata | MIT | [source](https://rich.readthedocs.io/en/latest/) |
| `s3tokenizer` | installed metadata | Apache-2.0 | [source](https://github.com/xingchensong/S3Tokenizer) |
| `safetensors` | installed metadata | Apache-2.0 | [source](https://github.com/huggingface/safetensors) |
| `scikit-learn` | installed metadata | BSD-3-Clause | [source](https://scikit-learn.org) |
| `scipy` | installed metadata | BSD-3-Clause | [source](https://scipy.org/) |
| `setuptools` | installed metadata | MIT | [source](https://github.com/pypa/setuptools) |
| `shellingham` | installed metadata | ISC | [source](https://github.com/sarugaku/shellingham) |
| `shiboken6` | installed metadata | LGPL-3.0 | [source](https://pyside.org) |
| `sounddevice` | installed metadata | MIT | [source](https://python-sounddevice.readthedocs.io/) |
| `soundfile` | installed metadata | BSD-3-Clause | [source](https://github.com/bastibe/python-soundfile) |
| `soxr` | installed metadata | LGPL-2.1-or-later | [source](https://github.com/dofuuz/python-soxr) |
| `spacy_pkuseg` | installed metadata | MIT | [source](https://github.com/explosion/spacy-pkuseg) |
| `srsly` | installed metadata | MIT | [source](https://github.com/explosion/srsly) |
| `sympy` | installed metadata | BSD-3-Clause | [source](https://sympy.org) |
| `symspellpy` | installed metadata | MIT | [source](https://github.com/mammothb/symspellpy) |
| `threadpoolctl` | installed metadata | BSD-3-Clause | [source](https://github.com/joblib/threadpoolctl) |
| `tokenizers` | installed metadata | Apache-2.0 | [source](https://github.com/huggingface/tokenizers) |
| `torch` | installed metadata | BSD-3-Clause | [source](https://pytorch.org/) |
| `torchaudio` | installed metadata | BSD-3-Clause | [source](https://github.com/pytorch/audio) |
| `torchvision` | installed metadata | BSD-3-Clause | [source](https://github.com/pytorch/vision) |
| `tqdm` | installed metadata | MPL-2.0 | [source](https://tqdm.github.io) |
| `transformers` | installed metadata | Apache-2.0 | [source](https://github.com/huggingface/transformers) |
| `typer` | installed metadata | MIT | [source](https://github.com/fastapi/typer) |
| `typing_extensions` | installed metadata | PSF-2.0 | [source](https://github.com/python/typing_extensions/issues) |
| `urllib3` | installed metadata | MIT | [source](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst) |
| `virtualenv` | installed metadata | MIT | [source](https://thanks.dev/u/gh/gaborbernat) |
| `zipp` | installed metadata | MIT | [source](https://github.com/jaraco/zipp) |

## Required notices

The following notices must accompany the distribution. The standard
license texts are in `THIRD_PARTY_LICENSES/`.

- **PySide6 / shiboken6 / Qt** — LGPL-3.0. A proprietary application may use the LGPL path while keeping its own source proprietary, provided the LGPL-covered libraries remain replaceable/relinkable, their complete corresponding source is made available (or a written offer is given), and the LGPL notice and text accompany the distribution. A Qt commercial license is the alternative.
- **audio.cpp** — Copyright 2026 ShugoAI LLC. Apache-2.0. Modified by The Oracle's vendored patches; see scripts/patches/.
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
