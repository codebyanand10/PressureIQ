"""Pressure category aggregator for bowling performance under pressure.

Partitions deliveries across the 5 canonical pressure categories:
- Very Low (0-19.99)
- Low (20-39.99)
- Moderate (40-59.99)
- High (60-79.99)
- Extreme (80-100)

Produces:
1. `bowler_pressure_category_metrics.parquet`: player-level stats across all 5 categories.
2. `bowler_high_pressure_performance.parquet`: dedicated high+extreme pressure cohort (pressure >= 60.0).
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bowling_pressure_metrics import (
    annotate_bowling_deliveries,
    compute_bowling_pressure_metrics,
)

logger = logging.getLogger(__name__)


def assign_bowling_pressure_category(
    pressure_scores: pd.Series,
    config: BowlingPressureConfig,
) -> pd.Series:
    """Vectorized assignment of bowling pressure score into categorical buckets."""
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


def aggregate_by_bowling_pressure_category(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    config: Optional[BowlingPressureConfig] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate bowling performance across pressure categories and high-pressure cohort.

    Args:
        deliveries_df: Delivery dataset with bowling_pressure_score.
        player_registry_df: Master player registry.
        config: Configuration parameters.

    Returns:
        Tuple of (category_metrics_df, high_pressure_performance_df).
    """
    cfg = config or BowlingPressureConfig()
    logger.info("Aggregating bowling performance by pressure categories...")

    df = annotate_bowling_deliveries(deliveries_df)
    df["pressure_category"] = assign_bowling_pressure_category(df["bowling_pressure_score"], cfg)

    # 1. Category Metrics: group by (bowler_id, pressure_category)
    logger.info("Computing bowling metrics across all 5 pressure categories...")
    cat_metrics = compute_bowling_pressure_metrics(
        deliveries_df=df,
        group_col=["bowler_id", "pressure_category"],
    )
    cat_metrics = cat_metrics.rename(columns={"bowler_id": "player_id"})

    # Map player names from registry
    reg_names = player_registry_df.set_index("player_id")["player_name"].to_dict()
    cat_metrics["player_name"] = cat_metrics["player_id"].map(reg_names).fillna(cat_metrics.get("bowler_name", "Unknown"))
    if "bowler_name" in cat_metrics.columns:
        cat_metrics = cat_metrics.drop(columns=["bowler_name"])

    # 2. High-Pressure Cohort: deliveries where bowling_pressure_score >= 60.0
    logger.info("Computing dedicated high-pressure (>= %.1f) bowling performance...", cfg.high_pressure_threshold)
    hp_deliveries = df[df["bowling_pressure_score"] >= cfg.high_pressure_threshold].copy()

    hp_metrics = compute_bowling_pressure_metrics(
        deliveries_df=hp_deliveries,
        group_col="bowler_id",
    )
    hp_metrics = hp_metrics.rename(columns={"bowler_id": "player_id"})
    hp_metrics["player_name"] = hp_metrics["player_id"].map(reg_names).fillna(hp_metrics.get("bowler_name", "Unknown"))
    if "bowler_name" in hp_metrics.columns:
        hp_metrics = hp_metrics.drop(columns=["bowler_name"])

    # Add sample deliveries count (including wides/no-balls)
    deliv_counts = hp_deliveries.groupby("bowler_id").size()
    hp_metrics["sample_deliveries"] = hp_metrics["player_id"].map(deliv_counts).fillna(0).astype(int)

    # Add specific breakdown: high pressure balls vs extreme pressure balls
    high_sub = hp_deliveries[hp_deliveries["pressure_category"] == "high"]
    extreme_sub = hp_deliveries[hp_deliveries["pressure_category"] == "extreme"]

    high_balls = high_sub[high_sub["is_legal_calc"] == 1].groupby("bowler_id").size()
    extreme_balls = extreme_sub[extreme_sub["is_legal_calc"] == 1].groupby("bowler_id").size()

    hp_metrics["high_pressure_balls"] = hp_metrics["player_id"].map(high_balls).fillna(0).astype(int)
    hp_metrics["extreme_pressure_balls"] = hp_metrics["player_id"].map(extreme_balls).fillna(0).astype(int)

    logger.info(
        "Aggregated %d category records and %d high-pressure bowler records.",
        len(cat_metrics),
        len(hp_metrics),
    )
    return cat_metrics, hp_metrics

