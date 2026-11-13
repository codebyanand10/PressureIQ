"""Bowling Pressure Performance Index (BPPI-B) calculator module.

Calculates the canonical BPPI-B (0 to 100) combining:
1. Economy-rate retention (30%)
2. Wicket-taking effectiveness (25%)
3. Dot-ball generation (20%)
4. Boundary prevention (15%)
5. Bowling-average retention (10%)

Preserves all intermediate component scores for complete transparency and explainability.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig

logger = logging.getLogger(__name__)


def calculate_bppi_b(
    comparison_df: pd.DataFrame,
    config: Optional[BowlingPressureConfig] = None,
) -> pd.DataFrame:
    """Calculate normalized Bowling Pressure Performance Index (BPPI-B) and its sub-components.

    Args:
        comparison_df: Output from baseline_comparator (`bowler_baseline_comparison`).
        config: Configuration parameters with weights and caps.

    Returns:
        DataFrame containing BPPI-B score and explainable component breakdown.
    """
    cfg = config or BowlingPressureConfig()
    logger.info("Calculating Bowling Pressure Performance Index (BPPI-B)...")

    df = comparison_df.copy()

    # 1. Economy Rate Retention Score (0-100)
    # 100% retention -> 50.0 score; 150% -> 75.0; 200% -> 100.0; 0% -> 0.0
    econ_ret = df["economy_retention"].fillna(100.0)
    df["score_economy_retention"] = np.clip(econ_ret * 0.50, 0.0, 100.0).round(2)

    # 2. Wicket-Taking Effectiveness Score (0-100)
    # Difference in wickets per legal ball: +0.08 -> 100.0; 0.0 -> 50.0; -0.08 -> 0.0
    wkt_diff = df["wicket_taking_difference"].fillna(0.0)
    df["score_wicket_taking"] = np.clip(50.0 + (wkt_diff * 625.0), 0.0, 100.0).round(2)

    # 3. Dot-Ball Generation Score (0-100)
    # Difference from baseline dot-ball %: positive is favorable!
    # +30% diff -> 100.0 score; 0% diff -> 50.0 score; -30% diff -> 0.0 score
    dot_diff = df["dot_ball_difference"].fillna(0.0)
    df["score_dot_ball_generation"] = np.clip(50.0 + (dot_diff * (50.0 / 30.0)), 0.0, 100.0).round(2)

    # 4. Boundary Prevention Score (0-100)
    # Difference from baseline boundary % conceded: negative is favorable!
    # -30% diff -> 100.0 score; 0% diff -> 50.0 score; +30% diff -> 0.0 score
    bnd_diff = df["boundary_prevention_difference"].fillna(0.0)
    df["score_boundary_prevention"] = np.clip(50.0 - (bnd_diff * (50.0 / 30.0)), 0.0, 100.0).round(2)

    # 5. Bowling Average Retention Score (0-100)
    # Difference in bowling average (base_avg - hp_avg): positive is favorable!
    base_avg = df.get("overall_shrunk_bowling_average", df.get("overall_bowling_average", pd.Series(24.0, index=df.index)))
    hp_avg = df["bowling_average"]
    wkts = df["wickets_credited"].fillna(0).astype(int)

    avg_score_raw = np.where(
        wkts > 0,
        50.0 + ((base_avg - hp_avg) * 2.50),
        30.0,  # Penalty if 0 wickets taken under high pressure
    )
    df["score_average_retention"] = np.clip(avg_score_raw, 0.0, 100.0).round(2)

    # Weighted Composite BPPI-B
    w = cfg.bppi_b_weights
    raw_bppi_b = (
        w.get("economy_retention", 0.30) * df["score_economy_retention"]
        + w.get("wicket_taking_effectiveness", 0.25) * df["score_wicket_taking"]
        + w.get("dot_ball_generation", 0.20) * df["score_dot_ball_generation"]
        + w.get("boundary_prevention", 0.15) * df["score_boundary_prevention"]
        + w.get("bowling_average_retention", 0.10) * df["score_average_retention"]
    )
    df["bppi_b"] = np.clip(raw_bppi_b, 0.0, 100.0).round(2)

    logger.info(
        "BPPI-B calculated across %d bowlers (Mean: %.2f, Median: %.2f, Min: %.2f, Max: %.2f).",
        len(df),
        df["bppi_b"].mean(),
        df["bppi_b"].median(),
        df["bppi_b"].min(),
        df["bppi_b"].max(),
    )
    return df

