"""Unit tests for Phase 8 export and reporting module."""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.ranking.export import (
    export_rankings_datasets,
    export_ranking_reports,
)


@pytest.fixture
def mock_export_data():
    """Mock datasets for export verification."""
    top_10_bat = pd.DataFrame({
        "rank": list(range(1, 11)),
        "player_id": [f"bat_{i}" for i in range(1, 11)],
        "player_name": [f"Batter {i}" for i in range(1, 11)],
        "final_fbpr": [75.0 - i for i in range(10)],
        "bppi": [70.0 - i for i in range(10)],
        "balls_faced": [150 - i * 5 for i in range(10)],
        "strike_rate": [160.0 - i * 2 for i in range(10)],
        "ci_lower_fbpr": [70.0 - i for i in range(10)],
        "ci_upper_fbpr": [80.0 - i for i in range(10)],
        "ci_width_fbpr": [10.0] * 10,
        "reliability_level": ["High"] * 10,
    })

    top_10_bowl = pd.DataFrame({
        "rank": list(range(1, 11)),
        "player_id": [f"bowl_{i}" for i in range(1, 11)],
        "player_name": [f"Bowler {i}" for i in range(1, 11)],
        "final_fbor": [50.0 - i * 0.5 for i in range(10)],
        "bppi_b": [52.0 - i * 0.5 for i in range(10)],
        "legal_balls_bowled": [180 - i * 5 for i in range(10)],
        "economy_rate": [7.5 + i * 0.1 for i in range(10)],
        "ci_lower_fbor": [47.0 - i * 0.5 for i in range(10)],
        "ci_upper_fbor": [53.0 - i * 0.5 for i in range(10)],
        "ci_width_fbor": [6.0] * 10,
        "reliability_level": ["High"] * 10,
    })

    all_bat = top_10_bat.copy()
    all_bowl = top_10_bowl.copy()
    excluded = pd.DataFrame({
        "player_id": ["excl_1"],
        "player_name": ["Excluded Player"],
        "role": ["batter"],
        "exclusion_reason": ["Insufficient Evidence (<40 balls)"],
        "balls_faced": [20],
        "is_eligible": [False],
    })

    cfg = {"version": "1.0.0", "active_profile": "primary"}
    validations = {"mathematical_consistency": True, "top_10_counts": True}
    fairness = {"ipl_proportion_batting": 0.5, "ipl_proportion_bowling": 0.5}

    return {
        "top_10_batters": top_10_bat,
        "top_10_bowlers": top_10_bowl,
        "all_batters": all_bat,
        "all_bowlers": all_bowl,
        "excluded_players": excluded,
        "ranking_cfg_dict": cfg,
        "validation_checks": validations,
        "fairness_audit": fairness,
    }


def test_export_rankings_datasets(tmp_path, mock_export_data):
    """Test exporting parquet datasets."""
    datasets = {
        "batter_ratings": mock_export_data["all_batters"],
        "bowler_ratings": mock_export_data["all_bowlers"],
    }
    paths = export_rankings_datasets(datasets, tmp_path)
    assert "batter_ratings" in paths
    assert "bowler_ratings" in paths
    assert paths["batter_ratings"].exists()
    assert paths["bowler_ratings"].suffix == ".parquet"

    # Read back and verify row count
    df_read = pd.read_parquet(paths["batter_ratings"])
    assert len(df_read) == 10


def test_export_ranking_reports(tmp_path, mock_export_data):
    """Test exporting CSV, XLSX, JSON and Markdown analytical reports."""
    paths = export_ranking_reports(
        top_10_batters=mock_export_data["top_10_batters"],
        top_10_bowlers=mock_export_data["top_10_bowlers"],
        all_batters=mock_export_data["all_batters"],
        all_bowlers=mock_export_data["all_bowlers"],
        excluded_players=mock_export_data["excluded_players"],
        ranking_cfg_dict=mock_export_data["ranking_cfg_dict"],
        validation_checks=mock_export_data["validation_checks"],
        fairness_audit=mock_export_data["fairness_audit"],
        output_dir=tmp_path,
    )

    # Verify key expected files
    assert (tmp_path / "top_10_batters.csv").exists()
    assert (tmp_path / "top_10_batters.xlsx").exists()
    assert (tmp_path / "top_10_bowlers.csv").exists()
    assert (tmp_path / "top_10_bowlers.xlsx").exists()
    assert (tmp_path / "ranking_configuration.json").exists()
    assert (tmp_path / "PHASE_8_FINAL_REPORT.md").exists()

    # Verify Excel is readable by pandas
    df_excel = pd.read_excel(tmp_path / "top_10_batters.xlsx")
    assert len(df_excel) == 10
    assert "final_fbpr" in df_excel.columns
