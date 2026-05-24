"""Raw-data safety scanner for the ITCH data pipeline.

Purpose
-------
Before CI or Docker are added, the project needs a programmatic check that
no raw Nasdaq ITCH data, large generated Parquet outputs, or private data
artifacts have crept into the repo tree.

This module scans a given repo root and returns a structured result that
the CLI can print and that CI can use as an exit-code gate.

Policy (A + B combination)
--------------------------
Forbidden by path:
  - ``data/**/*.gz``          raw Nasdaq/ITCH feed files
  - ``data/**/*.parquet``     any Parquet under the raw-data directory
  - ``outputs/**/*.parquet``  large generated outputs

Forbidden by path + extension mismatch:
  - any ``*.gz`` file under ``logs/`` that is NOT a ``.tar.gz`` bundle
    (a plain ``.gz`` there is almost certainly a misplaced raw feed)

Allowed by path + extension:
  - ``logs/**/*.tar.gz``      approved proof bundles
  - ``logs/**/*.json``        copied validation/manifest JSON
  - ``logs/**/*.out``         SLURM stdout logs
  - ``logs/**/*.err``         SLURM stderr logs
  - everything else           not checked by this scanner

Design notes
------------
- Uses only ``pathlib`` — no extra dependencies.
- ``scan_for_forbidden_artifacts`` is the public function used by the CLI
  and by tests.
- Tests use ``tmp_path`` (pytest) to build fake directory trees so no real
  Nasdaq data is needed.
"""
from __future__ import annotations

from pathlib import Path


# ---------------------------------------------------------------------------
# Internal rule helpers
# ---------------------------------------------------------------------------

def _is_forbidden(path: Path, repo_root: Path) -> tuple[bool, str]:
    """Return (True, reason) if *path* violates a raw-data policy rule.

    Parameters
    ----------
    path:
        Absolute path to one file inside the repo tree.
    repo_root:
        Absolute repo root used to compute the relative path for messages.

    Returns
    -------
    A ``(forbidden, reason)`` tuple.  ``forbidden`` is ``False`` for allowed
    files; ``reason`` is an empty string in that case.
    """
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        # File is outside the repo root — not our concern.
        return False, ""

    parts = rel.parts  # e.g. ("data", "nasdaq_bx_itch", "20191230.BX_ITCH_50.gz")
    suffix = path.suffix.lower()        # ".gz", ".parquet", …
    name_lower = path.name.lower()

    # Rule 1: anything under data/ that is a .gz file (raw ITCH feed).
    if parts and parts[0] == "data" and suffix == ".gz":
        return True, (
            f"Raw ITCH feed file detected under data/: {rel}"
        )

    # Rule 2: any Parquet file directly under data/ (should never be there).
    if parts and parts[0] == "data" and suffix == ".parquet":
        return True, (
            f"Parquet file detected under data/: {rel}"
        )

    # Rule 3: large generated Parquet outputs under outputs/.
    if parts and parts[0] == "outputs" and suffix == ".parquet":
        return True, (
            f"Generated Parquet output detected under outputs/: {rel}"
        )

    # Rule 4: a plain .gz file that landed under logs/ but is NOT a .tar.gz
    # bundle.  A proof bundle is always a .tar.gz (ends in ".tar.gz");
    # a misplaced raw feed ends in just ".gz".
    if (
        parts
        and parts[0] == "logs"
        and suffix == ".gz"
        and not name_lower.endswith(".tar.gz")
    ):
        return True, (
            f"Plain .gz file (not a .tar.gz proof bundle) detected under logs/: {rel}"
        )

    return False, ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scan_for_forbidden_artifacts(repo_root: str | Path) -> dict:
    """Walk *repo_root* and return a structured safety-scan result.

    Parameters
    ----------
    repo_root:
        Path to the root of the repository to scan.  Defaults to the current
        working directory when called from the CLI.

    Returns
    -------
    A dict with the following keys:

    ``status``
        ``"passed"`` if no violations were found, ``"failed"`` otherwise.
    ``repo_root``
        The resolved absolute path that was scanned (as a string).
    ``files_checked``
        Total number of files visited during the walk.
    ``violations``
        A list of violation dicts, each containing ``"path"`` and
        ``"reason"`` strings.
    ``checks_run``
        Number of distinct policy rules applied (informational).
    """
    root = Path(repo_root).resolve()

    violations: list[dict] = []
    files_checked = 0

    for file_path in root.rglob("*"):
        # Skip directories and hidden / cache trees that are not our concern.
        if not file_path.is_file():
            continue

        # Skip .venv, __pycache__, .git, .mypy_cache, etc.
        relative = file_path.relative_to(root)
        first_part = relative.parts[0] if relative.parts else ""
        if first_part.startswith(".") or first_part in ("__pycache__", ".venv", "node_modules"):
            continue
        # Skip nested __pycache__ anywhere in the tree.
        if "__pycache__" in relative.parts:
            continue

        files_checked += 1
        forbidden, reason = _is_forbidden(file_path, root)
        if forbidden:
            violations.append({"path": str(relative), "reason": reason})

    status = "passed" if not violations else "failed"

    return {
        "status": status,
        "repo_root": str(root),
        "files_checked": files_checked,
        "violations": violations,
        "checks_run": 4,  # number of distinct policy rules in _is_forbidden
    }
