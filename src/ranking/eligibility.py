"""Player eligibility evaluation module for Phase 8.

Implements defensible, evidence-based eligibility criteria for:
- Batters under pressure
- Bowlers under pressure

Classifications:
- Eligible
- Provisionally Eligible
- Insufficient Evidence
- Data Quality Exclusion
"""

from __future__ import annotations

import logging
from typing import Dict, Tuple
import numpy as np
import pandas as pd

from src.ranking.ranking_config import RankingConfig

logger = logging.getLogger(__name__)


def evaluate_batting_eligibility(
    batting_df: pd.DataFrame,
    baseline_df: pd.DataFrame,
    registry_df: pd.DataFrame,
    config: RankingConfig,
) -> pd.DataFrame:
    """Evaluate batting eligibility across all candidates.

    Args:
        batting_df: Merged batting pressure dataset with balls, matches, innings.
        baseline_df: Batting overall baseline dataset.
        registry_df: Master player registry.
        config: Ranking configuration.

    Returns:
        DataFrame of batting eligibility records.
    """
    df = batting_df.copy()
    df["player_id"] = df["player_id"].astype(str)

    # Valid baselines set
    valid_base_ids = set(baseline_df["player_id"].astype(str).unique())
    registered_ids = set(registry_df["player_id"].astype(str).unique())

    records = []
    for _, row in df.iterrows():
        pid = str(row["player_id"])
        name = str(row.get("player_name", "Unknown"))
        balls = int(row.get("balls_faced", 0))
        matches = int(row.get("matches_count", 0))
        inns = int(row.get("innings_count", 0))
        has_base = pid in valid_base_ids
        is_registered = pid in registered_ids

        status = "Insufficient Evidence"
        reason = "Sample size below provisional threshold"

        if not is_registered:
            status = "Data Quality Exclusion"
            reason = "Player ID not found in master player registry"
        elif config.bat_require_baseline and not has_base:
            status = "Data Quality Exclusion"
            reason = "No historical batting baseline established from Phase 5"
        elif (
            balls >= config.bat_min_balls
            and matches >= config.bat_min_matches
            and inns >= config.bat_min_innings
        ):
            status = "Eligible"
            reason = (
                f"Meets full criteria: {balls} balls (>= {config.bat_min_balls}), "
                f"{matches} matches (>= {config.bat_min_matches}), {inns} innings (>= {config.bat_min_innings})"
            )
        elif (
            balls >= config.bat_prov_min_balls
            and matches >= config.bat_prov_min_matches
        ):
            status = "Provisionally Eligible"
            reason = (
                f"Provisional sample: {balls} balls in {matches} matches "
                f"(below full threshold {config.bat_min_balls} balls / {config.bat_min_matches} matches)"
            )
        else:
            status = "Insufficient Evidence"
            reason = f"Insufficient pressure exposure: {balls} balls (< {config.bat_prov_min_balls})"

        records.append({
            "player_id": pid,
            "player_name": name,
            "role": "batter",
            "balls_faced": balls,
            "matches_count": matches,
            "innings_count": inns,
            "has_baseline": has_base,
            "is_registered": is_registered,
            "eligibility_status": status,
            "is_eligible": status == "Eligible",
            "exclusion_reason": reason if status != "Eligible" else "None (Fully Eligible)",
        })

    res_df = pd.DataFrame(records)
    logger.info(
        "Batting eligibility evaluated: %d total -> %s",
        len(res_df),
        res_df["eligibility_status"].value_counts().to_dict(),
    )
    return res_df


def evaluate_bowling_eligibility(
    bowling_df: pd.DataFrame,
    baseline_df: pd.DataFrame,
    registry_df: pd.DataFrame,
    config: RankingConfig,
) -> pd.DataFrame:
    """Evaluate bowling eligibility across all candidates.

    Args:
        bowling_df: Merged bowling pressure dataset with legal balls, matches, innings.
        baseline_df: Bowling overall baseline dataset.
        registry_df: Master player registry.
        config: Ranking configuration.

    Returns:
        DataFrame of bowling eligibility records.
    """
    df = bowling_df.copy()
    df["player_id"] = df["player_id"].astype(str)

    valid_base_ids = set(baseline_df["player_id"].astype(str).unique())
    registered_ids = set(registry_df["player_id"].astype(str).unique())

    records = []
    for _, row in df.iterrows():
        pid = str(row["player_id"])
        name = str(row.get("player_name", "Unknown"))
        balls = int(row.get("legal_balls_bowled", 0))
        matches = int(row.get("matches_bowled", 0))
        inns = int(row.get("innings_bowled", 0))
        has_base = pid in valid_base_ids
        is_registered = pid in registered_ids

        status = "Insufficient Evidence"
        reason = "Sample size below provisional threshold"

        if not is_registered:
            status = "Data Quality Exclusion"
            reason = "Player ID not found in master player registry"
        elif config.bowl_require_baseline and not has_base:
            status = "Data Quality Exclusion"
            reason = "No historical bowling baseline established from Phase 5"
        elif (
            balls >= config.bowl_min_balls
            and matches >= config.bowl_min_matches
            and inns >= config.bowl_min_innings
        ):
            status = "Eligible"
            reason = (
                f"Meets full criteria: {balls} legal balls (>= {config.bowl_min_balls}), "
                f"{matches} matches (>= {config.bowl_min_matches}), {inns} innings (>= {config.bowl_min_innings})"
            )
        elif (
            balls >= config.bowl_prov_min_balls
            and matches >= config.bowl_prov_min_matches
        ):
            status = "Provisionally Eligible"
            reason = (
                f"Provisional sample: {balls} balls in {matches} matches "
                f"(below full threshold {config.bowl_min_balls} balls / {config.bowl_min_matches} matches)"
            )
        else:
            status = "Insufficient Evidence"
            reason = f"Insufficient pressure exposure: {balls} balls (< {config.bowl_prov_min_balls})"

        records.append({
            "player_id": pid,
            "player_name": name,
            "role": "bowler",
            "legal_balls_bowled": balls,
            "matches_bowled": matches,
            "innings_bowled": inns,
            "has_baseline": has_base,
            "is_registered": is_registered,
            "eligibility_status": status,
            "is_eligible": status == "Eligible",
            "exclusion_reason": reason if status != "Eligible" else "None (Fully Eligible)",
        })

    res_df = pd.DataFrame(records)
    logger.info(
        "Bowling eligibility evaluated: %d total -> %s",
        len(res_df),
        res_df["eligibility_status"].value_counts().to_dict(),
    )
    return res_df

