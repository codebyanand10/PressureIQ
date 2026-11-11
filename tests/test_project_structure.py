"""Unit tests for project directory architecture and essential files.

Verifies that all Phase 0 directories and boilerplate configuration files
exist and follow the expected specification.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from src.config import config


def test_required_directories_exist():
    """Verify that all mandatory project directories exist."""
    root = config.project_root

    expected_directories = [
        root / "data" / "raw",
        root / "data" / "processed",
        root / "data" / "intermediate",
        root / "data" / "external",
        root / "notebooks",
        root / "src",
        root / "dashboard",
        root / "dashboard" / "components",
        root / "dashboard" / "pages",
        root / "dashboard" / "styles",
        root / "dashboard" / "assets",
        root / "tests",
        root / "outputs" / "rankings",
        root / "outputs" / "charts",
        root / "outputs" / "reports",
        root / "outputs" / "logs",
        root / "config",
        root / "docs",
    ]

    for d in expected_directories:
        assert d.is_dir(), f"Expected directory does not exist: {d}"


def test_essential_project_files_exist():
    """Verify that all core Phase 0 root and configuration files exist."""
    root = config.project_root

    expected_files = [
        root / "config" / "settings.yaml",
        root / "requirements.txt",
        root / ".env.example",
        root / ".gitignore",
        root / "README.md",
        root / "run.py",
        root / "dashboard" / "app.py",
        root / "src" / "config.py",
        root / "src" / "logger.py",
        root / "src" / "__init__.py",
        root / "dashboard" / "components" / "__init__.py",
        root / "tests" / "__init__.py",
        root / "docs" / "architecture.md",
        root / "docs" / "development_roadmap.md",
        root / "docs" / "environment_setup.md",
    ]

    for f in expected_files:
        assert f.is_file(), f"Expected file does not exist: {f}"


def test_notebooks_exist():
    """Verify that all 8 planned Phase exploration notebooks exist."""
    root = config.project_root
    notebook_dir = root / "notebooks"

    expected_notebooks = [
        "01_dataset_exploration.ipynb",
        "02_data_quality.ipynb",
        "03_dataset_relationships.ipynb",
        "04_match_state_reconstruction.ipynb",
        "05_pressure_analysis.ipynb",
        "06_batting_analysis.ipynb",
        "07_bowling_analysis.ipynb",
        "08_ranking_validation.ipynb",
    ]

    for nb in expected_notebooks:
        nb_path = notebook_dir / nb
        assert nb_path.is_file(), f"Expected notebook missing: {nb}"


def test_future_src_modules_exist():
    """Verify that future module stubs exist with appropriate documentation."""
    root = config.project_root
    src_dir = root / "src"

    expected_modules = [
        "data_loader.py",
        "data_validation.py",
        "preprocessing.py",
        "match_state.py",
        "pressure_engine.py",
        "batting_engine.py",
        "bowling_engine.py",
        "player_baseline.py",
        "ranking_engine.py",
        "statistical_validation.py",
        "report_generator.py",
    ]

    for mod in expected_modules:
        mod_path = src_dir / mod
        assert mod_path.is_file(), f"Expected module stub missing: {mod}"
        content = mod_path.read_text(encoding="utf-8")
        assert "TODO" in content, f"Module stub {mod} should contain TODO comment"

