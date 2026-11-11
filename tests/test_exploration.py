"""Unit tests for src/exploration.py.

Uses synthetic test fixtures to verify dataset discovery, inventory generation,
key validation, referential integrity, and matrix generation without modifying
or depending on real competition data.
"""

from __future__ import annotations

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.exploration import (
    RAW_DATASET_NAMES,
    discover_raw_datasets,
    generate_dataset_inventory,
    generate_data_dictionary,
    validate_primary_and_composite_keys,
    analyze_relationships,
    generate_data_availability_matrix,
)


@pytest.fixture
def synthetic_data_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with synthetic CSV files matching raw schemas."""
    data_dir = tmp_path / "raw"
    data_dir.mkdir()

    for name in RAW_DATASET_NAMES:
        csv_path = data_dir / name
        if name == "competitions.csv":
            df = pd.DataFrame({
                "comp_id": [1, 2],
                "comp_name": ["League A", "Tournament B"],
                "match_format": ["T20", "T20I"],
                "season": [2022, 2023],
            })
        elif name == "teams.csv":
            df = pd.DataFrame({
                "comp_id": [1, 1],
                "team_id": [10, 20],
                "team_name": ["Team X", "Team Y"],
            })
        elif name == "competition_team_player_mapping.csv":
            df = pd.DataFrame({
                "comp_id": [1, 1],
                "comp_name": ["League A", "League A"],
                "team_id": [10, 10],
                "team_name": ["Team X", "Team X"],
                "player_id": [100, 101],
                "player_name": ["Player One", "Player Two"],
            })
        elif name == "matches.csv":
            df = pd.DataFrame({
                "match_id": [1001, 1002],
                "comp_id": [1, 2],
                "match_number": [1, 2],
                "match_date": ["2022-01-01", "2023-01-01"],
                "stage": ["League", "Final"],
                "venue_id": [5, 6],
                "venue_country": ["India", "England"],
                "home_team_id": [10, 20],
                "home_team": ["Team X", "Team Y"],
                "away_team_id": [20, 10],
                "away_team": ["Team Y", "Team X"],
                "home_team_captain_id": [100, 101],
                "away_team_captain_id": [101, 100],
                "toss_win_team_id": [10, 20],
                "toss_opted": ["Batting", "Fielding"],
                "man_of_the_match": [100, 101],
                "first_inn_revised_overs": [np.nan, np.nan],
                "second_inn_revised_overs": [np.nan, np.nan],
                "revised_target": [np.nan, np.nan],
                "knock_out": [0, 1],
                "win_team_id": [10, 20],
                "result": ["Team X Won by 10 runs", "Team Y Won by 4 wickets"],
            })
        elif name == "playing_eleven.csv":
            df = pd.DataFrame({
                "match_id": [1001, 1001],
                "team_id": [10, 10],
                "player_id": [100, 101],
                "batting_order": [1.0, 2.0],
                "is_played": [True, True],
                "is_captain": [True, False],
                "is_wk": [False, True],
                "is_impact": [0, 0],
                "is_impact_off": [0, 0],
            })
        elif name == "ball_by_ball.csv":
            df = pd.DataFrame({
                "match_id": [1001, 1001],
                "innings": [1, 1],
                "overid": [1, 1],
                "over_ball_num": [1, 2],
                "innings_ball_num": [1, 2],
                "batting_team_id": [10, 10],
                "bowling_team_id": [20, 20],
                "striker_id": [100, 100],
                "striker_name": ["Player One", "Player One"],
                "non_striker_id": [101, 101],
                "non_striker_name": ["Player Two", "Player Two"],
                "bowler_id": [200, 200],
                "bowler_name": ["Bowler A", "Bowler A"],
                "batting_type": ["RHB", "RHB"],
                "bowling_type": ["Right-arm Fast", "Right-arm Fast"],
                "runs": [1, 4],
                "is_four": [False, True],
                "is_six": [False, False],
                "is_wicket": [False, False],
                "dismissal_type_id": [np.nan, np.nan],
                "dismissal_type": [np.nan, np.nan],
                "dismissed_player_id": [np.nan, np.nan],
                "extras_type": [np.nan, np.nan],
                "extras1_runs": [0, 0],
                "extras_2_runs": [0, 0],
                "pace_or_spin": ["Pace", "Pace"],
                "bowl_speed": [140.0, 142.5],
                "stroke": ["Drive", "Pull"],
                "delivery_style": ["Outswing", "Inswing"],
                "over_or_around": ["Over", "Over"],
                "on_or_off": ["Off-side", "On-side"],
                "delivery_ist_time": ["2022-01-01 19:30:00", "2022-01-01 19:31:00"],
            })

        df.to_csv(csv_path, index=False)

    return data_dir


def test_discover_raw_datasets_success(synthetic_data_dir: Path):
    """Verify that discover_raw_datasets finds all 6 expected CSVs."""
    discovered = discover_raw_datasets(synthetic_data_dir)
    assert len(discovered) == 6
    for name in RAW_DATASET_NAMES:
        assert name in discovered
        assert discovered[name].is_file()


def test_discover_raw_datasets_missing_file(synthetic_data_dir: Path):
    """Verify that missing files raise FileNotFoundError."""
    target = synthetic_data_dir / "ball_by_ball.csv"
    target.unlink()
    with pytest.raises(FileNotFoundError) as exc_info:
        discover_raw_datasets(synthetic_data_dir)
    assert "ball_by_ball.csv" in str(exc_info.value)


def test_generate_dataset_inventory(synthetic_data_dir: Path):
    """Verify that generate_dataset_inventory outputs accurate summary metrics."""
    paths = discover_raw_datasets(synthetic_data_dir)
    dfs = {name: pd.read_csv(p) for name, p in paths.items()}
    inventory = generate_dataset_inventory(dfs, paths)

    assert len(inventory) == 6
    assert "row_count" in inventory.columns
    assert "column_count" in inventory.columns
    assert "null_percentage" in inventory.columns
    assert inventory[inventory["dataset_name"] == "competitions.csv"]["row_count"].iloc[0] == 2


def test_key_validation_and_duplicate_detection():
    """Verify that validate_primary_and_composite_keys accurately detects duplicate and null keys."""
    synthetic_dfs = {
        "competitions.csv": pd.DataFrame({"comp_id": [1, 2]}),
        "teams.csv": pd.DataFrame({"comp_id": [1, 1], "team_id": [10, 20]}),
        "competition_team_player_mapping.csv": pd.DataFrame({
            "comp_id": [1, 1], "team_id": [10, 10], "player_id": [100, 101]
        }),
        "matches.csv": pd.DataFrame({"match_id": [1001, 1002]}),
        "playing_eleven.csv": pd.DataFrame({
            "match_id": [1001, 1001],
            "team_id": [10, 10],
            "player_id": [100, 100],  # Duplicate key intentionally introduced
        }),
        "ball_by_ball.csv": pd.DataFrame({
            "match_id": [1001, 1001],
            "innings": [1, 1],
            "innings_ball_num": [1, 2],
        }),
    }

    report = validate_primary_and_composite_keys(synthetic_dfs)
    assert len(report) == 6

    p11_report = report[report["dataset_name"] == "playing_eleven.csv"].iloc[0]
    assert p11_report["is_unique"] is False or p11_report["distinct_duplicates"] == 1
    assert p11_report["validity_status"] == "VIOLATION DETECTED"

    comps_report = report[report["dataset_name"] == "competitions.csv"].iloc[0]
    assert bool(comps_report["is_unique"]) is True
    assert comps_report["validity_status"] == "VALID"


def test_referential_integrity_audit():
    """Verify that analyze_relationships flags orphan keys properly."""
    synthetic_dfs = {
        "competitions.csv": pd.DataFrame({"comp_id": [1, 2]}),
        "matches.csv": pd.DataFrame({"comp_id": [1, 3], "match_id": [101, 102]}),  # comp_id 3 is orphan
        "teams.csv": pd.DataFrame({"comp_id": [1], "team_id": [10]}),
        "competition_team_player_mapping.csv": pd.DataFrame({
            "comp_id": [1], "team_id": [10], "player_id": [100]
        }),
        "playing_eleven.csv": pd.DataFrame({
            "match_id": [101], "team_id": [10], "player_id": [100]
        }),
        "ball_by_ball.csv": pd.DataFrame({
            "match_id": [101], "striker_id": [100], "bowler_id": [200]
        }),
    }

    rel_df, mermaid_md = analyze_relationships(synthetic_dfs)
    assert len(rel_df) >= 5
    assert "erDiagram" in mermaid_md

    comp_match_rel = rel_df[
        (rel_df["parent_dataset"] == "competitions.csv") & (rel_df["child_dataset"] == "matches.csv")
    ].iloc[0]
    assert comp_match_rel["unmatched_child_keys"] == 1
    assert comp_match_rel["referential_status"] == "ORPHAN KEYS DETECTED"


def test_data_availability_matrix():
    """Verify that generate_data_availability_matrix produces all expected dimension rows."""
    matrix = generate_data_availability_matrix({})
    assert len(matrix) >= 12
    assert "Requirement" in matrix.columns
    assert "Availability" in matrix.columns
    assert "AVAILABLE" in matrix["Availability"].values
    assert "DERIVABLE" in matrix["Availability"].values
