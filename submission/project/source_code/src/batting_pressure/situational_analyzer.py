"""Situational analysis module for batting under pressure.

Evaluates high-pressure performance partitioned across:
1. Innings Phase (Powerplay, Middle, Death)
2. Innings Number (1st Innings, 2nd Innings)
3. Competition Type (IPL, T20I, Domestic)
4. Match Stage (Knockout vs Non-Knockout)
5. Batting Position Group (Top, Middle, Lower Order)
6. Pressure Intensity (Moderate, High, Extreme)

Produces `batter_situational_performance.parquet`.
"""

from __future__ import annotations

import logging
from typing import List, Optional
import numpy as np
import pandas as pd

from src.batting_pressure.batting_pressure_config import BattingPressureConfig
from src.batting_pressure.batting_pressure_metrics import (
    annotate_batting_deliveries,
    compute_batting_pressure_metrics,
)

logger = logging.getLogger(__name__)


def analyze_situational_batting(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    config: Optional[BattingPressureConfig] = None,
) -> pd.DataFrame:
    """Analyze context-specific batting performance under pressure.

    Filters to pressure >= 40.0 (moderate, high, extreme) to ensure relevant sample depth.

    Args:
        deliveries_df: Delivery dataset with pressure scores and match metadata.
        player_registry_df: Master player registry.
        config: Configuration parameters.

    Returns:
        DataFrame representing `batter_situational_performance.parquet`.
    """
    cfg = config or BattingPressureConfig()
    logger.info("Computing situational batting performance under pressure...")

    d = annotate_batting_deliveries(deliveries_df)
    # Filter to pressure >= 40.0 for situational pressure analysis
    pressure_d = d[d["batting_pressure_score"] >= 40.0].copy()

    reg_names = player_registry_df.set_index("player_id")["player_name"].to_dict()

    situational_dfs: List[pd.DataFrame] = []

    # 1. Innings Phase
    if "innings_phase_before" in pressure_d.columns:
        phase_df = compute_batting_pressure_metrics(
            pressure_d,
            group_col=["striker_id", "innings_phase_before"],
        )
        phase_df = phase_df.rename(
            columns={"striker_id": "player_id", "innings_phase_before": "context_value"}
        )
        phase_df["context_type"] = "innings_phase"
        situational_dfs.append(phase_df)

    # 2. Innings Number (1st vs 2nd)
    if "innings" in pressure_d.columns:
        inn_sub = pressure_d.copy()
        inn_sub["innings_label"] = inn_sub["innings"].map({1: "1st_innings", 2: "2nd_innings"}).fillna("other")
        inn_df = compute_batting_pressure_metrics(
            inn_sub,
            group_col=["striker_id", "innings_label"],
        )
        inn_df = inn_df.rename(
            columns={"striker_id": "player_id", "innings_label": "context_value"}
        )
        inn_df["context_type"] = "innings_number"
        situational_dfs.append(inn_df)

    # 3. Competition Type
    if "competition_type" in pressure_d.columns:
        comp_df = compute_batting_pressure_metrics(
            pressure_d,
            group_col=["striker_id", "competition_type"],
        )
        comp_df = comp_df.rename(
            columns={"striker_id": "player_id", "competition_type": "context_value"}
        )
        comp_df["context_type"] = "competition_type"
        situational_dfs.append(comp_df)

    # 4. Match Stage (Knockout vs Non-Knockout)
    if "knock_out" in pressure_d.columns:
        ko_sub = pressure_d.copy()
        ko_sub["ko_label"] = np.where(ko_sub["knock_out"] == True, "knockout", "non_knockout")
        ko_df = compute_batting_pressure_metrics(
            ko_sub,
            group_col=["striker_id", "ko_label"],
        )
        ko_df = ko_df.rename(
            columns={"striker_id": "player_id", "ko_label": "context_value"}
        )
        ko_df["context_type"] = "match_stage"
        situational_dfs.append(ko_df)

    # 5. Batting Position Group
    if "batting_order" in pressure_d.columns:
        pos_sub = pressure_d.copy()
        bo = pos_sub["batting_order"].fillna(0).astype(int)
        pos_sub["position_group"] = np.where(
            bo.isin([1, 2, 3]), "top_order",
            np.where(bo.isin([4, 5, 6]), "middle_order",
            np.where(bo.isin([7, 8, 9, 10, 11]), "lower_order", "unassigned"))
        )
        pos_df = compute_batting_pressure_metrics(
            pos_sub,
            group_col=["striker_id", "position_group"],
        )
        pos_df = pos_df.rename(
            columns={"striker_id": "player_id", "position_group": "context_value"}
        )
        pos_df["context_type"] = "batting_position"
        situational_dfs.append(pos_df)

    # 6. Pressure Intensity (Moderate, High, Extreme)
    intensity_sub = pressure_d.copy()
    s = intensity_sub["batting_pressure_score"].fillna(0.0)
    intensity_sub["intensity_label"] = np.where(
        s < 60.0, "moderate",
        np.where(s < 80.0, "high", "extreme")
    )
    int_df = compute_batting_pressure_metrics(
        intensity_sub,
        group_col=["striker_id", "intensity_label"],
    )
    int_df = int_df.rename(
        columns={"striker_id": "player_id", "intensity_label": "context_value"}
    )
    int_df["context_type"] = "pressure_intensity"
    situational_dfs.append(int_df)

    # Combine all contexts
    combined = pd.concat(situational_dfs, ignore_index=True)
    combined["player_id"] = combined["player_id"].astype(str)
    combined["player_name"] = combined["player_id"].map(reg_names).fillna(combined.get("striker_name", "Unknown"))
    if "striker_name" in combined.columns:
        combined = combined.drop(columns=["striker_name"])

    logger.info("Generated %d situational records across %d contexts.", len(combined), combined["context_type"].nunique())
    return combined

