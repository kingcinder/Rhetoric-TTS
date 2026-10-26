from pathlib import Path

import numpy as np
import soundfile as sf

from the_oracle.audio.export_flac import next_available_output_path, write_flac
from the_oracle.audio.flac_tags import read_vorbis_comments, write_vorbis_comments
from the_oracle.audio.flac_tags import _read_blocks, _read_u32


def test_next_available_output_path_uses_desktop_suffixes(tmp_path: Path) -> None:
    base = tmp_path / "name.flac"
    base.touch()
    (tmp_path / "name (1).flac").touch()

    candidate = next_available_output_path(base)

    assert candidate == tmp_path / "name (2).flac"


def test_write_flac_does_not_overwrite_existing_output(tmp_path: Path) -> None:
    audio = np.linspace(-0.1, 0.1, num=2400, dtype=np.float32)
    first = write_flac(tmp_path / "oracle.flac", audio, 24000, {"title": "First"})
    second = write_flac(tmp_path / "oracle.flac", audio, 24000, {"title": "Second"})

    assert first == tmp_path / "oracle.flac"
    assert second == tmp_path / "oracle (1).flac"
    assert first.exists()
    assert second.exists()


def test_write_flac_writes_standard_vorbis_comments(tmp_path: Path) -> None:
    audio = np.linspace(-0.1, 0.1, num=2400, dtype=np.float32)
    destination = write_flac(
        tmp_path / "tagged.flac",
        audio,
        24000,
        {"title": "Tagged", "artist": "Rhetoric", "comment": "Unicode ✓", "empty": ""},
    )

    tags = read_vorbis_comments(destination)
    assert tags["TITLE"] == ["Tagged"]
    assert tags["ARTIST"] == ["Rhetoric"]
    assert tags["COMMENT"] == ["Unicode ✓"]
    assert "EMPTY" not in tags
    # The tag rewrite must leave a valid FLAC stream, not just parseable tags.
    decoded, sample_rate = sf.read(str(destination))
    assert decoded.shape == audio.shape
    assert sample_rate == 24000


def test_retagging_preserves_unrelated_comments(tmp_path: Path) -> None:
    destination = tmp_path / "retag.flac"
    sf.write(str(destination), np.zeros(240, dtype=np.float32), 24000, format="FLAC")

    write_vorbis_comments(destination, {"title": "First", "artist": "Rhetoric"})
    write_vorbis_comments(destination, {"album": "Alpha"})

    tags = read_vorbis_comments(destination)
    assert tags["TITLE"] == ["First"]
    assert tags["ARTIST"] == ["Rhetoric"]
    assert tags["ALBUM"] == ["Alpha"]


def test_new_files_use_rhetoric_vendor_and_read_legacy_vendor_files(tmp_path: Path) -> None:
    destination = tmp_path / "vendor.flac"
    sf.write(str(destination), np.zeros(240, dtype=np.float32), 24000, format="FLAC")
    write_vorbis_comments(destination, {"title": "First"})
    blocks, _ = _read_blocks(destination.read_bytes())
    payload = next(value for block_type, value in blocks if block_type == 4)
    length, offset = _read_u32(payload, 0)
    assert payload[offset : offset + length].decode("utf-8") == "Rhetoric"

    legacy = b"The Oracle"
    old_payload = len(legacy).to_bytes(4, "little") + legacy + payload[offset + length :]
    legacy_blocks, audio = _read_blocks(destination.read_bytes())
    output = bytearray(b"fLaC")
    for index, (kind, value) in enumerate(legacy_blocks):
        if kind == 4:
            value = old_payload
        output.append((0x80 if index == len(legacy_blocks) - 1 else 0) | kind)
        output.extend(len(value).to_bytes(3, "big"))
        output.extend(value)
    destination.write_bytes(output + audio)
    assert read_vorbis_comments(destination)["TITLE"] == ["First"]
