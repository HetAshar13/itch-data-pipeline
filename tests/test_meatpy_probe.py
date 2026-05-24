from itch_data_pipeline.meatpy_integration.probe import probe_meatpy


def test_probe_meatpy_returns_dependency_status():
    result = probe_meatpy()

    assert isinstance(result["installed"], bool)
    assert isinstance(result["version"], str)

    if result["installed"]:
        assert result["version"] != "not_available"
