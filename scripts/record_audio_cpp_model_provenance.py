#!/usr/bin/env python3
"""Record the immutable Hugging Face revision and digest for a GGUF model."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


class ProvenanceError(RuntimeError):
    """The model's upstream revision cannot be established safely."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_model_provenance(
    model: Path,
    package_info: dict[str, object],
    *,
    endpoint: str,
    open_url=urlopen,
) -> dict[str, object]:
    if not model.is_file():
        raise ProvenanceError(f"model file does not exist: {model}")
    try:
        download = package_info["download"]
        files = package_info["files"]
        if not isinstance(download, dict) or not isinstance(files, list):
            raise TypeError("package metadata has unexpected shape")
        repo = download["repo"]
        revision = download.get("revision", "main")
        remote_files = [name for name in files if isinstance(name, str) and Path(name).name == model.name]
        if not isinstance(repo, str) or not isinstance(revision, str) or len(remote_files) != 1:
            raise ValueError("package does not identify one repository file")
    except (KeyError, TypeError, ValueError) as exc:
        raise ProvenanceError(f"invalid model package metadata: {exc}") from exc

    digest = _sha256(model)
    destination = Path(f"{model}.rhetoric-provenance.json")
    if destination.is_file():
        try:
            existing = json.loads(destination.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = None
        if (
            isinstance(existing, dict)
            and existing.get("format") == 1
            and existing.get("repo") == repo
            and existing.get("file") == model.name
            and isinstance(existing.get("revision"), str)
            and re.fullmatch(r"[0-9a-f]{40}", existing["revision"])
            and existing.get("sha256") == digest
        ):
            return existing

    url = (
        f"{endpoint.rstrip('/')}/{quote(repo, safe='/')}/resolve/{quote(revision, safe='')}"
        f"/{quote(remote_files[0], safe='/')}"
    )
    try:
        with open_url(Request(url, method="HEAD"), timeout=60) as response:
            resolved_revision = response.headers.get("X-Repo-Commit", "")
        if not isinstance(resolved_revision, str) or not re.fullmatch(r"[0-9a-f]{40}", resolved_revision):
            api_url = (
                f"{endpoint.rstrip('/')}/api/models/{quote(repo, safe='/')}"
                f"?revision={quote(revision, safe='')}"
            )
            with open_url(Request(api_url, headers={"Accept": "application/json"}), timeout=60) as response:
                model_info = json.loads(response.read().decode("utf-8"))
            resolved_revision = model_info.get("sha", "") if isinstance(model_info, dict) else ""
    except Exception as exc:
        raise ProvenanceError(f"could not resolve immutable Hugging Face model revision: {exc}") from exc
    if not isinstance(resolved_revision, str) or not re.fullmatch(r"[0-9a-f]{40}", resolved_revision):
        raise ProvenanceError(f"Hugging Face did not provide an immutable model revision for {repo}")

    record: dict[str, object] = {
        "format": 1,
        "repo": repo,
        "revision": resolved_revision,
        "file": model.name,
        "sha256": digest,
    }
    temporary = Path(f"{destination}.tmp")
    temporary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-manager", type=Path, required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--model", type=Path, required=True)
    args = parser.parse_args(argv)
    info = json.loads(
        subprocess.run(
            [sys.executable, str(args.model_manager), "info", args.package, "--json"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    record = record_model_provenance(
        args.model,
        info,
        endpoint=os.environ.get("HF_ENDPOINT", "https://huggingface.co"),
    )
    print(f"Recorded {record['repo']}@{record['revision']} for {args.model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
