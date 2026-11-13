"""Tactical role and situation fairness validation module for Phase 9.

Investigates whether batting positions (openers, middle order, finishers)
or bowling roles (powerplay, middle, death, pace vs spin) receive unfair advantages
or systemic penalties in the Phase 8 ranking architecture.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple
import duckdb
import numpy as np
import pandas as pd

from src.config import config
from src.validation.validation_config import ValidationConfig

logger = logging.getLogger(__name__)


def evaluate_role_fairness(
    ranked_batters: pd.DataFrame,
    ranked_bowlers: pd.DataFrame,
    config_val: ValidationConfig,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Evaluate role and situational fairness across batting and bowling cohorts.

    Returns:
        Tuple of (batting_role_fairness_df, bowling_role_fairness_df, role_summary_metrics).
    """
    logger.info("Evaluating tactical role and situation fairness...")
    proc = config.data_processed_dir
    pressure_pq = proc / "pressure" / "pressure_scores.parquet"
    con = duckdb.connect()

    # 1. Batting Position Classification (from delivery-level batting_order)
    bat_order_df = con.execute(f"""
        SELECT 
            CAST(striker_id AS VARCHAR) AS player_id,
            AVG(batting_order) AS avg_batting_pos,
            SUM(CASE WHEN innings_phase_before = 'POWERPLAY' THEN 1 ELSE 0 END) AS pp_balls,
            SUM(CASE WHEN innings_phase_before = 'MIDDLE_OVERS' THEN 1 ELSE 0 END) AS mid_balls,
            SUM(CASE WHEN innings_phase_before = 'DEATH_OVERS' THEN 1 ELSE 0 END) AS death_balls,
            COUNT(*) AS total_balls
        FROM '{pressure_pq}'
        WHERE batting_pressure_level IN ('High', 'Extreme')
        GROUP BY striker_id
    """).df()

    bat_merged = ranked_batters.merge(bat_order_df, on="player_id", how="left")
    # Categorize role: Top Order (1-3), Middle Order (4-5), Lower Order / Finisher (6+)
    bat_merged["batting_role"] = np.where(
        bat_merged["avg_batting_pos"] <= 3.2, "Top Order (1-3)",
        np.where(bat_merged["avg_batting_pos"] <= 5.5, "Middle Order (4-5)", "Lower Order / Finisher (6+)")
    )

    # Batting role summary
    bat_role_summary = bat_merged.groupby("batting_role").agg(
        player_count=("player_id", "count"),
        top10_count=("rank", lambda s: (s <= config_val.top_n).sum()),
        mean_fbpr=("final_fbpr", "mean"),
        mean_balls_faced=("balls_faced", "mean"),
        mean_strike_rate=("strike_rate", "mean"),
    ).reset_index()
    bat_role_summary["top10_share"] = (bat_role_summary["top10_count"] / config_val.top_n).round(3)
    bat_role_summary["cohort_share"] = (bat_role_summary["player_count"] / len(bat_merged)).round(3)

    # 2. Bowling Role & Bowling Style Classification
    # Bowling role is already in ranked_bowlers from bowling_roles (Phase 7)!
    # primary_bowling_style is in ranked_bowlers (Pace vs Spin)!
    bowl_df = ranked_bowlers.copy()
    if "bowling_role" not in bowl_df.columns:
        bowl_df["bowling_role"] = "Multi-Phase Bowler"
    if "primary_bowling_style" not in bowl_df.columns:
        bowl_df["primary_bowling_style"] = "Pace"

    # Normalize style to Pace vs Spin
    bowl_df["style_category"] = np.where(
        bowl_df["primary_bowling_style"].str.lower().str.contains("spin|orthodox|break"), "Spin", "Pace"
    )

    bowl_role_summary = bowl_df.groupby("bowling_role").agg(
        player_count=("player_id", "count"),
        top10_count=("rank", lambda s: (s <= config_val.top_n).sum()),
        mean_fbor=("final_fbor", "mean"),
        mean_legal_balls=("legal_balls_bowled", "mean"),
        mean_economy=("economy_rate", "mean"),
    ).reset_index()
    bowl_role_summary["top10_share"] = (bowl_role_summary["top10_count"] / config_val.top_n).round(3)
    bowl_role_summary["cohort_share"] = (bowl_role_summary["player_count"] / len(bowl_df)).round(3)

    # Pace vs Spin breakdown
    style_summary = bowl_df.groupby("style_category").agg(
        player_count=("player_id", "count"),
        top10_count=("rank", lambda s: (s <= config_val.top_n).sum()),
        mean_fbor=("final_fbor", "mean"),
    ).reset_index()

    summary_metrics = {
        "batting_roles_represented_in_top10": int((bat_role_summary["top10_count"] > 0).sum()),
        "bowling_roles_represented_in_top10": int((bowl_role_summary["top10_count"] > 0).sum()),
        "pace_bowlers_in_top10": int(style_summary[style_summary["style_category"] == "Pace"]["top10_count"].iloc[0]) if "Pace" in style_summary["style_category"].values else 0,
        "spin_bowlers_in_top10": int(style_summary[style_summary["style_category"] == "Spin"]["top10_count"].iloc[0]) if "Spin" in style_summary["style_category"].values else 0,
    }

    logger.info("Role fairness evaluation complete.")
    return bat_role_summary, bowl_role_summary, summary_metrics

