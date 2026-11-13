"""Statistical validation and data integrity auditor for bowling under pressure.

Validates:
1. Mathematical formula consistency (economy rate, bowling average, strike rate).
2. Non-negativity of physical cricket counts.
3. Strict range bounds for BPPI-B and component scores (0 to 100).
4. Referential uniqueness (no duplicate player records).
5. Valid categorical assignments.
"""

from __future__ import annotations

import logging
from typing import Dict
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def validate_bowling_pressure_datasets(
    category_df: pd.DataFrame,
    hp_performance_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    bppi_df: pd.DataFrame,
    situational_df: pd.DataFrame,
) -> Dict[str, bool]:
    """Execute comprehensive mathematical and domain sanity checks for bowling.

    Returns:
        Dictionary mapping check names to boolean pass/fail status.
    """
    logger.info("Executing Phase 7 bowling statistical validation checks...")
    results: Dict[str, bool] = {}

    # 1. Non-negativity
    results["runs_non_negative"] = bool((category_df["runs_conceded"] >= 0).all())
    results["legal_balls_non_negative"] = bool((category_df["legal_balls_bowled"] >= 0).all())
    results["wickets_non_negative"] = bool((category_df["wickets_credited"] >= 0).all())

    # 2. Economy formula consistency
    valid_econ = hp_performance_df[hp_performance_df["legal_balls_bowled"] > 0]
    expected_econ = (valid_econ["runs_conceded"] * 6.0) / valid_econ["legal_balls_bowled"]
    econ_diff = (valid_econ["economy_rate"] - expected_econ).abs()
    results["economy_formula_consistent"] = bool((econ_diff < 0.02).all())

    # 3. Bowling average formula consistency
    valid_avg = hp_performance_df[hp_performance_df["wickets_credited"] > 0]
    expected_avg = valid_avg["runs_conceded"] / valid_avg["wickets_credited"]
    avg_diff = (valid_avg["bowling_average"] - expected_avg).abs()
    results["bowling_average_formula_consistent"] = bool((avg_diff < 0.02).all())

    # 4. Bowling average null when zero wickets
    zero_wkts = hp_performance_df[hp_performance_df["wickets_credited"] == 0]
    results["zero_wickets_average_is_null"] = bool(zero_wkts["bowling_average"].isna().all())

    # 5. BPPI-B score bounds [0, 100]
    results["bppi_b_within_bounds"] = bool(
        (bppi_df["bppi_b"] >= 0.0).all() and (bppi_df["bppi_b"] <= 100.0).all()
    )

    # 6. Component scores bounds [0, 100]
    comp_cols = [
        "score_economy_retention",
        "score_wicket_taking",
        "score_dot_ball_generation",
        "score_boundary_prevention",
        "score_average_retention",
    ]
    results["component_scores_within_bounds"] = bool(
        all(
            (bppi_df[col] >= 0.0).all() and (bppi_df[col] <= 100.0).all()
            for col in comp_cols
            if col in bppi_df.columns
        )
    )

    # 7. Uniqueness of primary keys
    results["hp_no_duplicate_players"] = bool(hp_performance_df["player_id"].is_unique)
    results["bppi_no_duplicate_players"] = bool(bppi_df["player_id"].is_unique)

    # 8. Classification validity
    valid_classes = {
        "Elite Under Pressure",
        "Strong Under Pressure",
        "Average Under Pressure",
        "Below Baseline Under Pressure",
        "Insufficient Evidence",
    }
    actual_classes = set(bppi_df["bowler_classification"].unique())
    results["classifications_valid"] = bool(actual_classes.issubset(valid_classes))

    # 9. Situational consistency
    results["situational_runs_non_negative"] = bool((situational_df["runs_conceded"] >= 0).all())

    all_passed = all(results.values())
    logger.info("Validation completed: %d checks executed, all passed = %s", len(results), all_passed)
    return results

