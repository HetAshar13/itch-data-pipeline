from pathlib import Path
from itch_data_pipeline.manifests.manifest_writer import build_sample_manifest, read_manifest, write_manifest


def test_sample_manifest_has_required_fields():
    manifest = build_sample_manifest()
    required = {
        "run_id",
        "date",
        "symbol",
        "input_file",
        "output_paths",
        "schema_version",
        "status",
        "row_counts",
        "validation_summary",
    }
    assert required.issubset(manifest.keys())


def test_write_and_read_manifest(tmp_path: Path):
    manifest = build_sample_manifest()
    output = tmp_path / "manifest.json"
    write_manifest(manifest, output)
    loaded = read_manifest(output)
    assert loaded["run_id"] == manifest["run_id"]
    assert loaded["schema_version"] == "1.0"


def test_sample_manifest_validation_summary_starts_not_run():
    manifest = build_sample_manifest()

    assert manifest["validation_summary"]["rules_run"] == 0
    assert manifest["validation_summary"]["rules_failed"] == 0
    assert manifest["validation_summary"]["status"] == "not_run"
