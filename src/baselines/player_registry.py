"""Player registry management module.

Maintains canonical player identities, squad registrations, tournament representation,
and participation volume across historical matches.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def build_player_registry(
    mapping_df: pd.DataFrame,
    playing_eleven_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    deliveries_df: pd.DataFrame,
) -> pd.DataFrame:
    """Construct master player registry combining registrations, team sheets, and delivery participation.

    Args:
        mapping_df: competition_team_player_mapping dataset.
        playing_eleven_df: cleaned playing_eleven dataset.
        matches_df: cleaned matches metadata dataset.
        deliveries_df: ball-by-ball delivery dataset.

    Returns:
        DataFrame representing player_registry.parquet conforming to Phase 5 specifications.
    """
    logger.info("Building master player registry across datasets...")

    # 1. Base Universe from master mapping: player_id, player_name, teams, comps
    mapping = mapping_df.copy()
    mapping["player_id"] = mapping["player_id"].astype(str)
    mapping["player_name"] = mapping["player_name"].fillna("Unknown").astype(str)

    # Group registrations by player_id
    player_names = mapping.groupby("player_id")["player_name"].first()
    player_teams = mapping.groupby("player_id")["team_name"].apply(lambda s: ";".join(sorted(set(s.dropna().astype(str)))))
    player_comps = mapping.groupby("player_id")["comp_name"].apply(lambda s: ";".join(sorted(set(s.dropna().astype(str)))))

    registry_base = pd.DataFrame({
        "player_id": player_names.index,
        "player_name": player_names.values,
        "registered_teams": player_teams.values,
        "competition_types": player_comps.values,
    }).set_index("player_id")

    # 2. Playing XI appearances & Dates
    pe = playing_eleven_df.copy()
    pe["player_id"] = pe["player_id"].astype(str)
    if "match_date" not in pe.columns and "match_date" in matches_df.columns:
        m = matches_df[["match_id", "match_date"]].drop_duplicates()
        pe_matches = pe.merge(m, on="match_id", how="left")
    else:
        pe_matches = pe

    if len(pe_matches) > 0 and "match_date" in pe_matches.columns:
        match_counts = pe_matches.groupby("player_id")["match_id"].nunique()
        first_dates = pe_matches.groupby("player_id")["match_date"].min()
        last_dates = pe_matches.groupby("player_id")["match_date"].max()
    else:
        match_counts = pd.Series(dtype=int)
        first_dates = pd.Series(dtype=str)
        last_dates = pd.Series(dtype=str)

    registry_base["matches_available"] = registry_base.index.map(match_counts).fillna(0).astype(int)
    registry_base["first_recorded_match"] = registry_base.index.map(first_dates)
    registry_base["last_recorded_match"] = registry_base.index.map(last_dates)

    # 3. Verified Batting and Bowling Innings from Deliveries
    deliv = deliveries_df.copy()
    deliv["striker_id"] = deliv["striker_id"].astype(str)
    deliv["bowler_id"] = deliv["bowler_id"].astype(str)

    # Batting innings: unique (match_id, innings) where player was striker
    bat_innings = deliv[["striker_id", "match_id", "innings"]].drop_duplicates().groupby("striker_id").size()
    # Bowling innings: unique (match_id, innings) where player was bowler
    bowl_innings = deliv[["bowler_id", "match_id", "innings"]].drop_duplicates().groupby("bowler_id").size()

    # Balls faced & legal balls bowled for quick activity check
    balls_faced = deliv[deliv["extras_type"] != "wide"].groupby("striker_id").size()
    legal_balls = deliv[deliv["is_legal_delivery"] == True].groupby("bowler_id").size()

    registry_base["batting_innings"] = registry_base.index.map(bat_innings).fillna(0).astype(int)
    registry_base["bowling_innings"] = registry_base.index.map(bowl_innings).fillna(0).astype(int)
    registry_base["total_balls_faced"] = registry_base.index.map(balls_faced).fillna(0).astype(int)
    registry_base["total_legal_balls_bowled"] = registry_base.index.map(legal_balls).fillna(0).astype(int)

    # Participation flags
    registry_base["is_active_batter"] = registry_base["total_balls_faced"] > 0
    registry_base["is_active_bowler"] = registry_base["total_legal_balls_bowled"] > 0
    registry_base["has_participated"] = registry_base["is_active_batter"] | registry_base["is_active_bowler"] | (registry_base["matches_available"] > 0)

    registry = registry_base.reset_index()

    logger.info(
        "Master registry built with %d players (%d active batters, %d active bowlers, %d participated on field).",
        len(registry),
        registry["is_active_batter"].sum(),
        registry["is_active_bowler"].sum(),
        registry["has_participated"].sum(),
    )

    return registry
