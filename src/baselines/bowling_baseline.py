"""Bowling baseline calculation module.

Generates overall and low-pressure reference bowling baselines for all eligible bowlers.
Separates general bowling performance from low-pressure baseline performance.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import pandas as pd

from src.baselines.baseline_config import BaselineConfig
from src.baselines.bowling_metrics import compute_bowling_metrics

logger = logging.getLogger(__name__)


def calculate_bowling_baselines(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    config: Optional[BaselineConfig] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generate overall and low-pressure bowling baselines.

    Args:
        deliveries_df: Match state dataset with pressure scores.
        player_registry_df: Master player registry.
        config: Optional BaselineConfig.

    Returns:
        Tuple of (bowling_overall_baseline, bowling_low_pressure_baseline).
    """
    cfg = config or BaselineConfig()
    logger.info("Computing bowling baselines (version: %s)...", cfg.version)

    df = deliveries_df.copy()
    registry_map = player_registry_df.set_index("player_id")["player_name"].to_dict()

    start_date = df["delivery_ist_time"].str[:10].min() if "delivery_ist_time" in df.columns else "2022-01-22"
    end_date = df["delivery_ist_time"].str[:10].max() if "delivery_ist_time" in df.columns else "2026-11-01"

    # 1. Overall Bowling Baseline (All eligible deliveries)
    logger.info("Calculating overall bowling baselines across %d deliveries...", len(df))
    bowl_overall = compute_bowling_metrics(df, group_col="bowler_id")
    bowl_overall = bowl_overall.rename(columns={"bowler_id": "player_id"})
    bowl_overall["player_name"] = bowl_overall["player_id"].map(registry_map).fillna("Unknown")
    bowl_overall["baseline_type"] = "overall"
    bowl_overall["baseline_start_date"] = start_date
    bowl_overall["baseline_end_date"] = end_date
    bowl_overall["baseline_version"] = cfg.version

    # 2. Low-Pressure Bowling Baseline
    lp_mask = df["bowling_pressure_score"].fillna(50.0) <= cfg.bowling_low_pressure_max
    df_lp = df[lp_mask]
    logger.info(
        "Calculating low-pressure bowling baselines across %d deliveries (pressure <= %.1f)...",
        len(df_lp),
        cfg.bowling_low_pressure_max,
    )

    bowl_lp = compute_bowling_metrics(df_lp, group_col="bowler_id")
    bowl_lp = bowl_lp.rename(columns={"bowler_id": "player_id"})
    bowl_lp["player_name"] = bowl_lp["player_id"].map(registry_map).fillna("Unknown")
    bowl_lp["baseline_type"] = "low_pressure"
    bowl_lp["baseline_start_date"] = start_date
    bowl_lp["baseline_end_date"] = end_date
    bowl_lp["baseline_version"] = cfg.version

    logger.info(
        "Bowling baselines complete: %d overall bowlers, %d low-pressure bowlers.",
        len(bowl_overall),
        len(bowl_lp),
    )

    return bowl_overall, bowl_lp

