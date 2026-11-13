"""Pressure category aggregator for batting performance.

Partitions deliveries across the 5 canonical pressure categories:
- Very Low (0-19.99)
- Low (20-39.99)
- Moderate (40-59.99)
- High (60-79.99)
- Extreme (80-100)

Produces:
1. `batter_pressure_category_metrics.parquet`: player-level stats across all 5 categories.
2. `batter_high_pressure_performance.parquet`: dedicated high+extreme pressure cohort (pressure >= 60.0).
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from src.batting_pressure.batting_pressure_config import BattingPressureConfig
from src.batting_pressure.batting_pressure_metrics import (
    annotate_batting_deliveries,
    compute_batting_pressure_metrics,
)

logger = logging.getLogger(__name__)


def assign_pressure_category(
    pressure_scores: pd.Series,
    config: BattingPressureConfig,
) -> pd.Series:
    """Vectorized assignment of pressure score into categorical buckets."""
    s = pressure_scores.fillna(0.0)
    conditions = [
        s <= config.very_low_max,
        (s > config.very_low_max) & (s <= config.low_max),
        (s > config.low_max) & (s <= config.moderate_max),
        (s > config.moderate_max) & (s <= config.high_max),
        s > config.high_max,
    ]
    choices = ["very_low", "low", "moderate", "high", "extreme"]
    return pd.Series(np.select(conditions, choices, default="low"), index=s.index)


def aggregate_by_pressure_category(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    config: Optional[BattingPressureConfig] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate batting performance across pressure categories and high-pressure cohort.

    Args:
        deliveries_df: Delivery dataset with batting_pressure_score.
        player_registry_df: Master player registry.
        config: Configuration parameters.

    Returns:
        Tuple of (category_metrics_df, high_pressure_performance_df).
    """
    cfg = config or BattingPressureConfig()
    logger.info("Aggregating batting performance by pressure categories...")

    df = annotate_batting_deliveries(deliveries_df)
    df["pressure_category"] = assign_pressure_category(df["batting_pressure_score"], cfg)

    # 1. Category Metrics: group by (striker_id, pressure_category)
    logger.info("Computing metrics across all 5 pressure categories...")
    cat_metrics = compute_batting_pressure_metrics(
        deliveries_df=df,
        group_col=["striker_id", "pressure_category"],
    )
    cat_metrics = cat_metrics.rename(columns={"striker_id": "player_id"})

    # Map player names from registry
    reg_names = player_registry_df.set_index("player_id")["player_name"].to_dict()
    cat_metrics["player_name"] = cat_metrics["player_id"].map(reg_names).fillna(cat_metrics.get("striker_name", "Unknown"))
    if "striker_name" in cat_metrics.columns:
        cat_metrics = cat_metrics.drop(columns=["striker_name"])

    # 2. High-Pressure Cohort: deliveries where batting_pressure_score >= 60.0
    logger.info("Computing dedicated high-pressure (>= %.1f) batting performance...", cfg.high_pressure_threshold)
    hp_deliveries = df[df["batting_pressure_score"] >= cfg.high_pressure_threshold].copy()

    hp_metrics = compute_batting_pressure_metrics(
        deliveries_df=hp_deliveries,
        group_col="striker_id",
    )
    hp_metrics = hp_metrics.rename(columns={"striker_id": "player_id"})
    hp_metrics["player_name"] = hp_metrics["player_id"].map(reg_names).fillna(hp_metrics.get("striker_name", "Unknown"))
    if "striker_name" in hp_metrics.columns:
        hp_metrics = hp_metrics.drop(columns=["striker_name"])

    # Add sample deliveries count (total high pressure deliveries faced, including wides)
    deliv_counts = hp_deliveries.groupby("striker_id").size()
    hp_metrics["sample_deliveries"] = hp_metrics["player_id"].map(deliv_counts).fillna(0).astype(int)

    # Add specific breakdown: high pressure balls vs extreme pressure balls
    high_sub = hp_deliveries[hp_deliveries["pressure_category"] == "high"]
    extreme_sub = hp_deliveries[hp_deliveries["pressure_category"] == "extreme"]

    high_balls = high_sub[high_sub["is_ball_faced"] == 1].groupby("striker_id").size()
    extreme_balls = extreme_sub[extreme_sub["is_ball_faced"] == 1].groupby("striker_id").size()

    hp_metrics["high_pressure_balls"] = hp_metrics["player_id"].map(high_balls).fillna(0).astype(int)
    hp_metrics["extreme_pressure_balls"] = hp_metrics["player_id"].map(extreme_balls).fillna(0).astype(int)

    logger.info(
        "Aggregated %d category records and %d high-pressure batter records.",
        len(cat_metrics),
        len(hp_metrics),
    )
    return cat_metrics, hp_metrics

