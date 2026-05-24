from pathlib import Path


def test_dockerfile_builds_public_safe_test_runtime():
    content = Path("Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.11-slim" in content
    assert "pip install -r requirements.txt" in content
    assert "pip install -e ." in content
    assert 'CMD ["python", "-m", "pytest"]' in content


def test_dockerignore_excludes_raw_and_generated_artifacts():
    patterns = set(Path(".dockerignore").read_text(encoding="utf-8").splitlines())

    assert "data/" in patterns
    assert "data_fixtures/" in patterns
    assert "outputs/" in patterns
    assert "logs/" in patterns
    assert "*.parquet" in patterns
    assert "*.gz" in patterns
    assert ".venv/" in patterns
