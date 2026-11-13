"""PressureIQ Project Inventory Engine.

Exhaustively scans the project workspace, identifies required, untracked,
or temporary artifacts, calculates file counts, sizes, and cryptographic
hashes for data and ranking assets.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

from src.logger import get_logger

logger = get_logger("PressureIQ.FinalAudit.Inventory")


@dataclass
class FileMetadata:
    """Metadata for an inventoried file."""
    path: str
    relative_path: str
    size_bytes: int
    category: str
    extension: str
    sha256: str | None = None


@dataclass
class ProjectInventoryResult:
    """Comprehensive project inventory summary."""
    total_files: int
    total_size_bytes: int
    category_counts: Dict[str, int] = field(default_factory=dict)
    category_sizes: Dict[str, int] = field(default_factory=dict)
    missing_required_files: List[str] = field(default_factory=list)
    temporary_files: List[str] = field(default_factory=list)
    duplicate_candidates: List[Dict[str, Any]] = field(default_factory=list)
    key_file_hashes: Dict[str, str] = field(default_factory=dict)
    file_records: List[FileMetadata] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "total_files": self.total_files,
            "total_size_bytes": self.total_size_bytes,
            "category_counts": self.category_counts,
            "category_sizes": self.category_sizes,
            "missing_required_files": self.missing_required_files,
            "temporary_files": self.temporary_files,
            "duplicate_candidates_count": len(self.duplicate_candidates),
            "key_file_hashes": self.key_file_hashes,
        }


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class ProjectInventory:
    """Auditor for scanning and verifying project assets."""

    REQUIRED_FILES = [
        "README.md",
        "requirements.txt",
        ".gitignore",
        "config/settings.yaml",
        "data/raw/ball_by_ball.csv",
        "data/raw/matches.csv",
        "data/raw/teams.csv",
        "data/raw/playing_eleven.csv",
        "data/raw/competitions.csv",
        "data/raw/competition_team_player_mapping.csv",
        "data/processed/match_state_reconstructed.parquet",
        "data/processed/integrated_ball_by_ball.parquet",
        "data/processed/pressure/pressure_scores.parquet",
        "data/processed/baselines/batting_overall_baseline.parquet",
        "data/processed/baselines/bowling_overall_baseline.parquet",
        "data/processed/rankings/batter_ratings.parquet",
        "data/processed/rankings/bowler_ratings.parquet",
        "outputs/rankings/top_10_batters.csv",
        "outputs/rankings/top_10_batters.xlsx",
        "outputs/rankings/top_10_bowlers.csv",
        "outputs/rankings/top_10_bowlers.xlsx",
        "outputs/validation/robustness_scorecard.csv",
        "outputs/validation/bootstrap_summary.csv",
        "docs/methodology/PressureIQ_Methodology_Report.md",
        "docs/methodology/PressureIQ_Methodology_Report.pdf",
        "docs/methodology/PressureIQ_Methodology_Report.docx",
        "dashboard/app.py",
    ]

    TEMPORARY_PATTERNS = [
        ".tmp",
        ".temp",
        "~",
        ".bak",
        ".orig",
        "Thumbs.db",
    ]

    EXCLUDE_DIRS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".idea",
        ".vscode",
        "submission",
    }

    def __init__(self, root_dir: Path | str | None = None) -> None:
        """Initialize inventory scanner."""
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()

    def categorize_path(self, rel_path: Path) -> str:
        """Categorize file based on location and extension."""
        parts = rel_path.parts
        if not parts:
            return "root"

        ext = rel_path.suffix.lower()
        first_part = parts[0]

        if first_part == "src":
            return "source_code"
        if first_part == "dashboard":
            return "dashboard"
        if first_part == "tests":
            return "tests"
        if first_part == "config":
            return "configuration"
        if first_part == "data":
            if len(parts) > 1 and parts[1] == "raw":
                return "raw_data"
            return "processed_data"
        if first_part == "docs":
            return "documentation"
        if first_part == "outputs":
            if "charts" in parts:
                return "charts"
            if "rankings" in parts:
                return "rankings"
            if "validation" in parts:
                return "validation"
            if "methodology" in parts:
                return "methodology_outputs"
            return "outputs"
        if first_part == "submission":
            return "submission"

        if ext == ".py":
            return "source_code"
        if ext in [".md", ".rst", ".txt"]:
            return "documentation"
        return "other"

    def scan(self) -> ProjectInventoryResult:
        """Scan project workspace and return inventory."""
        logger.info(f"Scanning project workspace at: {self.root_dir}")

        file_records: List[FileMetadata] = []
        category_counts: Dict[str, int] = {}
        category_sizes: Dict[str, int] = {}
        temporary_files: List[str] = []
        key_file_hashes: Dict[str, str] = {}

        total_bytes = 0

        # Traverse workspace
        for root, dirs, files in os.walk(self.root_dir):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for file_name in files:
                full_path = Path(root) / file_name
                try:
                    rel_path = full_path.relative_to(self.root_dir)
                except ValueError:
                    continue

                # Skip root-level virtualenvs if present
                if any(p in self.EXCLUDE_DIRS for p in rel_path.parts):
                    continue

                size = full_path.stat().st_size
                total_bytes += size
                category = self.categorize_path(rel_path)
                ext = full_path.suffix.lower()

                # Check temporary
                if any(pat in file_name for pat in self.TEMPORARY_PATTERNS) or file_name.endswith(".pyc"):
                    temporary_files.append(str(rel_path))

                category_counts[category] = category_counts.get(category, 0) + 1
                category_sizes[category] = category_sizes.get(category, 0) + size

                # Hash key files
                rel_str = str(rel_path).replace("\\", "/")
                sha = None
                if rel_str in self.REQUIRED_FILES or category in ["raw_data", "rankings"]:
                    sha = compute_sha256(full_path)
                    key_file_hashes[rel_str] = sha

                file_records.append(
                    FileMetadata(
                        path=str(full_path),
                        relative_path=str(rel_path),
                        size_bytes=size,
                        category=category,
                        extension=ext,
                        sha256=sha,
                    )
                )

        # Check missing required files
        missing: List[str] = []
        for req in self.REQUIRED_FILES:
            target = self.root_dir / req
            if not target.exists():
                missing.append(req)

        result = ProjectInventoryResult(
            total_files=len(file_records),
            total_size_bytes=total_bytes,
            category_counts=category_counts,
            category_sizes=category_sizes,
            missing_required_files=missing,
            temporary_files=temporary_files,
            duplicate_candidates=[],
            key_file_hashes=key_file_hashes,
            file_records=file_records,
        )

        logger.info(
            f"Inventory scan complete: {result.total_files} files, "
            f"{result.total_size_bytes / (1024*1024):.2f} MB across "
            f"{len(category_counts)} categories."
        )
        return result
