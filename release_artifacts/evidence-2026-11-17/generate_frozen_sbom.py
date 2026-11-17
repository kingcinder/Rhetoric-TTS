from __future__ import annotations

from datetime import datetime, timezone
from email.parser import BytesParser
from email.policy import compat32
from pathlib import Path
from urllib.parse import quote
import hashlib
import json
import re
import subprocess
import uuid

REPO = Path(__file__).resolve().parents[2]
RC = REPO / "release_artifacts/linux-rc-b9ee597"
KIT = RC / "kit"
FROZEN = RC / "AppDir/usr/lib/rhetoric/_internal"
SOURCE = "b9ee5979757d3d731c4189c3b53a2069405bb8a"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_component(path: Path, label: str, *, version: str | None = None) -> dict[str, object]:
    relative = path.relative_to(REPO).as_posix()
    item: dict[str, object] = {
        "type": "file",
        "bom-ref": f"file:{relative}",
        "name": path.name,
        "hashes": [{"alg": "SHA-256", "content": sha256(path)}],
        "properties": [
            {"name": "evidence:path", "value": relative},
            {"name": "evidence:role", "value": label},
            {"name": "evidence:size-bytes", "value": str(path.stat().st_size)},
        ],
    }
    if version:
        item["version"] = version
    return item


components: list[dict[str, object]] = []
python_refs: dict[str, str] = {}
for metadata_path in sorted(FROZEN.glob("*.dist-info/METADATA")):
    meta = BytesParser(policy=compat32).parsebytes(metadata_path.read_bytes())
    name = meta.get("Name")
    version = meta.get("Version")
    if not name or not version:
        continue
    normalized = re.sub(r"[-_.]+", "-", name).lower()
    purl = f"pkg:pypi/{quote(normalized, safe='-._')}@{quote(version, safe='.+-_')}"
    ref = purl
    python_refs[normalized] = ref
    licenses: list[dict[str, object]] = []
    expression = meta.get("License-Expression")
    license_name = expression or meta.get("License")
    if license_name and license_name.strip().lower() not in {"unknown", "none"}:
        # Keep upstream metadata verbatim; license review uses the separately shipped notices.
        licenses = [{"license": {"name": license_name.strip()}}]
    properties = [{"name": "evidence:metadata-path", "value": metadata_path.relative_to(REPO).as_posix()}]
    component: dict[str, object] = {
        "type": "library",
        "bom-ref": ref,
        "name": name,
        "version": version,
        "purl": purl,
        "properties": properties,
    }
    if licenses:
        component["licenses"] = licenses
    components.append(component)

native_refs: list[str] = []
for path in sorted(FROZEN.rglob("*")):
    if not path.is_file() or path.is_symlink() or ".so" not in path.name:
        continue
    component = file_component(path, "frozen native shared object")
    native_refs.append(str(component["bom-ref"]))
    components.append(component)

for path in sorted((KIT / "runtime-debs").glob("*.deb")):
    fields = subprocess.run(
        ["dpkg-deb", "-f", str(path), "Package", "Version", "Architecture"],
        check=True, text=True, capture_output=True,
    ).stdout.splitlines()
    package, version, arch = (fields + ["", "", ""])[:3]
    purl = f"pkg:deb/ubuntu/{quote(package, safe='-+._')}@{quote(version, safe=':+~.-')}?arch={quote(arch, safe='-._')}"
    components.append({
        "type": "library",
        "bom-ref": purl,
        "name": package,
        "version": version,
        "purl": purl,
        "hashes": [{"alg": "SHA-256", "content": sha256(path)}],
        "properties": [
            {"name": "evidence:path", "value": path.relative_to(REPO).as_posix()},
            {"name": "evidence:role", "value": "bundled Ubuntu runtime package"},
            {"name": "evidence:architecture", "value": arch},
        ],
    })

