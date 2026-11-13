"""Repo-local directory and filename helpers for Rhetoric GUI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shutil

from rhetoric.platform_support import app_data_dir


PORTABLE_MARKER = ".rhetoric-portable"

# Pre-rename portable marker; moved forward on first check.
LEGACY_PORTABLE_MARKER = "." + "oracle_portable".replace("_", "-")  # pre-rename marker, hyphenated spelling


@dataclass(frozen=True, slots=True)
class RhetoricPaths:
    repo_root: Path
    input_dir: Path
    output_dir: Path
    profile_dir: Path
    voice_dir: Path


def _portable_mode(root: Path) -> bool:
    value = os.environ.get("RHETORIC_PORTABLE", "").strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if (root / PORTABLE_MARKER).is_file():
        return True
    legacy_marker = root / LEGACY_PORTABLE_MARKER
    if legacy_marker.is_file():
        try:
            os.replace(legacy_marker, root / PORTABLE_MARKER)
        except OSError:
            pass
        return True
    return False


def _migrate_tree(source: Path, destination: Path) -> None:
    """Copy a legacy repo-local tree without deleting or overwriting files."""
    if not source.is_dir():
        return
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        target = destination / item.name
        if target.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def ensure_repo_default_paths(repo_root: str | Path) -> RhetoricPaths:
    root = Path(repo_root).expanduser().resolve()
    installed_root = Path(__file__).resolve().parents[2]
    data_root = root
    if root == installed_root and not _portable_mode(root):
        data_root = app_data_dir()
        for name in ("Input", "Output", "Profiles", "Seashells"):
            _migrate_tree(root / name, data_root / name)
    paths = RhetoricPaths(
        repo_root=root,
        input_dir=data_root / "Input",
        output_dir=data_root / "Output",
        profile_dir=data_root / "Profiles",
        voice_dir=data_root / "Seashells",
    )
    for path in (paths.input_dir, paths.output_dir, paths.profile_dir, paths.voice_dir):
        path.mkdir(parents=True, exist_ok=True)
    return paths


def render_work_dir() -> Path:
    """The app's working area for render material.

    Renders produce stems, caches, logs, previews, render plans and job files
    while they run. None of that is output: the user's chosen output folder
    must receive only the finished audio. Everything intermediate lives here,
    under the app's data home (``~/.local/share/rhetoric/render-work/`` on
    Linux), so it survives between renders and can be cleaned or swept
    independently of the output folder. ``RHETORIC_RENDER_WORK`` overrides the
    location for portable installs and tests.
    """
    override = os.environ.get("RHETORIC_RENDER_WORK", "").strip()
    path = Path(override).expanduser() if override else app_data_dir() / "render-work"
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_project_dir(input_path: str | Path) -> Path:
    """The per-render working directory for one input script.

    Named after the input file so revisiting the same script reuses its stem
    cache (fast re-renders) without the work appearing in the output folder.
    """
    stem = Path(str(input_path).strip()).stem or "render"
    safe = "".join(
        character if character.isalnum() or character in {"-", "_"} else "_"
        for character in stem
    ).strip("_") or "render"
    path = render_work_dir() / f"{safe}_rhetoric"
    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_output_filename(value: str) -> str:
    cleaned = Path(value.strip()).name
    if not cleaned:
        return ""
    suffix = Path(cleaned).suffix.lower()
    if suffix == ".flac":
        return cleaned
    stem = Path(cleaned).stem
    return f"{stem}.flac" if stem else ""


def default_output_filename(
    input_path: str | Path,
    output_dir: str | Path | None = None,
) -> str:
    """The auto-derived output name for a loaded script.

    The input file's stem plus the next free ``_No_N`` number -- the recorder's
    established ``Seashell_No_N`` counter. The number is chosen against the
    chosen output folder, so loading a script never proposes a name that would
    silently overwrite an earlier render (two renders of the same script land
    side by side instead). A name the user typed is never replaced by this
    helper; callers only apply it while the filename field is unedited.
    """
    candidate = Path(str(input_path).strip())
    stem = candidate.stem.strip()
    if not stem:
        return ""
    number = 1
    folder_text = str(output_dir).strip() if output_dir is not None else ""
    if folder_text:
        folder = Path(folder_text).expanduser()
        while (folder / f"{stem}_No_{number}.flac").exists():
            number += 1
    return f"{stem}_No_{number}.flac"


def resolve_output_filename(
    input_path: str | Path,
    output_dir: str | Path,
    default_output_dir: str | Path,
    requested_name: str,
) -> str:
    normalized = normalize_output_filename(requested_name)
    if normalized:
        return normalized
    if Path(output_dir).expanduser().resolve() == Path(default_output_dir).expanduser().resolve():
        return default_output_filename(input_path, output_dir)
    return ""
