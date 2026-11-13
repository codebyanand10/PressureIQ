"""Bowler classification module under pressure conditions.

Assigns evidence-based performance classifications:
- Elite Under Pressure
- Strong Under Pressure
- Average Under Pressure
- Below Baseline Under Pressure
- Insufficient Evidence

Produces `bowler_pressure_performance_index.parquet`.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig

logger = logging.getLogger(__name__)


def classify_bowlers(
    reliability_df: pd.DataFrame,
    config: Optional[BowlingPressureConfig] = None,
) -> pd.DataFrame:
    """Classify bowlers into pressure performance tiers based on BPPI-B and statistical evidence.

    Args:
        reliability_df: DataFrame from bowling_reliability with BPPI-B, sample metrics, and reliability tiers.
        config: Configuration parameters with classification thresholds.

    Returns:
        DataFrame representing `bowler_pressure_performance_index.parquet`.
    """
    cfg = config or BowlingPressureConfig()
    logger.info("Classifying bowlers by pressure performance and statistical evidence...")

    df = reliability_df.copy()

    bppi_b = df["bppi_b"].fillna(50.0)
    rel = df["reliability_level"].fillna("Insufficient Data")
    lb = df["legal_balls_bowled"].fillna(0).astype(int)

    # Classification Rules
    cond_insufficient = (rel == "Insufficient Data") | (lb < cfg.low_min_balls)
    cond_elite = (bppi_b >= cfg.elite_bppi_min) & (rel.isin(["High", "Medium"])) & (lb >= cfg.medium_min_balls)
    cond_strong = (bppi_b >= cfg.strong_bppi_min) & (bppi_b < cfg.elite_bppi_min) & (rel.isin(["High", "Medium"])) & (lb >= cfg.medium_min_balls)
    cond_average = (bppi_b >= cfg.average_bppi_min) & (bppi_b < cfg.strong_bppi_min) & (~cond_insufficient)
    cond_below = (bppi_b < cfg.average_bppi_min) & (~cond_insufficient)

    classification = np.where(
        cond_insufficient, "Insufficient Evidence",
        np.where(cond_elite, "Elite Under Pressure",
        np.where(cond_strong, "Strong Under Pressure",
        np.where(cond_average, "Average Under Pressure",
        np.where(cond_below, "Below Baseline Under Pressure", "Average Under Pressure"))))
    )

    df["bowler_classification"] = classification

    # Classification rationale code
    rationale = np.where(
        cond_insufficient, "SAMPLE_SIZE_INSUFFICIENT",
        np.where(cond_elite, "HIGH_BPPI_B_ROBUST_SAMPLE",
        np.where(cond_strong, "ELEVATED_BPPI_B_ROBUST_SAMPLE",
        np.where(cond_average, "BASELINE_PARITY",
        np.where(cond_below, "PERFORMANCE_DEGRADATION", "UNCLASSIFIED"))))
    )
    df["classification_rationale_code"] = rationale

    logger.info(
        "Bowler classification distribution: Elite=%d, Strong=%d, Average=%d, Below Baseline=%d, Insufficient Evidence=%d",
        (df["bowler_classification"] == "Elite Under Pressure").sum(),
        (df["bowler_classification"] == "Strong Under Pressure").sum(),
        (df["bowler_classification"] == "Average Under Pressure").sum(),
        (df["bowler_classification"] == "Below Baseline Under Pressure").sum(),
        (df["bowler_classification"] == "Insufficient Evidence").sum(),
    )
    return df

