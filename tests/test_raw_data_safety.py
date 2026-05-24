"""Tests for the raw-data safety scanner.

All tests use pytest's ``tmp_path`` fixture to build fake directory trees.
No real Nasdaq data is needed.

Policy under test (A + B)
--------------------------
- data/**/*.gz        → forbidden (raw ITCH feed, rule 1)
- data/**/*.parquet   → forbidden (parquet in raw dir, rule 2)
- outputs/**/*.parquet→ forbidden (generated output, rule 3)
- logs/**/*.gz (not .tar.gz) → forbidden (misplaced raw feed, rule 4)
- logs/**/*.tar.gz    → ALLOWED  (proof bundle)
- reports/*.md        → ALLOWED  (Markdown report)
- anything in .venv/  → SKIPPED  (not checked)
"""
from __future__ import annotations

from pathlib import Path

import pytest

from itch_data_pipeline.safety.raw_data import scan_for_forbidden_artifacts, _is_forbidden


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _touch(path: Path) -> Path:
    """Create *path* and all parents, write an empty file, return path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"fake content")
    return path


# ---------------------------------------------------------------------------
# Unit tests for _is_forbidden (the rule engine)
# ---------------------------------------------------------------------------

class TestIsForbiddenRules:
    """Low-level tests for each policy rule in isolation."""

    def test_rule1_raw_gz_under_data_is_forbidden(self, tmp_path):
        f = _touch(tmp_path / "data" / "nasdaq_bx_itch" / "20191230.BX_ITCH_50.gz")
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is True
        assert "data/" in reason
        assert "Raw ITCH feed" in reason

    def test_rule2_parquet_under_data_is_forbidden(self, tmp_path):
        f = _touch(tmp_path / "data" / "some_partition" / "part-000.parquet")
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is True
        assert "data/" in reason

    def test_rule3_parquet_under_outputs_is_forbidden(self, tmp_path):
        f = _touch(
            tmp_path
            / "outputs"
            / "local"
            / "dataset=lob_snapshots"
            / "date=2019-12-30"
            / "symbol=SPY"
            / "part-000.parquet"
        )
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is True
        assert "outputs/" in reason

    def test_rule4_plain_gz_under_logs_is_forbidden(self, tmp_path):
        # A plain .gz (not .tar.gz) that ended up under logs/ is a red flag.
        f = _touch(tmp_path / "logs" / "accidental_raw.gz")
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is True
        assert "logs/" in reason
        assert "Plain .gz" in reason

    def test_tar_gz_proof_bundle_under_logs_is_allowed(self, tmp_path):
        f = _touch(tmp_path / "logs" / "week12_lob_until_eof_5406828.tar.gz")
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is False
        assert reason == ""

    def test_markdown_report_is_allowed(self, tmp_path):
        f = _touch(tmp_path / "reports" / "week12_final_report.md")
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is False

    def test_json_proof_artifact_under_logs_is_allowed(self, tmp_path):
        f = _touch(tmp_path / "logs" / "week10_lob_5404108" / "lob_manifest_SPY_2019-12-30_5404108.json")
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is False

    def test_slurm_out_log_under_logs_is_allowed(self, tmp_path):
        f = _touch(tmp_path / "logs" / "hpc_week6_5386100.out")
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is False

    def test_slurm_err_log_under_logs_is_allowed(self, tmp_path):
        f = _touch(tmp_path / "logs" / "hpc_week6_5386100.err")
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is False

    def test_source_py_file_is_allowed(self, tmp_path):
        f = _touch(tmp_path / "src" / "itch_data_pipeline" / "cli.py")
        forbidden, reason = _is_forbidden(f, tmp_path)
        assert forbidden is False

    def test_file_outside_repo_root_is_allowed(self, tmp_path):
        # File outside the root should not raise and should return False.
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".gz", delete=False) as tf:
            outside = Path(tf.name)
        try:
            forbidden, reason = _is_forbidden(outside, tmp_path)
            assert forbidden is False
        finally:
            os.unlink(outside)


# ---------------------------------------------------------------------------
# Integration tests for scan_for_forbidden_artifacts
# ---------------------------------------------------------------------------

class TestScanForForbiddenArtifacts:
    """End-to-end scan tests over a fake repo tree."""

    def test_clean_tree_passes(self, tmp_path):
        """A repo with only safe files should pass."""
        _touch(tmp_path / "reports" / "week12_final_report.md")
        _touch(tmp_path / "logs" / "week12_lob_until_eof_5406828.tar.gz")
        _touch(tmp_path / "logs" / "hpc_week6_5386100.out")
        _touch(tmp_path / "src" / "itch_data_pipeline" / "cli.py")

        result = scan_for_forbidden_artifacts(tmp_path)

        assert result["status"] == "passed"
        assert result["violations"] == []
        assert result["files_checked"] >= 4

    def test_raw_gz_in_data_fails(self, tmp_path):
        """A raw .gz ITCH file under data/ must be detected."""
        _touch(tmp_path / "data" / "nasdaq_bx_itch" / "20191230.BX_ITCH_50.gz")

        result = scan_for_forbidden_artifacts(tmp_path)

        assert result["status"] == "failed"
        assert len(result["violations"]) == 1
        assert "data" in result["violations"][0]["path"]

    def test_parquet_in_outputs_fails(self, tmp_path):
        """Generated Parquet under outputs/ must be detected."""
        _touch(
            tmp_path
            / "outputs"
            / "local"
            / "dataset=lob_snapshots"
            / "date=2019-12-30"
            / "symbol=SPY"
            / "part-000.parquet"
        )

        result = scan_for_forbidden_artifacts(tmp_path)

        assert result["status"] == "failed"
        assert any("outputs" in v["path"] for v in result["violations"])

    def test_plain_gz_in_logs_fails(self, tmp_path):
        """A plain .gz (not .tar.gz) under logs/ must be detected."""
        _touch(tmp_path / "logs" / "raw_feed_misplaced.gz")

        result = scan_for_forbidden_artifacts(tmp_path)

        assert result["status"] == "failed"
        assert any("logs" in v["path"] for v in result["violations"])

    def test_tar_gz_in_logs_is_clean(self, tmp_path):
        """A .tar.gz proof bundle under logs/ must not trigger a violation."""
        _touch(tmp_path / "logs" / "week12_lob_until_eof_5406828.tar.gz")

        result = scan_for_forbidden_artifacts(tmp_path)

        assert result["status"] == "passed"
        assert result["violations"] == []

    def test_multiple_violations_all_reported(self, tmp_path):
        """Multiple forbidden files should all appear in violations list."""
        _touch(tmp_path / "data" / "nasdaq_bx_itch" / "20191230.BX_ITCH_50.gz")
        _touch(tmp_path / "outputs" / "local" / "lob_snapshots" / "part-000.parquet")

        result = scan_for_forbidden_artifacts(tmp_path)

        assert result["status"] == "failed"
        assert len(result["violations"]) == 2

    def test_venv_directory_is_skipped(self, tmp_path):
        """Files under .venv/ must be skipped entirely."""
        # A .gz inside .venv should NOT trigger a violation.
        _touch(tmp_path / ".venv" / "lib" / "some_package" / "data.gz")

        result = scan_for_forbidden_artifacts(tmp_path)

        assert result["status"] == "passed"
        assert result["violations"] == []

    def test_result_contains_required_keys(self, tmp_path):
        result = scan_for_forbidden_artifacts(tmp_path)
        assert "status" in result
        assert "repo_root" in result
        assert "files_checked" in result
        assert "violations" in result
        assert "checks_run" in result

    def test_checks_run_is_four(self, tmp_path):
        result = scan_for_forbidden_artifacts(tmp_path)
        assert result["checks_run"] == 4

    def test_repo_root_in_result_is_absolute(self, tmp_path):
        result = scan_for_forbidden_artifacts(tmp_path)
        assert Path(result["repo_root"]).is_absolute()
