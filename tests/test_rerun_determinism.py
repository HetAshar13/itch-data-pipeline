import json
from pathlib import Path
from itch_data_pipeline.manifests.manifest_writer import build_sample_manifest, write_manifest
from itch_data_pipeline.utils.hashing import sha256_file


def test_manifest_write_is_deterministic_for_same_content(tmp_path: Path):
    manifest = build_sample_manifest()
    manifest["start_time"] = "2026-01-01T00:00:00+00:00"
    manifest["end_time"] = "2026-01-01T00:00:00+00:00"

    first = tmp_path / "manifest_first.json"
    second = tmp_path / "manifest_second.json"

    write_manifest(manifest, first)
    write_manifest(manifest, second)

    assert sha256_file(first) == sha256_file(second)
    json.loads(first.read_text(encoding="utf-8"))
