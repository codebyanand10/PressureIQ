"""Batting baseline calculation module.

Generates overall and low-pressure reference batting baselines for all eligible batters.
Preserves clear separation between overall and low-pressure reference sets.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import pandas as pd

from src.baselines.baseline_config import BaselineConfig
from src.baselines.batting_metrics import compute_batting_metrics

logger = logging.getLogger(__name__)


def calculate_batting_baselines(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    config: Optional[BaselineConfig] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generate overall and low-pressure batting baselines.

    Args:
        deliveries_df: Match state dataset with pressure scores.
        player_registry_df: Master player registry.
        config: Optional BaselineConfig.

    Returns:
        Tuple of (batting_overall_baseline, batting_low_pressure_baseline).
    """
    cfg = config or BaselineConfig()
    logger.info("Computing batting baselines (version: %s)...", cfg.version)

    df = deliveries_df.copy()
    registry_map = player_registry_df.set_index("player_id")["player_name"].to_dict()

    # Determine global date bounds
    start_date = df["delivery_ist_time"].str[:10].min() if "delivery_ist_time" in df.columns else "2022-01-22"
    end_date = df["delivery_ist_time"].str[:10].max() if "delivery_ist_time" in df.columns else "2026-11-01"

    # 1. Overall Batting Baseline (All eligible deliveries)
    logger.info("Calculating overall batting baselines across %d deliveries...", len(df))
    bat_overall = compute_batting_metrics(df, group_col="striker_id")
    bat_overall = bat_overall.rename(columns={"striker_id": "player_id"})
    bat_overall["player_name"] = bat_overall["player_id"].map(registry_map).fillna("Unknown")
    bat_overall["baseline_type"] = "overall"
    bat_overall["baseline_start_date"] = start_date
    bat_overall["baseline_end_date"] = end_date
    bat_overall["baseline_version"] = cfg.version

    # 2. Low-Pressure Batting Baseline
    lp_mask = df["batting_pressure_score"].fillna(50.0) <= cfg.batting_low_pressure_max
    df_lp = df[lp_mask]
    logger.info(
        "Calculating low-pressure batting baselines across %d deliveries (pressure <= %.1f)...",
        len(df_lp),
        cfg.batting_low_pressure_max,
    )

    bat_lp = compute_batting_metrics(df_lp, group_col="striker_id")
    bat_lp = bat_lp.rename(columns={"striker_id": "player_id"})
    bat_lp["player_name"] = bat_lp["player_id"].map(registry_map).fillna("Unknown")
    bat_lp["baseline_type"] = "low_pressure"
    bat_lp["baseline_start_date"] = start_date
    bat_lp["baseline_end_date"] = end_date
    bat_lp["baseline_version"] = cfg.version

    logger.info(
        "Batting baselines complete: %d overall batters, %d low-pressure batters.",
        len(bat_overall),
        len(bat_lp),
    )

    return bat_overall, bat_lp

