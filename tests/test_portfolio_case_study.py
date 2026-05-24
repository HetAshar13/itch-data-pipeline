from pathlib import Path


def test_portfolio_case_study_contains_required_sections():
    content = Path("reports/portfolio_case_study.md").read_text(encoding="utf-8")

    for heading in [
        "## Problem",
        "## Architecture",
        "## Data Products",
        "## Validation Strategy",
        "## Analytics Layer",
        "## HPC Proof",
        "## Reproducibility",
        "## Data Governance",
        "## Limitations",
        "## Lessons Learned",
    ]:
        assert heading in content


def test_portfolio_case_study_contains_evidence_and_safety_boundaries():
    content = Path("reports/portfolio_case_study.md").read_text(encoding="utf-8")

    for expected in [
        "MeatPy",
        "DuckDB",
        "Streamlit",
        "Iris HPC",
        "SLURM",
        "1,000,000",
        "796,151",
        "535,626",
        "29,156,757",
        "614,578",
        "126 passed",
        "111 passed in 7.27s",
        "raw Nasdaq data",
        "raw ITCH integer units",
        "does not prove complete market microstructure correctness",
    ]:
        assert expected in content


def test_portfolio_case_study_does_not_claim_streamlit_runs_pipeline():
    content = Path("reports/portfolio_case_study.md").read_text(encoding="utf-8")

    assert "Streamlit reads existing artifacts only" in content
    assert "does not trigger extraction" in content
