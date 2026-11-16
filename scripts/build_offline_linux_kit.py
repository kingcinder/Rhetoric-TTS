#!/usr/bin/env python3
"""Add the pinned CPU and Vulkan Chatterbox models to the Ubuntu offline kit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

CHATTERBOX_REPO = "ResembleAI/chatterbox"
CHATTERBOX_REVISION = "5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18"
AUDIOCPP_COMMIT = "748c5e28f6a7228b8f38ad7142ca97d29584544b"
CHATTERBOX_FILES = (
    "conds.pt",
    "s3gen.safetensors",
    "t3_cfg.safetensors",
    "tokenizer.json",
    "ve.safetensors",
)
REPO_ROOT = Path(__file__).resolve().parents[1]


class BuildError(RuntimeError):
    """The offline kit's model inputs are missing or inconsistent."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_provenance(path: Path, subject: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"missing or invalid {subject} provenance: {path}") from exc
    if not isinstance(value, dict) or value.get("format") != 1:
        raise BuildError(f"unsupported {subject} provenance format: {path}")
    return value


def _link_or_copy(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def stage_models(model_cache: Path, vulkan_model: Path, destination: Path) -> dict[str, object]:
    """Stage only the pinned Chatterbox standard checkpoint and Vulkan GGUF."""
    repo = model_cache / "models--ResembleAI--chatterbox"
    snapshot = repo / "snapshots" / CHATTERBOX_REVISION
    ref = repo / "refs" / "main"
    if not snapshot.is_dir() or not ref.is_file() or ref.read_text(encoding="ascii").strip() != CHATTERBOX_REVISION:
        raise BuildError(f"model cache is not pinned to {CHATTERBOX_REVISION}: {repo}")
    missing = [name for name in CHATTERBOX_FILES if not (snapshot / name).is_file()]
    if missing:
        raise BuildError(f"missing required Chatterbox files: {', '.join(missing)}")
    if not vulkan_model.is_file() or vulkan_model.name != "chatterbox-q8_0.gguf":
        raise BuildError(f"expected the audio.cpp chatterbox-q8_0.gguf model: {vulkan_model}")
    model_provenance = _read_provenance(
        Path(f"{vulkan_model}.rhetoric-provenance.json"), "Vulkan model"
    )
    revision = model_provenance.get("revision")
    if (
        model_provenance.get("repo") != "audio-cpp/audio.cpp-gguf"
        or model_provenance.get("file") != vulkan_model.name
        or not isinstance(revision, str)
        or not re.fullmatch(r"[0-9a-f]{40}", revision)
        or model_provenance.get("sha256") != _sha256(vulkan_model)
    ):
        raise BuildError(f"Vulkan model provenance does not match the model bytes: {vulkan_model}")

    if destination.exists():
        shutil.rmtree(destination)
    staged_snapshot = destination / "hf_cache" / "models--ResembleAI--chatterbox" / "snapshots" / CHATTERBOX_REVISION
    (staged_snapshot.parent.parent / "refs").mkdir(parents=True, exist_ok=True)
    staged_snapshot.mkdir(parents=True)
    for name in CHATTERBOX_FILES:
        _link_or_copy(snapshot / name, staged_snapshot / name)
    (staged_snapshot.parent.parent / "refs" / "main").write_text(CHATTERBOX_REVISION, encoding="ascii")

    staged_vulkan = destination / "Chatterbox-GGUF" / vulkan_model.name
    staged_vulkan.parent.mkdir(parents=True)
    _link_or_copy(vulkan_model, staged_vulkan)

    license_template = (REPO_ROOT / "THIRD_PARTY_LICENSES" / "MIT.txt").read_text(encoding="utf-8")
    placeholder = "Copyright (c) <year> <copyright holders>"
    if placeholder not in license_template:
        raise BuildError("MIT license template no longer has its expected copyright placeholder")
    licenses = destination / "THIRD_PARTY_LICENSES"
    licenses.mkdir(exist_ok=True)
    (licenses / "ResembleAI-Chatterbox-MIT.txt").write_text(
        license_template.replace(placeholder, "Copyright (c) 2025 Resemble AI", 1),
        encoding="utf-8",
    )
    (destination / "MODEL_NOTICES.md").write_text(
        "# Model notices\n\n"
        f"The CPU checkpoint is `{CHATTERBOX_REPO}` at revision `{CHATTERBOX_REVISION}`.\n\n"
        "The Vulkan Q8_0 GGUF was obtained through the audio.cpp `chatterbox_q8_0` package "
        f"(`audio-cpp/audio.cpp-gguf`, immutable revision `{revision}`).\n\n"
        "Copyright (c) 2025 Resemble AI. The Chatterbox model is identified as MIT licensed in "
        "Rhetoric's third-party inventory. The corresponding MIT text with this copyright notice "
        "is included at `THIRD_PARTY_LICENSES/ResembleAI-Chatterbox-MIT.txt`.\n",
        encoding="utf-8",
    )

    manifest: dict[str, object] = {
        "format": 1,
        "cpu_model": {
            "repo": CHATTERBOX_REPO,
            "revision": CHATTERBOX_REVISION,
            "files": [
                {"file": name, "size": (staged_snapshot / name).stat().st_size, "sha256": _sha256(staged_snapshot / name)}
                for name in CHATTERBOX_FILES
            ],
        },
        "vulkan_model": {
            "repo": "audio-cpp/audio.cpp-gguf",
            "revision": revision,
            "file": staged_vulkan.name,
            "size": staged_vulkan.stat().st_size,
            "sha256": _sha256(staged_vulkan),
        },
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    all_model_files = sorted(path for path in destination.rglob("*") if path.is_file())
    (destination / "SHA256SUMS").write_text(
        "".join(f"{_sha256(path)}  {path.relative_to(destination)}\n" for path in all_model_files),
        encoding="utf-8",
    )
    return manifest


def stage_audio_cpp(binary: Path, destination: Path) -> dict[str, object]:
    """Stage the pinned audio.cpp CLI and its upstream license texts."""
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise BuildError(f"audiocpp_cli must exist and be executable: {binary}")
    try:
        source_commit = subprocess.run(
            ["git", "-C", str(REPO_ROOT / "audio.cpp"), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildError("could not verify the audio.cpp source checkout for the offline kit") from exc
    if source_commit != AUDIOCPP_COMMIT:
        raise BuildError(f"audio.cpp checkout is not pinned to {AUDIOCPP_COMMIT}: {source_commit}")
    binary_provenance = _read_provenance(
        Path(f"{binary}.rhetoric-provenance.json"), "audio.cpp build"
    )
    if (
        binary_provenance.get("source_commit") != source_commit
        or binary_provenance.get("binary_sha256") != _sha256(binary)
    ):
        raise BuildError(f"audio.cpp binary provenance does not match pinned source or binary: {binary}")
    staged = destination / "audio.cpp" / "bin" / "audiocpp_cli"
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(binary, staged)
    licenses = destination / "audio.cpp" / "THIRD_PARTY_LICENSES"
    licenses.mkdir(exist_ok=True)
    for source, name in (
        (REPO_ROOT / "audio.cpp" / "LICENSE", "audio.cpp-Apache-2.0.txt"),
        (REPO_ROOT / "audio.cpp" / "external" / "ggml" / "LICENSE", "ggml-MIT.txt"),
        (REPO_ROOT / "audio.cpp" / "external" / "sentencepiece" / "LICENSE", "sentencepiece-Apache-2.0.txt"),
    ):
        if not source.is_file():
            raise BuildError(f"missing audio.cpp third-party license: {source}")
        shutil.copy2(source, licenses / name)
    return {
        "source_commit": AUDIOCPP_COMMIT,
        "binary": str(staged.relative_to(destination)),
        "sha256": _sha256(staged),
        "size": staged.stat().st_size,
        "licenses": sorted(path.name for path in licenses.iterdir()),
    }


def install_script_text() -> str:
    """Return the model-aware Ubuntu 24.04 install script."""
    return """#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
[ "$(dpkg --print-architecture)" = amd64 ] || { echo "Rhetoric offline kit requires amd64." >&2; exit 2; }
[ "$(id -u)" -eq 0 ] || { echo "Run with sudo to install system packages." >&2; exit 2; }
(cd "$ROOT" && sha256sum -c SHA256SUMS)
model_path=/opt/rhetoric/models/Chatterbox-GGUF/chatterbox-q8_0.gguf
model_marker=/opt/rhetoric/.rhetoric-offline-kit-owns-gguf
app_root=/opt/rhetoric/usr/lib/rhetoric
audiocpp_path=$app_root/audio.cpp/bin/audiocpp_cli
audiocpp_marker=/opt/rhetoric/.rhetoric-offline-kit-owns-audiocpp
if [ -e "$model_path" ]; then
  cmp -s "$ROOT/models/Chatterbox-GGUF/chatterbox-q8_0.gguf" "$model_path" || { echo "Existing Vulkan model differs; refusing to overwrite: $model_path" >&2; exit 2; }
fi
dpkg -i "$ROOT"/runtime-debs/*.deb
dpkg --configure --pending
dpkg -i "$ROOT"/rhetoric_1.5.0_amd64.deb
if [ -e "$audiocpp_path" ]; then
  cmp -s "$ROOT/audio.cpp/bin/audiocpp_cli" "$audiocpp_path" || { echo "Existing audio.cpp binary differs; refusing to overwrite: $audiocpp_path" >&2; exit 2; }
else
  install -d -m 0755 "$app_root/audio.cpp/bin"
  install -m 0755 "$ROOT/audio.cpp/bin/audiocpp_cli" "$audiocpp_path"
  : > "$audiocpp_marker"
fi
install -d -m 0755 /opt/rhetoric/models/Chatterbox-GGUF
if [ -e "$model_path" ]; then
  cmp -s "$ROOT/models/Chatterbox-GGUF/chatterbox-q8_0.gguf" "$model_path" || { echo "Existing Vulkan model differs; refusing to overwrite: $model_path" >&2; exit 2; }
else
  install -m 0644 "$ROOT/models/Chatterbox-GGUF/chatterbox-q8_0.gguf" "$model_path"
  : > "$model_marker"
fi
target_user=${SUDO_USER:-root}
passwd_entry=$(getent passwd "$target_user") || { echo "Cannot resolve install user: $target_user" >&2; exit 2; }
old_ifs=$IFS
IFS=:
set -- $passwd_entry
IFS=$old_ifs
target_uid=$3
target_gid=$4
target_home=$6
hf_cache=$target_home/.cache/huggingface/hub
hf_repo=$hf_cache/models--ResembleAI--chatterbox
install -d -o "$target_uid" -g "$target_gid" -m 0755 "$hf_cache" "$hf_repo"
cp -a "$ROOT/models/hf_cache/models--ResembleAI--chatterbox/." "$hf_repo/"
chown -R "$target_uid:$target_gid" "$hf_repo"
echo "Installed pinned CPU Chatterbox cache for $target_user."
echo "Installed Vulkan GGUF at /opt/rhetoric/models/Chatterbox-GGUF/chatterbox-q8_0.gguf."
echo "Installed audio.cpp CLI at $audiocpp_path."
"""


def uninstall_script_text() -> str:
    """Remove the app and only the system GGUF this kit added."""
    return """#!/bin/sh
set -eu
[ "$(id -u)" -eq 0 ] || { echo "Run with sudo to remove Rhetoric." >&2; exit 2; }
model_marker=/opt/rhetoric/.rhetoric-offline-kit-owns-gguf
audiocpp_marker=/opt/rhetoric/.rhetoric-offline-kit-owns-audiocpp
app_root=/opt/rhetoric/usr/lib/rhetoric
if [ -f "$audiocpp_marker" ]; then
  rm -f "$app_root/audio.cpp/bin/audiocpp_cli" "$audiocpp_marker"
  rmdir "$app_root/audio.cpp/bin" "$app_root/audio.cpp" 2>/dev/null || true
fi
if [ -f "$model_marker" ]; then
  rm -f /opt/rhetoric/models/Chatterbox-GGUF/chatterbox-q8_0.gguf "$model_marker"
  rmdir /opt/rhetoric/models/Chatterbox-GGUF /opt/rhetoric/models 2>/dev/null || true
fi
dpkg --remove rhetoric
"""


def _write_readme(kit_dir: Path, manifest: dict[str, object]) -> None:
    cpu_files = manifest["cpu_model"]["files"]  # type: ignore[index]
    cpu_size = sum(item["size"] for item in cpu_files)  # type: ignore[index]
    vulkan = manifest["vulkan_model"]  # type: ignore[assignment]
    (kit_dir / "README.md").write_text(
        "# Rhetoric 1.5.0 Ubuntu 24.04 amd64 offline kit\n\n"
        "This kit installs the frozen CPU application, its declared Ubuntu runtime packages, "
        "the pinned Chatterbox CPU and Vulkan models, the audio.cpp CLI, and Ubuntu 24.04's Mesa RADV Vulkan ICD.\n\n"
        "Run `sudo ./install.sh` after extraction. The installer seeds the invoking user (or root) "
        "Hugging Face cache and installs the GGUF under `/opt/rhetoric/models`. Remove the app with "
        "`sudo ./uninstall.sh`; the per-user CPU model cache is retained.\n\n"
        f"CPU model: `{CHATTERBOX_REPO}` at `{CHATTERBOX_REVISION}`, {cpu_size:,} bytes across five files.\n\n"
        f"Vulkan model: `{vulkan['file']}`, {vulkan['size']:,} bytes, from the audio.cpp `chatterbox_q8_0` package.\n\n"
        "The kit includes `audiocpp_cli`, the Vulkan loader, and the Mesa RADV userspace driver. "
        "The AMDGPU kernel module, firmware, kernel, and `/dev/dri` device access remain host requirements. "
        "Uninstall removes kit-owned app/model files; shared Ubuntu runtime packages and the user's CPU cache remain.\n",
        encoding="utf-8",
    )


def build_kit(
    kit_dir: Path,
    model_cache: Path,
    vulkan_model: Path,
    archive: Path,
    *,
    audiocpp_binary: Path,
    mesa_vulkan_deb: Path,
) -> dict[str, object]:
    if not (kit_dir / "rhetoric_1.5.0_amd64.deb").is_file() or not (kit_dir / "runtime-debs").is_dir():
        raise BuildError(f"not a staged Ubuntu offline kit: {kit_dir}")
    release_deb = archive.parent / "rhetoric_1.5.0_amd64.deb"
    if release_deb.is_file():
        shutil.copy2(release_deb, kit_dir / release_deb.name)
    manifest = stage_models(model_cache, vulkan_model, kit_dir / "models")
    audio_manifest = stage_audio_cpp(audiocpp_binary, kit_dir)
    if not mesa_vulkan_deb.is_file() or not mesa_vulkan_deb.name.startswith("mesa-vulkan-drivers_"):
        raise BuildError(f"expected the Ubuntu mesa-vulkan-drivers amd64 package: {mesa_vulkan_deb}")
    staged_mesa = kit_dir / "runtime-debs" / mesa_vulkan_deb.name
    shutil.copy2(mesa_vulkan_deb, staged_mesa)
    offline_manifest = {
        "format": 1,
        "target": "Ubuntu 24.04 amd64",
        "models": manifest,
        "audio_cpp": audio_manifest,
        "vulkan_runtime": {
            "package": staged_mesa.name,
            "size": staged_mesa.stat().st_size,
            "sha256": _sha256(staged_mesa),
        },
    }
    (kit_dir / "manifest.json").write_text(json.dumps(offline_manifest, indent=2) + "\n", encoding="utf-8")
    _write_readme(kit_dir, manifest)
    installer = kit_dir / "install.sh"
    installer.write_text(install_script_text(), encoding="utf-8", newline="\n")
    installer.chmod(0o755)
    uninstaller = kit_dir / "uninstall.sh"
    uninstaller.write_text(uninstall_script_text(), encoding="utf-8", newline="\n")
    uninstaller.chmod(0o755)
    base_files = [
        kit_dir / "rhetoric_1.5.0_amd64.deb",
        *sorted((kit_dir / "runtime-debs").glob("*.deb")),
        kit_dir / "install.sh",
        kit_dir / "uninstall.sh",
        kit_dir / "README.md",
        kit_dir / "manifest.json",
        kit_dir / "models" / "SHA256SUMS",
        *sorted(path for path in (kit_dir / "models").rglob("*") if path.is_file()),
        *sorted(path for path in (kit_dir / "audio.cpp").rglob("*") if path.is_file()),
    ]
    (kit_dir / "SHA256SUMS").write_text(
        "".join(f"{_sha256(path)}  {path.relative_to(kit_dir)}\n" for path in sorted(set(base_files))),
        encoding="utf-8",
    )
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        archive.unlink()
    with tarfile.open(archive, "w:gz", compresslevel=1) as tar:
        tar.add(kit_dir, arcname=kit_dir.name, recursive=True)
    _write_release_manifests(archive.parent, archive)
    return manifest


def _write_release_manifests(artifact_dir: Path, offline_archive: Path) -> None:
    artifacts = [
        artifact_dir / "rhetoric-1.5.0-x86_64.AppImage",
        artifact_dir / "rhetoric_1.5.0_amd64.deb",
        offline_archive,
    ]
    missing = [path.name for path in artifacts if not path.is_file()]
    if missing:
        raise BuildError(f"release artifacts missing beside offline kit: {', '.join(missing)}")
    sbom = artifact_dir / "sbom.json"
    checksum_files = [*artifacts, *([sbom] if sbom.is_file() else [])]
    checksum_path = artifact_dir / "checksums-1.5.0.sha256"
    checksum_path.write_text(
        "".join(f"{_sha256(path)}  {path.name}\n" for path in sorted(checksum_files, key=lambda p: p.name)),
        encoding="utf-8",
    )
    payload = {
        "format": 1,
        "version": "1.5.0",
        "artifacts": [
            {"name": path.name, "sha256": _sha256(path), "size": path.stat().st_size}
            for path in sorted(artifacts, key=lambda p: p.name)
        ],
        "rollback": "Install the previous verified artifact; no automatic replacement is performed.",
    }
    (artifact_dir / "update-manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-dir", type=Path, required=True, help="Existing staged Ubuntu offline kit directory.")
    parser.add_argument("--model-cache", type=Path, required=True, help="Hugging Face hub cache containing the pinned Chatterbox snapshot.")
    parser.add_argument(
        "--vulkan-model",
        type=Path,
        required=True,
        help="GGUF with adjacent .rhetoric-provenance.json (write with the model downloader or recorder).",
    )
    parser.add_argument(
        "--audiocpp-binary",
        type=Path,
        required=True,
        help="CLI built by scripts/build_audio_cpp.sh with its adjacent provenance record.",
    )
    parser.add_argument("--mesa-vulkan-deb", type=Path, required=True, help="Ubuntu 24.04 amd64 mesa-vulkan-drivers package.")
    parser.add_argument("--archive", type=Path, required=True, help="Output .tar.gz path.")
    args = parser.parse_args()
    manifest = build_kit(
        args.kit_dir,
        args.model_cache,
        args.vulkan_model,
        args.archive,
        audiocpp_binary=args.audiocpp_binary,
        mesa_vulkan_deb=args.mesa_vulkan_deb,
    )
    print(json.dumps({"archive": str(args.archive), "bytes": args.archive.stat().st_size, "models": manifest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