models = KIT / "models"
model_manifest = json.loads((models / "manifest.json").read_text())
for record in model_manifest["cpu_model"]["files"]:
    path = models / "hf_cache/models--ResembleAI--chatterbox/snapshots" / model_manifest["cpu_model"]["revision"] / record["file"]
    components.append({
        "type": "machine-learning-model",
        "bom-ref": f"pkg:generic/ResembleAI-chatterbox@{model_manifest['cpu_model']['revision']}#{record['file']}",
        "name": f"ResembleAI/chatterbox/{record['file']}",
        "version": model_manifest["cpu_model"]["revision"],
        "hashes": [{"alg": "SHA-256", "content": record["sha256"]}],
        "properties": [
            {"name": "evidence:path", "value": path.relative_to(REPO).as_posix()},
            {"name": "evidence:size-bytes", "value": str(record["size"])},
            {"name": "evidence:source-revision", "value": model_manifest["cpu_model"]["revision"]},
        ],
    })
vm = model_manifest["vulkan_model"]
path = models / "Chatterbox-GGUF" / vm["file"]
components.append({
    "type": "machine-learning-model",
    "bom-ref": f"pkg:generic/audio-cpp-audio.cpp-gguf@{vm['revision']}#{vm['file']}",
    "name": vm["file"],
    "version": vm["revision"],
    "hashes": [{"alg": "SHA-256", "content": vm["sha256"]}],
    "properties": [
        {"name": "evidence:path", "value": path.relative_to(REPO).as_posix()},
        {"name": "evidence:size-bytes", "value": str(vm["size"])},
        {"name": "evidence:source-revision", "value": vm["revision"]},
    ],
})

ac = KIT / "audio.cpp/bin/audiocpp_cli"
ac_manifest = json.loads((KIT / "manifest.json").read_text())["audio_cpp"]
components.append({
    "type": "file",
    "bom-ref": f"file:{ac.relative_to(REPO).as_posix()}",
    "name": "audiocpp_cli",
    "version": ac_manifest["source_commit"],
    "hashes": [{"alg": "SHA-256", "content": ac_manifest["sha256"]}],
    "properties": [
        {"name": "evidence:path", "value": ac.relative_to(REPO).as_posix()},
        {"name": "evidence:role", "value": "patched audio.cpp Vulkan inference binary"},
        {"name": "evidence:size-bytes", "value": str(ac_manifest["size"])},
    ],
})

app = RC / "rhetoric_1.5.0_amd64.deb"
app_hash = sha256(app)
root_ref = "pkg:generic/rhetoric@1.5.0"
all_runtime_refs = sorted([*python_refs.values(), *native_refs])
all_runtime_refs.extend(c["bom-ref"] for c in components if c.get("type") == "machine-learning-model")
all_runtime_refs.extend(c["bom-ref"] for c in components if any(p.get("value") == "bundled Ubuntu runtime package" for p in c.get("properties", [])))
bom = {
    "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
    "bomFormat": "CycloneDX",
    "specVersion": "1.5",
    "serialNumber": f"urn:uuid:{uuid.uuid4()}",
    "version": 1,
    "metadata": {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tools": {"components": [{"type": "application", "name": "Rhetoric frozen runtime inventory generator", "version": "1"}]},
        "component": {
            "type": "application",
            "bom-ref": root_ref,
            "name": "Rhetoric",
            "version": "1.5.0",
            "purl": root_ref,
            "hashes": [{"alg": "SHA-256", "content": app_hash}],
            "properties": [
                {"name": "evidence:public-release-label", "value": "V1.00a"},
                {"name": "evidence:source-commit", "value": SOURCE},
                {"name": "evidence:target", "value": "Ubuntu 24.04 amd64"},
                {"name": "evidence:package", "value": app.relative_to(REPO).as_posix()},
                {"name": "evidence:vulnerability-audit", "value": "not performed: advisory service unavailable"},
            ],
        },
    },
    "components": components,
    "dependencies": [{"ref": root_ref, "dependsOn": all_runtime_refs}],
}
output = RC / "sbom.json"
output.write_text(json.dumps(bom, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(f"sbom={output}")
print(f"python_packages={len(python_refs)} native_shared_objects={len(native_refs)} runtime_debs={len(list((KIT/'runtime-debs').glob('*.deb')))} model_components=6")
print(f"components={len(components)} app_sha256={app_hash} bytes={output.stat().st_size}")
