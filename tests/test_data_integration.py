"""Unit and integration tests for dataset integration (Phase 2)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.data_integration import (
    build_integrated_ball_by_ball,
    build_match_metadata,
    build_match_participation_metadata,
    build_player_registration_metadata,
    build_team_metadata,
    classify_competitions,
)


@pytest.fixture
def sample_comps_classified() -> pd.DataFrame:
    raw_comps = pd.DataFrame({
        "comp_id": [1358, 2670, 1331],
        "comp_name": [
            "IPL 2022",
            "Mens T20 Emerging Teams Asia Cup 2024",
            "England in West Indies T20I Series 2022",
        ],
        "match_format": ["T20", "T20", "T20I"],
        "season": ["2022", "2024", "2022"],
    })
    return classify_competitions(raw_comps)


@pytest.fixture
def sample_matches(sample_comps_classified: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "match_id": [101, 102],
        "comp_id": [1358, 1331],
        "match_number": [1, 2],
        "match_date": ["2022-03-26", "2022-01-22"],
        "stage": ["League", "League"],
        "venue_id": [1, 2],
        "venue_country": ["India", "West Indies"],
        "home_team_id": [10, 20],
        "away_team_id": [11, 21],
        "result": ["Team A won", "Team B won"],
        "win_team_id": [10, 21],
        "knock_out": [0, 0],
    })


@pytest.fixture
def sample_teams() -> pd.DataFrame:
    return pd.DataFrame({
        "comp_id": [1358, 1358, 1331],
        "team_id": [10, 11, 20],
        "team_name": ["Team 10", "Team 11", "Team 20"],
    })


def test_classify_competitions(sample_comps_classified: pd.DataFrame):
    cats = sample_comps_classified.set_index("comp_id")["competition_category"].to_dict()
    assert cats[1358] == "IPL"
    assert cats[2670] == "Other T20 leagues"
    assert cats[1331] == "T20I"


def test_build_match_metadata_cardinality(sample_matches: pd.DataFrame, sample_comps_classified: pd.DataFrame):
    integrated = build_match_metadata(sample_matches, sample_comps_classified)
    assert len(integrated) == len(sample_matches)
    assert "competition_category" in integrated.columns
    assert "comp_name" in integrated.columns


def test_build_team_metadata_cardinality(sample_teams: pd.DataFrame, sample_comps_classified: pd.DataFrame):
    integrated = build_team_metadata(sample_teams, sample_comps_classified)
    assert len(integrated) == len(sample_teams)
    assert "competition_category" in integrated.columns


def test_build_integrated_ball_by_ball_no_fanout(
    sample_matches: pd.DataFrame,
    sample_comps_classified: pd.DataFrame,
):
    deliveries = pd.DataFrame({
        "delivery_order_idx": [0, 1, 2],
        "match_id": [101, 101, 102],
        "innings": [1, 1, 1],
        "overid": [1, 1, 1],
        "over_ball_num": [1, 2, 1],
        "innings_ball_num": [1, 2, 1],
        "runs": [1, 0, 4],
    })

    integrated = build_integrated_ball_by_ball(deliveries, sample_matches, sample_comps_classified)
    # Strictly preserves delivery row count
    assert len(integrated) == len(deliveries)
    assert integrated["delivery_order_idx"].tolist() == [0, 1, 2]
    assert "competition_category" in integrated.columns
    assert "venue_country" in integrated.columns

