"""Eligibility threshold sensitivity analysis module for Phase 9.

Tests how changing minimum balls, matches, and innings thresholds
alters candidate cohort size, exclusions, and Top 10 membership stability.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple
import pandas as pd
from scipy.stats import spearmanr

from src.validation.validation_config import ValidationConfig

logger = logging.getLogger(__name__)


def evaluate_eligibility_sensitivity(
    batting_el_df: pd.DataFrame,
    bowling_el_df: pd.DataFrame,
    ranked_batters: pd.DataFrame,
    ranked_bowlers: pd.DataFrame,
    config: ValidationConfig,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate eligibility sensitivity across lower, primary, and higher thresholds.

    Returns:
        Tuple of (eligibility_summary_df, threshold_movement_df).
    """
    logger.info("Evaluating eligibility threshold sensitivity...")

    ref_bat_top10 = set(ranked_batters.head(config.top_n)["player_id"])
    ref_bowl_top10 = set(ranked_bowlers.head(config.top_n)["player_id"])

    summary_rows = []
    movement_rows = []

    for scenario_name, sc in config.ELIGIBILITY_SCENARIOS.items():
        # Batting Filter
        bat_el = batting_el_df[
            (batting_el_df["balls_faced"] >= sc["bat_min_balls"])
            & (batting_el_df["matches_count"] >= sc["bat_min_matches"])
            & (batting_el_df["innings_count"] >= sc["bat_min_inns"])
            & (batting_el_df["has_baseline"] == True)
            & (batting_el_df.get("is_registered", pd.Series(True, index=batting_el_df.index)) == True)
        ]
        n_bat_eligible = len(bat_el)
        n_bat_excluded = len(batting_el_df) - n_bat_eligible

        # Batting Top 10 under this threshold
        # Filter ranked_batters by eligible pids and take top 10
        bat_sub = ranked_batters[ranked_batters["player_id"].isin(bat_el["player_id"])].reset_index(drop=True)
        bat_top10_sc = set(bat_sub.head(config.top_n)["player_id"])
        bat_overlap = len(ref_bat_top10.intersection(bat_top10_sc))
        bat_entering = list(bat_top10_sc - ref_bat_top10)
        bat_leaving = list(ref_bat_top10 - bat_top10_sc)

        # Bowling Filter
        bowl_el = bowling_el_df[
            (bowling_el_df["legal_balls_bowled"] >= sc["bowl_min_balls"])
            & (bowling_el_df["matches_bowled"] >= sc["bowl_min_matches"])
            & (bowling_el_df["innings_bowled"] >= sc["bowl_min_inns"])
            & (bowling_el_df["has_baseline"] == True)
            & (bowling_el_df.get("is_registered", pd.Series(True, index=bowling_el_df.index)) == True)
        ]
        n_bowl_eligible = len(bowl_el)
        n_bowl_excluded = len(bowling_el_df) - n_bowl_eligible

        bowl_sub = ranked_bowlers[ranked_bowlers["player_id"].isin(bowl_el["player_id"])].reset_index(drop=True)
        bowl_top10_sc = set(bowl_sub.head(config.top_n)["player_id"])
        bowl_overlap = len(ref_bowl_top10.intersection(bowl_top10_sc))
        bowl_entering = list(bowl_top10_sc - ref_bowl_top10)
        bowl_leaving = list(ref_bowl_top10 - bowl_top10_sc)

        summary_rows.append({
            "scenario": scenario_name,
            "bat_min_balls": sc["bat_min_balls"],
            "bat_min_matches": sc["bat_min_matches"],
            "bat_eligible_count": n_bat_eligible,
            "bat_excluded_count": n_bat_excluded,
            "bat_top10_overlap": bat_overlap,
            "bat_players_entering_count": len(bat_entering),
            "bat_players_leaving_count": len(bat_leaving),
            "bowl_min_balls": sc["bowl_min_balls"],
            "bowl_min_matches": sc["bowl_min_matches"],
            "bowl_eligible_count": n_bowl_eligible,
            "bowl_excluded_count": n_bowl_excluded,
            "bowl_top10_overlap": bowl_overlap,
            "bowl_players_entering_count": len(bowl_entering),
            "bowl_players_leaving_count": len(bowl_leaving),
        })

        # Track movements
        for pid in bat_leaving:
            p_name = ranked_batters[ranked_batters["player_id"] == pid]["player_name"].iloc[0]
            movement_rows.append({
                "scenario": scenario_name, "role": "batter", "action": "LEAVING_TOP_10",
                "player_id": pid, "player_name": p_name,
                "reason": f"Fails tighter threshold ({sc['bat_min_balls']} balls, {sc['bat_min_matches']} matches)",
            })
        for pid in bat_entering:
            p_name = bat_sub[bat_sub["player_id"] == pid]["player_name"].iloc[0]
            movement_rows.append({
                "scenario": scenario_name, "role": "batter", "action": "ENTERING_TOP_10",
                "player_id": pid, "player_name": p_name,
                "reason": "Promoted due to cohort shift",
            })
        for pid in bowl_leaving:
            p_name = ranked_bowlers[ranked_bowlers["player_id"] == pid]["player_name"].iloc[0]
            movement_rows.append({
                "scenario": scenario_name, "role": "bowler", "action": "LEAVING_TOP_10",
                "player_id": pid, "player_name": p_name,
                "reason": f"Fails tighter threshold ({sc['bowl_min_balls']} legal balls)",
            })
        for pid in bowl_entering:
            p_name = bowl_sub[bowl_sub["player_id"] == pid]["player_name"].iloc[0]
            movement_rows.append({
                "scenario": scenario_name, "role": "bowler", "action": "ENTERING_TOP_10",
                "player_id": pid, "player_name": p_name,
                "reason": "Promoted due to cohort shift",
            })

    df_summary = pd.DataFrame(summary_rows)
    df_movement = pd.DataFrame(movement_rows) if movement_rows else pd.DataFrame(columns=["scenario", "role", "action", "player_id", "player_name", "reason"])

    logger.info("Eligibility threshold sensitivity complete.")
    return df_summary, df_movement
