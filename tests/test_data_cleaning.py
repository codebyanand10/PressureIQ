"""Unit and integration tests for data cleaning and preprocessing (Phase 2)."""

from __future__ import annotations

import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.preprocessing import (
    clean_ball_by_ball,
    clean_competition_team_player_mapping,
    clean_competitions,
    clean_matches,
    clean_playing_eleven,
    clean_teams,
    compute_file_hash,
    read_parquet,
    save_parquet,
    verify_raw_files_integrity,
)


@pytest.fixture
def sample_competitions_df() -> pd.DataFrame:
    return pd.DataFrame({
        "comp_id": [1358, 1715],
        "comp_name": [" IPL 2022 ", "IPL 2023"],
        "match_format": [" T20 ", "T20"],
        "season": [" 2022 ", "2023"],
    })


@pytest.fixture
def sample_playing_eleven_with_dupes() -> pd.DataFrame:
    return pd.DataFrame({
        "match_id": [13613, 13613, 13613],
        "team_id": [20, 20, 20],
        "player_id": [223, 223, 250],
        "batting_order": [5.0, 6.0, 2.0],
        "is_played": [True, True, True],
        "is_captain": ["False", "False", "False"],
        "is_wk": ["False", "False", "False"],
        "is_impact": [0, 0, 0],
        "is_impact_off": [0, 0, 0],
    })


@pytest.fixture
def sample_bbb_for_dupes() -> pd.DataFrame:
    return pd.DataFrame({
        "match_id": [13613, 13613],
        "striker_id": [223, 250],
        "batting_order": [5, 2],
    })


def test_clean_competitions(sample_competitions_df: pd.DataFrame):
    cleaned, meta = clean_competitions(sample_competitions_df)
    assert len(cleaned) == 2
    assert cleaned["comp_name"].tolist() == ["IPL 2022", "IPL 2023"]
    assert cleaned["match_format"].tolist() == ["T20", "T20"]
    assert cleaned["season"].tolist() == ["2022", "2023"]
    assert meta["is_unique"] is True


def test_clean_playing_eleven_deduplication(
    sample_playing_eleven_with_dupes: pd.DataFrame,
    sample_bbb_for_dupes: pd.DataFrame,
):
    cleaned, audit, meta = clean_playing_eleven(
        sample_playing_eleven_with_dupes, sample_bbb_for_dupes
    )
    # Player 223 had 2 duplicate rows (order 5 and 6); order 5 matches bbb so order 6 is removed
    assert len(cleaned) == 2
    assert meta["is_unique"] is True
    assert len(audit) == 1
    assert audit.iloc[0]["player_id"] == 223
    assert audit.iloc[0]["removed_batting_order"] == 6.0
    p223_row = cleaned[cleaned["player_id"] == 223]
    assert p223_row.iloc[0]["batting_order"] == 5.0


def test_clean_ball_by_ball_speed_radar_and_typo():
    raw_bbb = pd.DataFrame({
        "match_id": [1, 1],
        "innings": [1, 1],
        "overid": [1, 1],
        "over_ball_num": [1, 2],
        "innings_ball_num": [1, 2],
        "batting_team_id": [10, 10],
        "bowling_team_id": [20, 20],
        "striker_id": [101, 101],
        "striker_name": ["Batter A", "Batter A"],
        "non_striker_id": [102, 102],
        "non_striker_name": ["Batter B", "Batter B"],
        "bowler_id": [201, 201],
        "bowler_name": ["Bowler A", "Bowler A"],
        "batting_type": ["RHB", "RHB"],
        "bowling_type": ["Fast", "Fast"],
        "batting_order": [1, 1],
        "runs": [0, 4],
        "is_four": [False, True],
        "is_six": [False, False],
        "is_wicket": [True, False],
        "dismissal_type_id": [1.0, np.nan],
        "dismissal_type": ["Obstracting the field", np.nan],
        "dismissed_player_id": [101.0, 101.0],  # row 2 has anomalous dismissed_player_id on non-wicket
        "extras_type": [np.nan, np.nan],
        "extras1_runs": [0, 0],
        "extras_2_runs": [0, 0],
        "pace_or_spin": ["Pace", "Pace"],
        "bowl_speed": [0.0, 135.5],
        "stroke": ["Drive", "Cut"],
        "delivery_style": ["Inswing", "Outswing"],
        "over_or_around": ["Over", "Over"],
        "on_or_off": ["Off", "Off"],
        "delivery_ist_time": ["2022-01-01 00:00:00 UTC", "2022-01-01 00:01:00 UTC"],
    })

    cleaned, invalid_report, meta = clean_ball_by_ball(raw_bbb)
    assert len(cleaned) == 2
    # Typo corrected
    assert cleaned.loc[0, "dismissal_type"] == "Obstructing the field"
    # Speed radar 0.0 converted to NaN
    assert np.isnan(cleaned.loc[0, "bowl_speed"])
    assert cleaned.loc[1, "bowl_speed"] == 135.5
    # Anomalous dismissed_player_id on non-wicket neutralized
    assert pd.isna(cleaned.loc[1, "dismissed_player_id"])
    assert len(invalid_report) == 1
    # Traceability index
    assert "delivery_order_idx" in cleaned.columns


def test_parquet_io_roundtrip():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "value": ["alpha", "beta", "gamma"],
        "score": [10.5, 20.0, 30.2],
    })
    with tempfile.TemporaryDirectory() as tmp_dir:
        pq_path = Path(tmp_dir) / "test.parquet"
        save_parquet(df, pq_path)
        assert pq_path.is_file()

        df_loaded = read_parquet(pq_path)
        assert len(df_loaded) == 3
        assert df_loaded["value"].tolist() == ["alpha", "beta", "gamma"]


def test_file_hash_consistency():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"PressureIQ verification payload")
        temp_path = Path(f.name)

    try:
        h1 = compute_file_hash(temp_path)
        h2 = compute_file_hash(temp_path)
        assert h1 == h2
        assert len(h1) == 64
    finally:
        if temp_path.is_file():
            temp_path.unlink()

