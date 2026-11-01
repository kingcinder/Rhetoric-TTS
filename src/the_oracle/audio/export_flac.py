"""FLAC export with SoundFile primary writing and ffmpeg fallback tagging."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from the_oracle import licensing as _licensing
from the_oracle.audio.flac_tags import write_vorbis_comments

LOGGER = logging.getLogger(__name__)

#: Vorbis-comment field carrying the licensee's opaque serial id into exported
#: audio. It is forensic attribution for leaked renders, not a lock: it never
#: changes what the customer can do, and it holds the licence UUID (never the
#: licensee's name or email).
FORENSIC_LICENSE_FIELD = "RHETORIC_LICENSE"


def next_available_output_path(path: str | Path) -> Path:
    destination = Path(path)
    if not destination.exists():
        return destination
    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    index = 1
    while True:
        candidate = parent / f"{stem} ({index}){suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _tag_flac(path: Path, metadata: dict[str, str]) -> None:
    """Write Vorbis comments through the stdlib tagger in ``flac_tags``.

    The import lives at module level, not inside this function: the
    suite-wide worker sweep (``tests/test_worker_import_sweep.py``) requires
    worker-reachable modules to carry no function-level imports, and a
    first-import on a QThread races the GUI main thread through shiboken's
    signature hook (U4.2).
    """
    write_vorbis_comments(path, metadata)


def _ffmpeg_write(path: Path, audio: np.ndarray, sample_rate: int, metadata: dict[str, str]) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FLAC export failed and ffmpeg is not available.")

    temp_wav = path.with_suffix(".tmp.wav")
    sf.write(str(temp_wav), audio, sample_rate, format="WAV")
    command = [ffmpeg, "-y", "-i", str(temp_wav)]
    for key, value in metadata.items():
        if value:
            command.extend(["-metadata", f"{key}={value}"])
    command.extend(["-c:a", "flac", str(path)])
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    finally:
        temp_wav.unlink(missing_ok=True)


def _require_serial() -> _licensing.LicenseStatus:
    """Refuse to write an audio file from an unlicensed install.

    Deliberately independent of ``the_oracle.licensing.policy.require``: every
    rendered or exported file passes through here, so patching the pipeline's
    entry gate does not make this module produce output. Returns the verified
    status so the writer can stamp the licensee's id into the file.
    """
    status = _licensing.current_license()
    if status.ok and status.state == "valid":
        return status
    detail = f"{status.detail} " if status.detail else ""
    raise _licensing.LicenseRequired(
        f"Enter a serial number to export audio. {detail}"
        "Activation is offline and takes one paste."
    )


def write_flac(path: str | Path, audio: np.ndarray, sample_rate: int, metadata: dict[str, str]) -> Path:
    status = _require_serial()
    if status.lic_id:
        # Copy: the caller's metadata is shared state and must not gain a tag
        # the caller did not ask for.
        metadata = dict(metadata)
        metadata[FORENSIC_LICENSE_FIELD] = status.lic_id
    destination = next_available_output_path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        sf.write(str(destination), np.asarray(audio, dtype=np.float32), sample_rate, format="FLAC")
    except Exception:
        # The audio write itself failed: fall back to the ffmpeg pipeline,
        # which writes and tags in one pass.
        _ffmpeg_write(destination, audio, sample_rate, metadata)
        return destination
    # Tagging is best-effort metadata only: a tagging failure must warn, not
    # fail an export whose audio file was written successfully.
    try:
        _tag_flac(destination, metadata)
    except Exception as exc:
        LOGGER.warning("FLAC tagging failed for %s (%s); audio export kept.", destination, exc)
    return destination


def export_flac(input_wav: str | Path, output_flac: str | Path, metadata: dict[str, str]) -> Path:
    audio, sample_rate = sf.read(str(input_wav), always_2d=False)
    array = np.asarray(audio, dtype=np.float32)
    if array.ndim > 1:
        array = array.mean(axis=1)
    return write_flac(output_flac, array, sample_rate, metadata)
