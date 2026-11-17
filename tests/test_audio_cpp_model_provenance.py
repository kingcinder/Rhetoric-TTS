from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "record_audio_cpp_model_provenance.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("rhetoric_model_provenance", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Response:
    headers = {"X-Repo-Commit": "c" * 40}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None


def test_records_immutable_hugging_face_revision_and_model_hash(tmp_path: Path) -> None:
    tool = _load_script()
    model = tmp_path / "chatterbox-q8_0.gguf"
    model.write_bytes(b"model bytes")
    calls = []

    def fake_urlopen(request, *, timeout):
        calls.append((request.full_url, request.get_method(), timeout))
        return _Response()

    record = tool.record_model_provenance(
        model,
        {
            "files": ["Chatterbox-GGUF/chatterbox-q8_0.gguf"],
            "download": {"repo": "audio-cpp/audio.cpp-gguf", "revision": "main"},
        },
        endpoint="https://huggingface.test",
        open_url=fake_urlopen,
    )

    assert record["revision"] == "c" * 40
    assert record["sha256"] == hashlib.sha256(b"model bytes").hexdigest()
    assert json.loads(Path(f"{model}.rhetoric-provenance.json").read_text()) == record
    assert calls == [(
        "https://huggingface.test/audio-cpp/audio.cpp-gguf/resolve/main/Chatterbox-GGUF/chatterbox-q8_0.gguf",
        "HEAD",
        60,
    )]


def test_refuses_to_record_mutable_or_missing_hugging_face_revision(tmp_path: Path) -> None:
    tool = _load_script()
    model = tmp_path / "chatterbox-q8_0.gguf"
    model.write_bytes(b"model bytes")

    with pytest.raises(tool.ProvenanceError, match="immutable"):
        tool.record_model_provenance(
            model,
            {
                "files": ["Chatterbox-GGUF/chatterbox-q8_0.gguf"],
                "download": {"repo": "audio-cpp/audio.cpp-gguf", "revision": "main"},
            },
            endpoint="https://huggingface.test",
            open_url=lambda *_args, **_kwargs: type("Response", (), {"__enter__": lambda self: self, "__exit__": lambda *a: None, "headers": {}})(),
        )


def test_uses_model_info_sha_when_resolve_head_omits_commit_header(tmp_path: Path) -> None:
    tool = _load_script()
    model = tmp_path / "chatterbox-q8_0.gguf"
    model.write_bytes(b"model bytes")
    calls = []

    class ApiResponse(_Response):
        headers = {}

        def read(self):
            return json.dumps({"sha": "d" * 40}).encode("utf-8")

    class HeadResponse(_Response):
        headers = {}

    def fake_urlopen(request, *, timeout):
        calls.append((request.full_url, request.get_method(), timeout))
        return HeadResponse() if request.get_method() == "HEAD" else ApiResponse()

    record = tool.record_model_provenance(
        model,
        {
            "files": ["Chatterbox-GGUF/chatterbox-q8_0.gguf"],
            "download": {"repo": "audio-cpp/audio.cpp-gguf", "revision": "main"},
        },
        endpoint="https://huggingface.test",
        open_url=fake_urlopen,
    )

    assert record["revision"] == "d" * 40
    assert record["sha256"] == hashlib.sha256(b"model bytes").hexdigest()
    assert calls == [
        (
            "https://huggingface.test/audio-cpp/audio.cpp-gguf/resolve/main/"
            "Chatterbox-GGUF/chatterbox-q8_0.gguf",
            "HEAD",
            60,
        ),
        ("https://huggingface.test/api/models/audio-cpp/audio.cpp-gguf?revision=main", "GET", 60),
    ]
