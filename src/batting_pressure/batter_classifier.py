"""Batter classification module under pressure conditions.

Assigns interpretable performance classifications:
- Elite Under Pressure
- Strong Under Pressure
- Average Under Pressure
- Below Baseline Under Pressure
- Insufficient Evidence

Produces `batter_pressure_performance_index.parquet`.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

from src.batting_pressure.batting_pressure_config import BattingPressureConfig

logger = logging.getLogger(__name__)


def classify_batters(
    reliability_df: pd.DataFrame,
    config: Optional[BattingPressureConfig] = None,
) -> pd.DataFrame:
    """Classify batters into pressure performance tiers based on BPPI and statistical evidence.

    Args:
        reliability_df: DataFrame from batting_reliability with BPPI, sample metrics, and reliability tiers.
        config: Configuration parameters with classification thresholds.

    Returns:
        DataFrame representing `batter_pressure_performance_index.parquet`.
    """
    cfg = config or BattingPressureConfig()
    logger.info("Classifying batters by pressure performance and statistical evidence...")

    df = reliability_df.copy()

    bppi = df["bppi"].fillna(50.0)
    rel = df["reliability_level"].fillna("Insufficient Data")
    bf = df["balls_faced"].fillna(0).astype(int)

    # Classification Rules
    cond_insufficient = (rel == "Insufficient Data") | (bf < cfg.low_min_balls)
    cond_elite = (bppi >= cfg.elite_bppi_min) & (rel.isin(["High", "Medium"])) & (bf >= cfg.medium_min_balls)
    cond_strong = (bppi >= cfg.strong_bppi_min) & (bppi < cfg.elite_bppi_min) & (rel.isin(["High", "Medium"])) & (bf >= cfg.medium_min_balls)
    cond_average = (bppi >= cfg.average_bppi_min) & (bppi < cfg.strong_bppi_min) & (~cond_insufficient)
    cond_below = (bppi < cfg.average_bppi_min) & (~cond_insufficient)

    classification = np.where(
        cond_insufficient, "Insufficient Evidence",
        np.where(cond_elite, "Elite Under Pressure",
        np.where(cond_strong, "Strong Under Pressure",
        np.where(cond_average, "Average Under Pressure",
        np.where(cond_below, "Below Baseline Under Pressure", "Average Under Pressure"))))
    )

    df["batter_classification"] = classification

    # Classification rationale code
    rationale = np.where(
        cond_insufficient, "SAMPLE_SIZE_INSUFFICIENT",
        np.where(cond_elite, "HIGH_BPPI_ROBUST_SAMPLE",
        np.where(cond_strong, "ELEVATED_BPPI_ROBUST_SAMPLE",
        np.where(cond_average, "BASELINE_PARITY",
        np.where(cond_below, "PERFORMANCE_DEGRADATION", "UNCLASSIFIED"))))
    )
    df["classification_rationale_code"] = rationale

    logger.info(
        "Classification distribution: Elite=%d, Strong=%d, Average=%d, Below Baseline=%d, Insufficient Evidence=%d",
        (df["batter_classification"] == "Elite Under Pressure").sum(),
        (df["batter_classification"] == "Strong Under Pressure").sum(),
        (df["batter_classification"] == "Average Under Pressure").sum(),
        (df["batter_classification"] == "Below Baseline Under Pressure").sum(),
        (df["batter_classification"] == "Insufficient Evidence").sum(),
    )
    return df

