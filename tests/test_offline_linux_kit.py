from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_builder():
    path = REPO_ROOT / "scripts" / "build_offline_linux_kit.py"
    spec = importlib.util.spec_from_file_location("rhetoric_offline_linux_kit", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_model_provenance(model: Path, revision: str = "a" * 40) -> None:
    (model.parent / f"{model.name}.rhetoric-provenance.json").write_text(
        json.dumps({
            "format": 1,
            "repo": "audio-cpp/audio.cpp-gguf",
            "revision": revision,
            "file": model.name,
            "sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
        }),
        encoding="utf-8",
    )


def _write_binary_provenance(builder, binary: Path) -> None:
    Path(f"{binary}.rhetoric-provenance.json").write_text(
        json.dumps({
            "format": 1,
            "source_commit": builder.AUDIOCPP_COMMIT,
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        }),
        encoding="utf-8",
    )


def test_model_stage_contains_only_pinned_standard_cpu_and_vulkan_models(tmp_path: Path) -> None:
    builder = _load_builder()
    revision = builder.CHATTERBOX_REVISION
    source = tmp_path / "source-hub"
    snapshot = source / "models--ResembleAI--chatterbox" / "snapshots" / revision
    snapshot.mkdir(parents=True)
    for name in builder.CHATTERBOX_FILES:
        (snapshot / name).write_bytes(name.encode())
    (snapshot / "t3_mtl23ls_v2.safetensors").write_bytes(b"unused multilingual weight")
    refs = source / "models--ResembleAI--chatterbox" / "refs"
    refs.mkdir()
    (refs / "main").write_text(revision)
    gguf = tmp_path / "chatterbox-q8_0.gguf"
    gguf.write_bytes(b"vulkan model")
    _write_model_provenance(gguf)

    out = tmp_path / "models"
    manifest = builder.stage_models(source, gguf, out)

    staged = out / "hf_cache" / "models--ResembleAI--chatterbox" / "snapshots" / revision
    assert {p.name for p in staged.iterdir()} == set(builder.CHATTERBOX_FILES)
    assert (out / "hf_cache" / "models--ResembleAI--chatterbox" / "refs" / "main").read_text() == revision
    assert (out / "Chatterbox-GGUF" / "chatterbox-q8_0.gguf").read_bytes() == b"vulkan model"
    assert manifest["cpu_model"]["repo"] == "ResembleAI/chatterbox"
    assert manifest["cpu_model"]["revision"] == revision
    assert manifest["vulkan_model"]["file"] == "chatterbox-q8_0.gguf"
    assert "Copyright (c) 2025 Resemble AI" in (out / "MODEL_NOTICES.md").read_text()
    mit = (out / "THIRD_PARTY_LICENSES" / "ResembleAI-Chatterbox-MIT.txt").read_text()
    assert "Copyright (c) 2025 Resemble AI" in mit
    assert "<year> <copyright holders>" not in mit
    assert manifest["vulkan_model"]["revision"] == "a" * 40


def test_model_stage_fails_when_pinned_cpu_checkpoint_is_incomplete(tmp_path: Path) -> None:
    builder = _load_builder()
    source = tmp_path / "source-hub"
    snapshot = source / "models--ResembleAI--chatterbox" / "snapshots" / builder.CHATTERBOX_REVISION
    snapshot.mkdir(parents=True)
    refs = source / "models--ResembleAI--chatterbox" / "refs"
    refs.mkdir()
    (refs / "main").write_text(builder.CHATTERBOX_REVISION)
    (snapshot / "t3_cfg.safetensors").write_bytes(b"one file only")
    gguf = tmp_path / "model.gguf"
    gguf.write_bytes(b"gguf")
    _write_model_provenance(gguf)

    with pytest.raises(builder.BuildError, match="missing required Chatterbox files"):
        builder.stage_models(source, gguf, tmp_path / "out")


def test_model_install_script_seeds_user_hub_cache_and_system_vulkan_model() -> None:
    builder = _load_builder()
    script = builder.install_script_text()

    assert 'models/hf_cache/models--ResembleAI--chatterbox' in script
    assert 'models/Chatterbox-GGUF/chatterbox-q8_0.gguf' in script
    assert "hf_cache=$target_home/.cache/huggingface/hub" in script
    assert "install -d -m 0755 /opt/rhetoric/models/Chatterbox-GGUF" in script
    assert script.index("Existing Vulkan model differs") < script.index('dpkg -i "$ROOT"/rhetoric_1.5.0_amd64.deb')


def test_uninstaller_removes_only_a_gguf_owned_by_the_offline_kit() -> None:
    builder = _load_builder()
    script = builder.uninstall_script_text()

    assert "dpkg --remove rhetoric" in script
    assert ".rhetoric-offline-kit-owns-gguf" in script
    assert "rm -f /opt/rhetoric/models/Chatterbox-GGUF/chatterbox-q8_0.gguf" in script
    assert ".cache/huggingface" not in script


def test_audio_cpp_install_and_uninstall_are_scoped_to_kit_owned_paths() -> None:
    builder = _load_builder()
    install = builder.install_script_text()
    uninstall = builder.uninstall_script_text()

    assert 'audio.cpp/bin/audiocpp_cli' in install
    assert "app_root=/opt/rhetoric/usr/lib/rhetoric" in install
    assert 'audiocpp_path=$app_root/audio.cpp/bin/audiocpp_cli' in install
    assert ".rhetoric-offline-kit-owns-audiocpp" in install
    assert 'dpkg -i "$ROOT"/runtime-debs/*.deb' in install
    assert "mesa-vulkan-drivers" not in uninstall
    assert "dpkg --remove rhetoric" in uninstall
    assert ".rhetoric-offline-kit-owns-audiocpp" in uninstall


def test_kit_builder_stages_pinned_audio_cpp_binary_and_radv_package(tmp_path: Path) -> None:
    builder = _load_builder()
    cache = tmp_path / "source-hub"
    repo = cache / "models--ResembleAI--chatterbox"
    snapshot = repo / "snapshots" / builder.CHATTERBOX_REVISION
    snapshot.mkdir(parents=True)
    (repo / "refs").mkdir()
    (repo / "refs" / "main").write_text(builder.CHATTERBOX_REVISION)
    for name in builder.CHATTERBOX_FILES:
        (snapshot / name).write_bytes(name.encode())
    gguf = tmp_path / "chatterbox-q8_0.gguf"
    gguf.write_bytes(b"gguf")
    _write_model_provenance(gguf)
    cli = tmp_path / "audiocpp_cli"
    cli.write_bytes(b"executable")
    cli.chmod(0o755)
    _write_binary_provenance(builder, cli)
    mesa = tmp_path / "mesa-vulkan-drivers_25.2.8-0ubuntu0.24.04.4_amd64.deb"
    mesa.write_bytes(b"debian package")
    kit = tmp_path / "kit"
    (kit / "runtime-debs").mkdir(parents=True)
    (kit / "rhetoric_1.5.0_amd64.deb").write_bytes(b"deb")
    (tmp_path / "rhetoric-1.5.0-x86_64.AppImage").write_bytes(b"appimage")
    (tmp_path / "rhetoric_1.5.0_amd64.deb").write_bytes(b"release deb")
    archive = tmp_path / "offline.tar.gz"

    builder.build_kit(kit, cache, gguf, archive, audiocpp_binary=cli, mesa_vulkan_deb=mesa)

    staged_cli = kit / "audio.cpp" / "bin" / "audiocpp_cli"
    assert staged_cli.read_bytes() == b"executable"
    assert staged_cli.stat().st_mode & 0o111
    assert (kit / "runtime-debs" / mesa.name).read_bytes() == b"debian package"
    assert "audio.cpp/bin/audiocpp_cli" in (kit / "SHA256SUMS").read_text()


def test_kit_checksums_cover_the_hub_revision_ref(tmp_path: Path) -> None:
    builder = _load_builder()
    cache = tmp_path / "source-hub"
    repo = cache / "models--ResembleAI--chatterbox"
    snapshot = repo / "snapshots" / builder.CHATTERBOX_REVISION
    snapshot.mkdir(parents=True)
    (repo / "refs").mkdir()
    (repo / "refs" / "main").write_text(builder.CHATTERBOX_REVISION)
    for name in builder.CHATTERBOX_FILES:
        (snapshot / name).write_bytes(name.encode())
    gguf = tmp_path / "chatterbox-q8_0.gguf"
    gguf.write_bytes(b"gguf")
    _write_model_provenance(gguf)
    kit = tmp_path / "kit"
    (kit / "runtime-debs").mkdir(parents=True)
    (kit / "rhetoric_1.5.0_amd64.deb").write_bytes(b"deb")
    (kit / "runtime-debs" / "libx.deb").write_bytes(b"runtime")
    (kit / "uninstall.sh").write_text("#!/bin/sh\n")
    (tmp_path / "rhetoric-1.5.0-x86_64.AppImage").write_bytes(b"appimage")
    (tmp_path / "rhetoric_1.5.0_amd64.deb").write_bytes(b"release deb")
    cli = tmp_path / "audiocpp_cli"
    cli.write_bytes(b"cli")
    cli.chmod(0o755)
    _write_binary_provenance(builder, cli)
    mesa = tmp_path / "mesa-vulkan-drivers_25.2.8-0ubuntu0.24.04.4_amd64.deb"
    mesa.write_bytes(b"mesa deb")
    (tmp_path / "sbom.json").write_text("{}\n")
    archive = tmp_path / "offline.tar.gz"

    builder.build_kit(kit, cache, gguf, archive, audiocpp_binary=cli, mesa_vulkan_deb=mesa)

    checksums = (kit / "SHA256SUMS").read_text()
    assert "models/hf_cache/models--ResembleAI--chatterbox/refs/main" in checksums
    assert archive.is_file()
    assert (kit / "audio.cpp" / "bin" / "audiocpp_cli").is_file()
    assert (kit / "runtime-debs" / mesa.name).is_file()
    assert (kit / "rhetoric_1.5.0_amd64.deb").read_bytes() == b"release deb"
    release = __import__("json").loads((tmp_path / "update-manifest.json").read_text())
    assert {item["name"] for item in release["artifacts"]} == {
        "rhetoric-1.5.0-x86_64.AppImage",
        "rhetoric_1.5.0_amd64.deb",
        "offline.tar.gz",
    }


def test_model_stage_rejects_missing_immutable_source_provenance(tmp_path: Path) -> None:
    builder = _load_builder()
    source = tmp_path / "source-hub"
    snapshot = source / "models--ResembleAI--chatterbox" / "snapshots" / builder.CHATTERBOX_REVISION
    snapshot.mkdir(parents=True)
    (source / "models--ResembleAI--chatterbox" / "refs").mkdir()
    (source / "models--ResembleAI--chatterbox" / "refs" / "main").write_text(builder.CHATTERBOX_REVISION)
    for name in builder.CHATTERBOX_FILES:
        (snapshot / name).write_bytes(name.encode())
    gguf = tmp_path / "chatterbox-q8_0.gguf"
    gguf.write_bytes(b"gguf")

    with pytest.raises(builder.BuildError, match="provenance"):
        builder.stage_models(source, gguf, tmp_path / "out")


def test_audio_cpp_stage_rejects_missing_build_provenance(tmp_path: Path) -> None:
    builder = _load_builder()
    binary = tmp_path / "audiocpp_cli"
    binary.write_bytes(b"binary")
    binary.chmod(0o755)

    with pytest.raises(builder.BuildError, match="provenance"):
        builder.stage_audio_cpp(binary, tmp_path / "kit")


def test_model_stage_rejects_provenance_for_different_model_bytes(tmp_path: Path) -> None:
    builder = _load_builder()
    source = tmp_path / "source-hub"
    snapshot = source / "models--ResembleAI--chatterbox" / "snapshots" / builder.CHATTERBOX_REVISION
    snapshot.mkdir(parents=True)
    refs = source / "models--ResembleAI--chatterbox" / "refs"
    refs.mkdir()
    (refs / "main").write_text(builder.CHATTERBOX_REVISION)
    for name in builder.CHATTERBOX_FILES:
        (snapshot / name).write_bytes(name.encode())
    gguf = tmp_path / "chatterbox-q8_0.gguf"
    gguf.write_bytes(b"original bytes")
    _write_model_provenance(gguf)
    gguf.write_bytes(b"changed bytes")

    with pytest.raises(builder.BuildError, match="provenance does not match"):
        builder.stage_models(source, gguf, tmp_path / "out")


def test_audio_cpp_stage_rejects_provenance_for_different_binary_bytes(tmp_path: Path) -> None:
    builder = _load_builder()
    binary = tmp_path / "audiocpp_cli"
    binary.write_bytes(b"original binary")
    binary.chmod(0o755)
    _write_binary_provenance(builder, binary)
    binary.write_bytes(b"changed binary")

    with pytest.raises(builder.BuildError, match="provenance does not match"):
        builder.stage_audio_cpp(binary, tmp_path / "kit")
