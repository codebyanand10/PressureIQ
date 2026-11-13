"""Bowler role analyzer module.

Analyzes bowling usage distributions across match phases:
- Powerplay (overs 1-6)
- Middle overs (overs 7-15)
- Death overs (overs 16-20)

Assigns evidence-based bowling roles:
- Powerplay Specialist
- Middle-Overs Specialist
- Death-Overs Specialist
- Multi-Phase Bowler

Produces `bowler_role_analysis.parquet`.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bowling_pressure_metrics import annotate_bowling_deliveries

logger = logging.getLogger(__name__)


def analyze_bowler_roles(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    config: Optional[BowlingPressureConfig] = None,
) -> pd.DataFrame:
    """Analyze historical bowling phase distributions and assign tactical bowling roles.

    Args:
        deliveries_df: Delivery dataset.
        player_registry_df: Master player registry.
        config: Configuration parameters.

    Returns:
        DataFrame representing `bowler_role_analysis.parquet`.
    """
    cfg = config or BowlingPressureConfig()
    logger.info("Analyzing bowling roles and phase distributions...")

    d = annotate_bowling_deliveries(deliveries_df)
    legal = d[d["is_legal_calc"] == 1].copy()

    # Determine phase for each ball
    phase_col = "innings_phase_before" if "innings_phase_before" in legal.columns else None
    if not phase_col:
        # Fallback to overid
        legal["phase"] = np.where(
            legal["overid"] < 6, "powerplay",
            np.where(legal["overid"] < 15, "middle", "death")
        )
    else:
        legal["phase"] = legal["innings_phase_before"]

    # Count legal balls per bowler per phase
    phase_counts = legal.groupby(["bowler_id", "phase"]).size().unstack(fill_value=0)
    for p in ["powerplay", "middle", "death"]:
        if p not in phase_counts.columns:
            phase_counts[p] = 0

    total_legal = phase_counts.sum(axis=1)
    phase_counts["total_legal_balls"] = total_legal

    # Phase proportions
    phase_counts["powerplay_pct"] = np.where(total_legal > 0, (phase_counts["powerplay"] / total_legal) * 100.0, 0.0).round(1)
    phase_counts["middle_pct"] = np.where(total_legal > 0, (phase_counts["middle"] / total_legal) * 100.0, 0.0).round(1)
    phase_counts["death_pct"] = np.where(total_legal > 0, (phase_counts["death"] / total_legal) * 100.0, 0.0).round(1)

    # High pressure phase counts (pressure >= 60.0)
    hp_legal = legal[legal["bowling_pressure_score"] >= cfg.high_pressure_threshold]
    hp_counts = hp_legal.groupby(["bowler_id", "phase"]).size().unstack(fill_value=0)
    for p in ["powerplay", "middle", "death"]:
        if p not in hp_counts.columns:
            hp_counts[p] = 0
    hp_total = hp_counts.sum(axis=1)

    phase_counts["hp_total_legal_balls"] = hp_total.reindex(phase_counts.index).fillna(0).astype(int)
    phase_counts["hp_powerplay_balls"] = hp_counts["powerplay"].reindex(phase_counts.index).fillna(0).astype(int)
    phase_counts["hp_middle_balls"] = hp_counts["middle"].reindex(phase_counts.index).fillna(0).astype(int)
    phase_counts["hp_death_balls"] = hp_counts["death"].reindex(phase_counts.index).fillna(0).astype(int)

    # Tactical Role Assignment
    pp_ratio = phase_counts["powerplay"] / total_legal
    mid_ratio = phase_counts["middle"] / total_legal
    death_ratio = phase_counts["death"] / total_legal
    min_balls = cfg.min_balls_for_role

    conditions = [
        total_legal < min_balls,
        pp_ratio >= cfg.powerplay_threshold,
        death_ratio >= cfg.death_threshold,
        mid_ratio >= cfg.middle_threshold,
    ]
    choices = [
        "Unclassified / Part-Timer",
        "Powerplay Specialist",
        "Death-Overs Specialist",
        "Middle-Overs Specialist",
    ]
    phase_counts["bowling_role"] = np.select(conditions, choices, default="Multi-Phase Bowler")

    # Primary Bowling Style (Pace vs Spin)
    if "pace_or_spin" in legal.columns:
        style_series = legal.groupby("bowler_id")["pace_or_spin"].first().dropna().astype(str).str.title()
        phase_counts["primary_bowling_style"] = phase_counts.index.map(style_series).fillna("Unknown")
    else:
        phase_counts["primary_bowling_style"] = "Unknown"

    role_df = phase_counts.reset_index().rename(columns={"bowler_id": "player_id"})

    # Map player names from registry
    reg_names = player_registry_df.set_index("player_id")["player_name"].to_dict()
    role_df["player_name"] = role_df["player_id"].map(reg_names).fillna("Unknown")

    logger.info(
        "Classified bowling roles: %s",
        role_df["bowling_role"].value_counts().to_dict(),
    )
    return role_df

