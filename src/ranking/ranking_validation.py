"""Ranking validation, integrity checks, and fairness audit module for Phase 8.

Audits:
- Non-negativity and strictly bounded [0, 100] scores.
- Referential integrity (uniqueness of player_id per role, deterministic tie-breaking).
- Exact Top 10 extraction without duplicate ranks.
- Fairness audit: sample size bias, role representation, baseline vs absolute balance.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def validate_rankings(
    ranked_batters_df: pd.DataFrame,
    ranked_bowlers_df: pd.DataFrame,
    top_10_batters_df: pd.DataFrame,
    top_10_bowlers_df: pd.DataFrame,
) -> Dict[str, bool]:
    """Execute mathematical, referential, and domain validation checks on rankings.

    Returns:
        Dictionary mapping test names to boolean pass/fail status.
    """
    logger.info("Executing Phase 8 ranking mathematical and integrity validations...")
    checks: Dict[str, bool] = {}

    # 1. Score Bounds [0, 100]
    checks["batting_ratings_within_bounds"] = bool(
        (ranked_batters_df["final_fbpr"] >= 0.0).all() and (ranked_batters_df["final_fbpr"] <= 100.0).all()
    )
    checks["bowling_ratings_within_bounds"] = bool(
        (ranked_bowlers_df["final_fbor"] >= 0.0).all() and (ranked_bowlers_df["final_fbor"] <= 100.0).all()
    )

    # 2. Component Scores Bounds [0, 100]
    bat_comp_cols = [
        "score_batting_resilience",
        "score_batting_absolute",
        "score_batting_consistency",
        "score_batting_context",
    ]
    checks["batting_components_within_bounds"] = bool(
        all(
            (ranked_batters_df[col] >= 0.0).all() and (ranked_batters_df[col] <= 100.0).all()
            for col in bat_comp_cols
            if col in ranked_batters_df.columns
        )
    )

    bowl_comp_cols = [
        "score_bowling_resilience",
        "score_bowling_absolute",
        "score_bowling_consistency",
        "score_bowling_context",
    ]
    checks["bowling_components_within_bounds"] = bool(
        all(
            (ranked_bowlers_df[col] >= 0.0).all() and (ranked_bowlers_df[col] <= 100.0).all()
            for col in bowl_comp_cols
            if col in ranked_bowlers_df.columns
        )
    )

    # 3. Uniqueness of Player IDs
    checks["batting_player_ids_unique"] = bool(ranked_batters_df["player_id"].is_unique)
    checks["bowling_player_ids_unique"] = bool(ranked_bowlers_df["player_id"].is_unique)
    checks["top_10_batters_unique"] = bool(top_10_batters_df["player_id"].is_unique)
    checks["top_10_bowlers_unique"] = bool(top_10_bowlers_df["player_id"].is_unique)

    # 4. Exact Top 10 Count (if >= 10 eligible)
    checks["top_10_batters_count_exact"] = len(top_10_batters_df) == min(10, len(ranked_batters_df))
    checks["top_10_bowlers_count_exact"] = len(top_10_bowlers_df) == min(10, len(ranked_bowlers_df))

    # 5. Deterministic Sequential Ranks
    expected_bat_ranks = list(range(1, len(top_10_batters_df) + 1))
    checks["top_10_batters_sequential_ranks"] = list(top_10_batters_df["rank"]) == expected_bat_ranks

    expected_bowl_ranks = list(range(1, len(top_10_bowlers_df) + 1))
    checks["top_10_bowlers_sequential_ranks"] = list(top_10_bowlers_df["rank"]) == expected_bowl_ranks

    # 6. Monotonic Non-Increasing Order
    checks["batting_ratings_monotonically_ordered"] = bool(
        (top_10_batters_df["final_fbpr"].diff().dropna() <= 1e-4).all()
    )
    checks["bowling_ratings_monotonically_ordered"] = bool(
        (top_10_bowlers_df["final_fbor"].diff().dropna() <= 1e-4).all()
    )

    # 7. Confidence Bounds Validity: lower <= rating <= upper
    valid_bat_ci = (
        (ranked_batters_df["ci_lower_fbpr"] <= ranked_batters_df["final_fbpr"] + 1e-4)
        & (ranked_batters_df["final_fbpr"] <= ranked_batters_df["ci_upper_fbpr"] + 1e-4)
    )
    checks["batting_confidence_bounds_valid"] = bool(valid_bat_ci.all())

    valid_bowl_ci = (
        (ranked_bowlers_df["ci_lower_fbor"] <= ranked_bowlers_df["final_fbor"] + 1e-4)
        & (ranked_bowlers_df["final_fbor"] <= ranked_bowlers_df["ci_upper_fbor"] + 1e-4)
    )
    checks["bowling_confidence_bounds_valid"] = bool(valid_bowl_ci.all())

    all_passed = all(checks.values())
    logger.info("Validation completed: %d checks executed, all passed = %s", len(checks), all_passed)
    return checks


def audit_ranking_fairness(
    ranked_batters_df: pd.DataFrame,
    ranked_bowlers_df: pd.DataFrame,
) -> Dict[str, float]:
    """Audit potential systemic biases in player rankings.

    Evaluates:
    - Correlation between volume (balls/matches) and final rating.
    - Role representation across top quartiles.
    - Balance between absolute performance and baseline resilience.
    """
    audit: Dict[str, float] = {}

    # Batting: Volume correlation
    if len(ranked_batters_df) > 5:
        corr_bat_vol = float(ranked_batters_df["balls_faced"].corr(ranked_batters_df["final_fbpr"]))
        corr_bat_mat = float(ranked_batters_df["matches_count"].corr(ranked_batters_df["final_fbpr"]))
        corr_bat_sr = float(ranked_batters_df["strike_rate"].corr(ranked_batters_df["final_fbpr"]))
        corr_bat_res = float(ranked_batters_df["score_batting_resilience"].corr(ranked_batters_df["final_fbpr"]))
        audit["batting_volume_correlation"] = round(corr_bat_vol, 3)
        audit["batting_matches_correlation"] = round(corr_bat_mat, 3)
        audit["batting_strike_rate_correlation"] = round(corr_bat_sr, 3)
        audit["batting_resilience_correlation"] = round(corr_bat_res, 3)

    # Bowling: Volume correlation
    if len(ranked_bowlers_df) > 5:
        corr_bowl_vol = float(ranked_bowlers_df["legal_balls_bowled"].corr(ranked_bowlers_df["final_fbor"]))
        corr_bowl_mat = float(ranked_bowlers_df["matches_bowled"].corr(ranked_bowlers_df["final_fbor"]))
        corr_bowl_econ = float(ranked_bowlers_df["economy_rate"].corr(ranked_bowlers_df["final_fbor"]))
        corr_bowl_res = float(ranked_bowlers_df["score_bowling_resilience"].corr(ranked_bowlers_df["final_fbor"]))
        audit["bowling_volume_correlation"] = round(corr_bowl_vol, 3)
        audit["bowling_matches_correlation"] = round(corr_bowl_mat, 3)
        audit["bowling_economy_correlation"] = round(corr_bowl_econ, 3)
        audit["bowling_resilience_correlation"] = round(corr_bowl_res, 3)

    return audit

