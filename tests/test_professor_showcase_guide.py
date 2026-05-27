from pathlib import Path


def test_professor_showcase_guide_covers_private_review_flow():
    content = Path("docs/PROFESSOR_SHOWCASE_GUIDE.md").read_text(encoding="utf-8")

    for expected in [
        "Professor Showcase Guide",
        "private technical review",
        "MeatPy handles ITCH parsing and LOB reconstruction",
        "public-safe portfolio version",
        "Private Nasdaq ITCH .gz",
        "message_events, order_events, lob_snapshots",
        "reports/final_evidence_report.md",
        "reports/lob_10m_comparison.md",
        "evidence/README.md",
        "docs/DATA_CONTRACTS.md",
        "docs/OPERATIONS_RUNBOOK.md",
        "29,156,757",
        "614,578",
        "535,626",
        "5406828",
        "does not prove full market microstructure correctness",
        "Do not present this as a trading strategy",
    ]:
        assert expected in content


def test_readme_links_professor_showcase_guide():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "docs/PROFESSOR_SHOWCASE_GUIDE.md" in content
