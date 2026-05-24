from pathlib import Path
from itch_data_pipeline.utils.hashing import sha256_file, sha256_text


def test_sha256_text_is_stable():
    assert sha256_text("hello") == sha256_text("hello")
    assert sha256_text("hello") != sha256_text("world")


def test_sha256_file_is_stable(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("same content", encoding="utf-8")
    assert sha256_file(file_path) == sha256_file(file_path)


def test_sha256_file_changes_when_content_changes(tmp_path: Path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_text("first content", encoding="utf-8")
    second.write_text("second content", encoding="utf-8")

    assert sha256_file(first) != sha256_file(second)
