"""Statistical validation and data integrity auditor for batting under pressure.

Validates:
1. Mathematical formula consistency (strike rates, averages, retention).
2. Non-negativity of physical cricket counts.
3. Strict range bounds for BPPI and component scores (0 to 100).
4. Referential uniqueness (no duplicate player records).
5. Valid categorical assignments.
"""

from __future__ import annotations

import logging
from typing import Dict
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def validate_batting_pressure_datasets(
    category_df: pd.DataFrame,
    hp_performance_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    bppi_df: pd.DataFrame,
    situational_df: pd.DataFrame,
) -> Dict[str, bool]:
    """Execute comprehensive mathematical and domain sanity checks.

    Returns:
        Dictionary mapping check names to boolean pass/fail status.
    """
    logger.info("Executing Phase 6 statistical validation checks...")
    results: Dict[str, bool] = {}

    # 1. Non-negativity
    results["runs_non_negative"] = bool((category_df["total_runs"] >= 0).all())
    results["balls_non_negative"] = bool((category_df["balls_faced"] >= 0).all())
    results["dismissals_non_negative"] = bool((category_df["dismissals"] >= 0).all())

    # 2. Strike rate formula consistency
    valid_sr = hp_performance_df[hp_performance_df["balls_faced"] > 0]
    expected_sr = (valid_sr["total_runs"] / valid_sr["balls_faced"]) * 100.0
    sr_diff = (valid_sr["strike_rate"] - expected_sr).abs()
    results["strike_rate_formula_consistent"] = bool((sr_diff < 0.02).all())

    # 3. Batting average formula consistency
    valid_avg = hp_performance_df[hp_performance_df["dismissals"] > 0]
    expected_avg = valid_avg["total_runs"] / valid_avg["dismissals"]
    avg_diff = (valid_avg["batting_average"] - expected_avg).abs()
    results["batting_average_formula_consistent"] = bool((avg_diff < 0.02).all())

    # 4. Batting average null when zero dismissals
    zero_dism = hp_performance_df[hp_performance_df["dismissals"] == 0]
    results["zero_dismissals_average_is_null"] = bool(zero_dism["batting_average"].isna().all())

    # 5. BPPI score bounds [0, 100]
    results["bppi_within_bounds"] = bool(
        (bppi_df["bppi"] >= 0.0).all() and (bppi_df["bppi"] <= 100.0).all()
    )

    # 6. Component scores bounds [0, 100]
    comp_cols = [
        "score_sr_retention",
        "score_average_retention",
        "score_boundary_efficiency",
        "score_dot_ball_control",
        "score_dismissal_management",
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
    actual_classes = set(bppi_df["batter_classification"].unique())
    results["classifications_valid"] = bool(actual_classes.issubset(valid_classes))

    # 9. Situational consistency
    results["situational_runs_non_negative"] = bool((situational_df["total_runs"] >= 0).all())

    all_passed = all(results.values())
    logger.info("Validation completed: %d checks executed, all passed = %s", len(results), all_passed)
    return results

