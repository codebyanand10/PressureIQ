"""Scoring weight sensitivity analysis module for Phase 9.

Tests how player ratings, full ranking orders, and Top 10 memberships shift
under alternative defensible weighting scenarios (balanced, absolute-focused,
baseline-focused, consistency-focused, reliability-focused, pressure-difficulty-focused).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from src.validation.ranking_stability import calculate_ranking_similarity_metrics
from src.validation.validation_config import ValidationConfig

logger = logging.getLogger(__name__)


def run_weight_sensitivity_analysis(
    ranked_batters: pd.DataFrame,
    ranked_bowlers: pd.DataFrame,
    config: ValidationConfig,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Execute multi-scenario weight sensitivity analysis.

    Returns:
        Tuple of (batting_sensitivity_df, bowling_sensitivity_df, scenarios_summary_df).
    """
    logger.info("Executing scoring weight sensitivity analysis across %d scenarios...", len(config.SENSITIVITY_SCENARIOS))

    bat_sens_records = []
    bowl_sens_records = []
    summary_records = []

    ref_bat_ranks = ranked_batters.set_index("player_id")["rank"]
    ref_bowl_ranks = ranked_bowlers.set_index("player_id")["rank"]

    for scenario_name, weights in config.SENSITIVITY_SCENARIOS.items():
        w_res = weights["quality_and_resilience"]
        w_abs = weights["absolute_performance"]
        w_con = weights["consistency"]
        w_ctx = weights["pressure_context"]

        # 1. Batting Recalculation
        bat_df = ranked_batters.copy()
        raw_bat = (
            w_res * bat_df["score_batting_resilience"]
            + w_abs * bat_df["score_batting_absolute"]
            + w_con * bat_df["score_batting_consistency"]
            + w_ctx * bat_df["score_batting_context"]
        )
        # Apply Empirical Bayes shrinkage
        prior_mean_bat = float(raw_bat.median())
        n0_bat = 25.0 if scenario_name != "reliability_focused" else 40.0
        balls = bat_df["balls_faced"].astype(float)
        lam_bat = (balls / (balls + n0_bat)).clip(0.0, 1.0)
        shrunk_bat = (lam_bat * raw_bat + (1.0 - lam_bat) * prior_mean_bat).clip(0.0, 100.0).round(2)

        bat_df[f"rating_{scenario_name}"] = shrunk_bat
        bat_df[f"rank_{scenario_name}"] = bat_df[f"rating_{scenario_name}"].rank(ascending=False, method="min").astype(int)

        comp_bat_ranks = bat_df.set_index("player_id")[f"rank_{scenario_name}"]
        bat_metrics = calculate_ranking_similarity_metrics(ref_bat_ranks, comp_bat_ranks, top_n=config.top_n)

        # 2. Bowling Recalculation
        bowl_df = ranked_bowlers.copy()
        raw_bowl = (
            w_res * bowl_df["score_bowling_resilience"]
            + w_abs * bowl_df["score_bowling_absolute"]
            + w_con * bowl_df["score_bowling_consistency"]
            + w_ctx * bowl_df["score_bowling_context"]
        )
        prior_mean_bowl = float(raw_bowl.median())
        n0_bowl = 30.0 if scenario_name != "reliability_focused" else 50.0
        lb = bowl_df["legal_balls_bowled"].astype(float)
        lam_bowl = (lb / (lb + n0_bowl)).clip(0.0, 1.0)
        shrunk_bowl = (lam_bowl * raw_bowl + (1.0 - lam_bowl) * prior_mean_bowl).clip(0.0, 100.0).round(2)

        bowl_df[f"rating_{scenario_name}"] = shrunk_bowl
        bowl_df[f"rank_{scenario_name}"] = bowl_df[f"rating_{scenario_name}"].rank(ascending=False, method="min").astype(int)

        comp_bowl_ranks = bowl_df.set_index("player_id")[f"rank_{scenario_name}"]
        bowl_metrics = calculate_ranking_similarity_metrics(ref_bowl_ranks, comp_bowl_ranks, top_n=config.top_n)

        # Record scenario summary
        summary_records.append({
            "scenario": scenario_name,
            "weights_resilience": w_res,
            "weights_absolute": w_abs,
            "weights_consistency": w_con,
            "weights_context": w_ctx,
            "batting_spearman": bat_metrics["spearman"],
            "batting_kendall": bat_metrics["kendall"],
            "batting_top10_overlap": bat_metrics["top_n_overlap"],
            "batting_jaccard": bat_metrics["jaccard"],
            "bowling_spearman": bowl_metrics["spearman"],
            "bowling_kendall": bowl_metrics["kendall"],
            "bowling_top10_overlap": bowl_metrics["top_n_overlap"],
            "bowling_jaccard": bowl_metrics["jaccard"],
        })

        # Record player level scenario details
        for _, r in bat_df.iterrows():
            bat_sens_records.append({
                "scenario": scenario_name,
                "player_id": r["player_id"],
                "player_name": r["player_name"],
                "official_rank": int(r["rank"]),
                "official_fbpr": float(r["final_fbpr"]),
                "scenario_fbpr": float(r[f"rating_{scenario_name}"]),
                "scenario_rank": int(r[f"rank_{scenario_name}"]),
                "rank_delta": int(r[f"rank_{scenario_name}"]) - int(r["rank"]),
                "in_top_10": bool(r[f"rank_{scenario_name}"] <= config.top_n),
            })

        for _, r in bowl_df.iterrows():
            bowl_sens_records.append({
                "scenario": scenario_name,
                "player_id": r["player_id"],
                "player_name": r["player_name"],
                "official_rank": int(r["rank"]),
                "official_fbor": float(r["final_fbor"]),
                "scenario_fbor": float(r[f"rating_{scenario_name}"]),
                "scenario_rank": int(r[f"rank_{scenario_name}"]),
                "rank_delta": int(r[f"rank_{scenario_name}"]) - int(r["rank"]),
                "in_top_10": bool(r[f"rank_{scenario_name}"] <= config.top_n),
            })

    df_bat_sens = pd.DataFrame(bat_sens_records)
    df_bowl_sens = pd.DataFrame(bowl_sens_records)
    df_summary = pd.DataFrame(summary_records)

    logger.info("Weight sensitivity analysis complete.")
    return df_bat_sens, df_bowl_sens, df_summary

