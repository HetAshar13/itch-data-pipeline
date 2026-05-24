from pathlib import Path


def test_operations_runbook_documents_core_operational_paths():
    content = Path("docs/OPERATIONS_RUNBOOK.md").read_text(encoding="utf-8")

    assert "ssh iris-cluster" in content
    assert "sbatch hpc/submit_lob_snapshots.slurm" in content
    assert "sbatch hpc/submit_lob_snapshots_until_eof.slurm" in content
    assert "scp iris-cluster:" in content
    assert "docker build -t itch-data-pipeline:test ." in content


def test_operations_runbook_documents_safety_and_failures():
    content = Path("docs/OPERATIONS_RUNBOOK.md").read_text(encoding="utf-8")

    assert "Do not commit or share raw Nasdaq ITCH" in content
    assert "Do not copy raw ITCH input or `part-000.parquet`" in content
    assert "Raw-data safety fails locally" in content
    assert "Validation fails" in content
