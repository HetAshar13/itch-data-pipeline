from pathlib import Path

import pytest

from itch_data_pipeline.config import load_yaml


def test_load_yaml_reads_mapping(tmp_path: Path):
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        "paths:\n"
        "  input_root: data/input\n"
        "  output_root: outputs/local\n"
        "processing:\n"
        "  default_symbol: AAPL\n",
        encoding="utf-8",
    )

    loaded = load_yaml(config_path)

    assert loaded["paths"]["input_root"] == "data/input"
    assert loaded["paths"]["output_root"] == "outputs/local"
    assert loaded["processing"]["default_symbol"] == "AAPL"


def test_load_yaml_raises_for_missing_file(tmp_path: Path):
    missing_path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        load_yaml(missing_path)
