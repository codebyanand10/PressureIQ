"""Batting Pressure Performance Index (BPPI) calculator module.

Calculates the canonical BPPI (0 to 100) combining:
1. Strike-rate retention (30%)
2. Batting-average retention (25%)
3. Boundary efficiency (20%)
4. Dot-ball control (15%)
5. Dismissal management (10%)

Preserves all intermediate component scores for complete transparency and explainability.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

from src.batting_pressure.batting_pressure_config import BattingPressureConfig

logger = logging.getLogger(__name__)


def calculate_bppi(
    comparison_df: pd.DataFrame,
    config: Optional[BattingPressureConfig] = None,
) -> pd.DataFrame:
    """Calculate normalized Batting Pressure Performance Index (BPPI) and its sub-components.

    Args:
        comparison_df: Output from baseline_comparator (`batter_baseline_comparison`).
        config: Configuration parameters with weights and caps.

    Returns:
        DataFrame containing BPPI score and explainable component breakdown.
    """
    cfg = config or BattingPressureConfig()
    logger.info("Calculating Batting Pressure Performance Index (BPPI)...")

    df = comparison_df.copy()

    # 1. Strike Rate Retention Score (0-100)
    # 100% retention -> 50.0 score; 150% -> 75.0; 200% -> 100.0; 0% -> 0.0
    sr_ret = df["strike_rate_retention"].fillna(100.0)
    df["score_sr_retention"] = np.clip(sr_ret * 0.50, 0.0, 100.0).round(2)

    # 2. Batting Average Retention Score (0-100)
    # Uses shrunk baseline average where possible to mitigate extreme small-sample denominators
    shrunk_base_avg = df.get("overall_shrunk_batting_average", df.get("overall_batting_average", pd.Series(22.0, index=df.index)))
    hp_avg = df["batting_average"]
    dism = df["dismissals"].fillna(0).astype(int)
    runs = df["total_runs"].fillna(0).astype(float)

    # If dismissals == 0 and runs > 0, player was never dismissed under high pressure: reward based on runs
    avg_ret_raw = np.where(
        dism > 0,
        np.where(shrunk_base_avg > 0, (hp_avg / shrunk_base_avg) * 100.0, 100.0),
        np.where(runs >= 30, 180.0, np.where(runs >= 15, 140.0, 100.0)),
    )
    df["score_average_retention"] = np.clip(avg_ret_raw * 0.50, 0.0, 100.0).round(2)

    # 3. Boundary Efficiency Score (0-100)
    # Difference from baseline boundary %: 0% diff -> 50.0 score; +30% diff -> 100.0 score; -30% diff -> 0.0 score
    bnd_diff = df["boundary_percentage_difference"].fillna(0.0)
    df["score_boundary_efficiency"] = np.clip(50.0 + (bnd_diff * (50.0 / 30.0)), 0.0, 100.0).round(2)

    # 4. Dot Ball Control Score (0-100)
    # Difference from baseline dot-ball %: negative is favorable!
    # 0% diff -> 50.0 score; -30% diff -> 100.0 score; +30% diff -> 0.0 score
    dot_diff = df["dot_ball_difference"].fillna(0.0)
    df["score_dot_ball_control"] = np.clip(50.0 - (dot_diff * (50.0 / 30.0)), 0.0, 100.0).round(2)

    # 5. Dismissal Management Score (0-100)
    # Difference from baseline dismissal rate: negative is favorable!
    # 0 diff -> 50.0 score; -0.05 diff -> 100.0 score; +0.05 diff -> 0.0 score
    dism_diff = df["dismissal_risk_difference"].fillna(0.0)
    df["score_dismissal_management"] = np.clip(50.0 - (dism_diff * 1000.0), 0.0, 100.0).round(2)

    # Weighted Composite BPPI
    w = cfg.bppi_weights
    raw_bppi = (
        w.get("strike_rate_retention", 0.30) * df["score_sr_retention"]
        + w.get("batting_average_retention", 0.25) * df["score_average_retention"]
        + w.get("boundary_efficiency", 0.20) * df["score_boundary_efficiency"]
        + w.get("dot_ball_control", 0.15) * df["score_dot_ball_control"]
        + w.get("dismissal_management", 0.10) * df["score_dismissal_management"]
    )
    df["bppi"] = np.clip(raw_bppi, 0.0, 100.0).round(2)

    logger.info(
        "BPPI calculated across %d batters (Mean: %.2f, Median: %.2f, Min: %.2f, Max: %.2f).",
        len(df),
        df["bppi"].mean(),
        df["bppi"].median(),
        df["bppi"].min(),
        df["bppi"].max(),
    )
    return df

