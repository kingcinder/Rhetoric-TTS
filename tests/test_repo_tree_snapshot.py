from pathlib import Path

from tests.helpers import repo_tree_snapshot


def test_metadata_only_snapshot_does_not_read_file_contents(tmp_path, monkeypatch):
    sample = tmp_path / "user-owned.txt"
    sample.write_text("private fixture content", encoding="utf-8")

    def reject_read_bytes(_path):
        raise AssertionError("metadata-only snapshots must not open file contents")

    monkeypatch.setattr(Path, "read_bytes", reject_read_bytes)
    snapshot = repo_tree_snapshot(tmp_path, hash_contents=False)

    assert "size=" in snapshot["user-owned.txt"]
    assert "mtime=" in snapshot["user-owned.txt"]
    assert "sha256=not-read" in snapshot["user-owned.txt"]
