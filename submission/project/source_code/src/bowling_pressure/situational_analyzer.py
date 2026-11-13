"""Situational analysis module for bowling under pressure.

Evaluates pressure bowling performance partitioned across:
1. Innings Phase (Powerplay, Middle, Death)
2. Innings Number (1st Innings, 2nd Innings)
3. Competition Type (IPL, T20I, Domestic)
4. Bowling Style (Pace vs Spin)
5. Match Stage (Knockout vs Non-Knockout)
6. Pressure Intensity (Moderate, High, Extreme)

Produces `bowler_situational_performance.parquet`.
"""

from __future__ import annotations

import logging
from typing import List, Optional
import numpy as np
import pandas as pd

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bowling_pressure_metrics import (
    annotate_bowling_deliveries,
    compute_bowling_pressure_metrics,
)

logger = logging.getLogger(__name__)


def analyze_situational_bowling(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    config: Optional[BowlingPressureConfig] = None,
) -> pd.DataFrame:
    """Analyze context-specific bowling performance under pressure.

    Filters to pressure >= 40.0 (moderate, high, extreme) to ensure relevant sample volume.

    Args:
        deliveries_df: Delivery dataset with pressure scores and match metadata.
        player_registry_df: Master player registry.
        config: Configuration parameters.

    Returns:
        DataFrame representing `bowler_situational_performance.parquet`.
    """
    cfg = config or BowlingPressureConfig()
    logger.info("Computing situational bowling performance under pressure...")

    d = annotate_bowling_deliveries(deliveries_df)
    pressure_d = d[d["bowling_pressure_score"] >= 40.0].copy()

    reg_names = player_registry_df.set_index("player_id")["player_name"].to_dict()

    situational_dfs: List[pd.DataFrame] = []

    # 1. Innings Phase
    if "innings_phase_before" in pressure_d.columns:
        phase_df = compute_bowling_pressure_metrics(
            pressure_d,
            group_col=["bowler_id", "innings_phase_before"],
        )
        phase_df = phase_df.rename(
            columns={"bowler_id": "player_id", "innings_phase_before": "context_value"}
        )
        phase_df["context_type"] = "innings_phase"
        situational_dfs.append(phase_df)

    # 2. Innings Number (1st vs 2nd)
    if "innings" in pressure_d.columns:
        inn_sub = pressure_d.copy()
        inn_sub["innings_label"] = inn_sub["innings"].map({1: "1st_innings", 2: "2nd_innings"}).fillna("other")
        inn_df = compute_bowling_pressure_metrics(
            inn_sub,
            group_col=["bowler_id", "innings_label"],
        )
        inn_df = inn_df.rename(
            columns={"bowler_id": "player_id", "innings_label": "context_value"}
        )
        inn_df["context_type"] = "innings_number"
        situational_dfs.append(inn_df)

    # 3. Competition Type
    if "competition_type" in pressure_d.columns:
        comp_df = compute_bowling_pressure_metrics(
            pressure_d,
            group_col=["bowler_id", "competition_type"],
        )
        comp_df = comp_df.rename(
            columns={"bowler_id": "player_id", "competition_type": "context_value"}
        )
        comp_df["context_type"] = "competition_type"
        situational_dfs.append(comp_df)

    # 4. Bowling Style (Pace vs Spin)
    style_col = "pace_or_spin" if "pace_or_spin" in pressure_d.columns else None
    if style_col:
        style_sub = pressure_d.copy()
        clean_style = style_sub[style_col].fillna("Unknown").astype(str).str.title()
        valid_style = clean_style.isin(["Pace", "Spin"])
        style_sub["style_label"] = np.where(valid_style, clean_style, "Other")
        style_df = compute_bowling_pressure_metrics(
            style_sub,
            group_col=["bowler_id", "style_label"],
        )
        style_df = style_df.rename(
            columns={"bowler_id": "player_id", "style_label": "context_value"}
        )
        style_df["context_type"] = "bowling_style"
        situational_dfs.append(style_df)

    # 5. Match Stage (Knockout vs Non-Knockout)
    if "knock_out" in pressure_d.columns:
        ko_sub = pressure_d.copy()
        ko_sub["ko_label"] = np.where(ko_sub["knock_out"] == True, "knockout", "non_knockout")
        ko_df = compute_bowling_pressure_metrics(
            ko_sub,
            group_col=["bowler_id", "ko_label"],
        )
        ko_df = ko_df.rename(
            columns={"bowler_id": "player_id", "ko_label": "context_value"}
        )
        ko_df["context_type"] = "match_stage"
        situational_dfs.append(ko_df)

    # 6. Pressure Intensity (Moderate, High, Extreme)
    intensity_sub = pressure_d.copy()
    s = intensity_sub["bowling_pressure_score"].fillna(0.0)
    intensity_sub["intensity_label"] = np.where(
        s < 60.0, "moderate",
        np.where(s < 80.0, "high", "extreme")
    )
    int_df = compute_bowling_pressure_metrics(
        intensity_sub,
        group_col=["bowler_id", "intensity_label"],
    )
    int_df = int_df.rename(
        columns={"bowler_id": "player_id", "intensity_label": "context_value"}
    )
    int_df["context_type"] = "pressure_intensity"
    situational_dfs.append(int_df)

    # Combine all contexts
    combined = pd.concat(situational_dfs, ignore_index=True)
    combined["player_id"] = combined["player_id"].astype(str)
    combined["player_name"] = combined["player_id"].map(reg_names).fillna(combined.get("bowler_name", "Unknown"))
    if "bowler_name" in combined.columns:
        combined = combined.drop(columns=["bowler_name"])

    logger.info("Generated %d situational bowling records across %d contexts.", len(combined), combined["context_type"].nunique())
    return combined

