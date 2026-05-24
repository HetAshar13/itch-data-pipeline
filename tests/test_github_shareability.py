import subprocess
from pathlib import Path


def test_readme_is_recruiter_ready_and_public_safe():
    content = Path("README.md").read_text(encoding="utf-8")

    for expected in [
        "[![CI]",
        "At A Glance",
        "29,156,757",
        "614,578",
        "535,626",
        "126",
        "Docker",
        "GitHub Actions CI",
        "Iris SLURM",
        "```mermaid",
        "Engineering Decisions I Made",
        "I used MeatPy instead of writing a parser",
        "I validate before querying",
        "I store ITCH prices as raw integer units",
        "Raw Nasdaq data and large Parquet outputs excluded from Git",
        "reports/portfolio_case_study.md",
        "reports/final_evidence_report.md",
        "reports/lob_10m_comparison.md",
        "docs/DATA_CONTRACTS.md",
        "docs/OPERATIONS_RUNBOOK.md",
        "docs/REPRODUCIBILITY.md",
        "evidence/",
        "does not prove complete market microstructure correctness",
    ]:
        assert expected in content


def test_github_publish_checklist_covers_safe_publish_flow():
    content = Path("docs/GITHUB_PUBLISH_CHECKLIST.md").read_text(encoding="utf-8")

    for expected in [
        "itch-data-pipeline",
        "data-engineering",
        "market-data",
        "python",
        "git init",
        "git remote add origin",
        "git push -u origin main",
        "check-raw-data-safety",
        "data/",
        "outputs/",
        "logs/",
        "*.parquet",
        "raw Nasdaq",
        "evidence/",
        "reports/final_evidence_report.md",
        "reports/lob_10m_comparison.md",
    ]:
        assert expected in content


def test_evidence_readme_documents_public_safe_boundaries():
    content = Path("evidence/README.md").read_text(encoding="utf-8")

    for expected in [
        "Public-Safe Evidence Artifacts",
        "SLURM `.out` logs",
        "Manifest JSON files",
        "Validation JSON files",
        "DuckDB summary JSON files",
        "no raw ITCH files",
        "no Nasdaq feed `.gz` files",
        "no generated `part-000.parquet` files",
        "week6_hpc/",
        "week11_lob_10m/",
        "week12_lob_until_eof_5406828/",
    ]:
        assert expected in content


def test_gitignore_keeps_private_and_generated_artifacts_out_of_git():
    content = Path(".gitignore").read_text(encoding="utf-8")

    for expected in [
        ".venv/",
        "data/",
        "outputs/",
        "logs/",
        "*.parquet",
        "*.gz",
        "configs/local.yaml",
        "*.egg-info/",
    ]:
        assert expected in content


def test_key_public_reports_are_not_empty():
    for report_path in [
        "reports/portfolio_case_study.md",
        "reports/final_evidence_report.md",
        "reports/lob_10m_comparison.md",
    ]:
        content = Path(report_path).read_text(encoding="utf-8")
        assert len(content.strip()) > 500

    comparison = Path("reports/lob_10m_comparison.md").read_text(encoding="utf-8")
    assert "SPY" in comparison
    assert "QQQ" in comparison
    assert "IWM" in comparison
    assert "10000000" in comparison


def test_public_docs_do_not_expose_ai_workflow_terms():
    tracked = subprocess.run(
        ["git", "ls-files", "README.md", "docs/*.md", "reports/*.md", "evidence/README.md"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    public_paths = [Path(path) for path in tracked]

    forbidden_terms = [
        "Codex",
        "Antigravity",
        "context snapshot",
        "prompts/",
    ]

    for path in public_paths:
        content = path.read_text(encoding="utf-8")
        for term in forbidden_terms:
            assert term.lower() not in content.lower(), f"{term!r} found in {path}"
