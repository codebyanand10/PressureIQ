"""Baseline reliability assessment module.

Evaluates sample density, dismissal/wicket confidence, and match breadth to assign
transparent reliability ratings (High, Medium, Low, Insufficient Data).
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from src.baselines.baseline_config import BaselineConfig

logger = logging.getLogger(__name__)


def assess_batting_reliability(
    df: pd.DataFrame,
    config: Optional[BaselineConfig] = None,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate batting reliability scores, levels, and flags.

    Returns:
        Tuple of (score_series, level_series, flags_series).
    """
    cfg = config or BaselineConfig()
    balls = df["total_balls_faced"].fillna(0).astype(int).values
    dismissals = df["dismissals"].fillna(0).astype(int).values
    matches = df.get("matches_batted", pd.Series(1, index=df.index)).fillna(1).astype(int).values

    scores = np.zeros(len(df), dtype=float)
    levels = []
    flags = []

    for i in range(len(df)):
        b = balls[i]
        d = dismissals[i]
        m = matches[i]
        fl = []

        # Numerical score (0-100) based on balls faced and dismissals
        score = min(100.0, (b / float(cfg.batting_high_min_balls)) * 75.0 + min(25.0, d * 5.0))
        scores[i] = round(score, 1)

        # Level assignment
        if b >= cfg.batting_high_min_balls and d >= cfg.batting_min_dismissals:
            lvl = "High"
        elif b >= cfg.batting_medium_min_balls:
            lvl = "Medium"
        elif b >= cfg.batting_low_min_balls:
            lvl = "Low"
        else:
            lvl = "Insufficient Data"
            fl.append("SMALL_SAMPLE")

        if d == 0 and b > 0:
            fl.append("ZERO_DISMISSALS")
        if m == 1:
            fl.append("SINGLE_MATCH_SAMPLE")
        if not fl:
            fl.append("NORMAL")

        levels.append(lvl)
        flags.append(";".join(fl))

    index = df.index
    return (
        pd.Series(scores, index=index, name="baseline_reliability_score"),
        pd.Series(levels, index=index, name="baseline_reliability_level"),
        pd.Series(flags, index=index, name="baseline_reliability_flags"),
    )


def assess_bowling_reliability(
    df: pd.DataFrame,
    config: Optional[BaselineConfig] = None,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate bowling reliability scores, levels, and flags.

    Returns:
        Tuple of (score_series, level_series, flags_series).
    """
    cfg = config or BaselineConfig()
    balls = df["legal_balls_bowled"].fillna(0).astype(int).values
    wickets = df["wickets_credited"].fillna(0).astype(int).values
    matches = df.get("matches_bowled", pd.Series(1, index=df.index)).fillna(1).astype(int).values

    scores = np.zeros(len(df), dtype=float)
    levels = []
    flags = []

    for i in range(len(df)):
        b = balls[i]
        w = wickets[i]
        m = matches[i]
        fl = []

        score = min(100.0, (b / float(cfg.bowling_high_min_balls)) * 75.0 + min(25.0, w * 5.0))
        scores[i] = round(score, 1)

        if b >= cfg.bowling_high_min_balls and w >= cfg.bowling_min_wickets:
            lvl = "High"
        elif b >= cfg.bowling_medium_min_balls:
            lvl = "Medium"
        elif b >= cfg.bowling_low_min_balls:
            lvl = "Low"
        else:
            lvl = "Insufficient Data"
            fl.append("SMALL_SAMPLE")

        if w == 0 and b > 0:
            fl.append("ZERO_WICKETS")
        if m == 1:
            fl.append("SINGLE_MATCH_SAMPLE")
        if not fl:
            fl.append("NORMAL")

        levels.append(lvl)
        flags.append(";".join(fl))

    index = df.index
    return (
        pd.Series(scores, index=index, name="baseline_reliability_score"),
        pd.Series(levels, index=index, name="baseline_reliability_level"),
        pd.Series(flags, index=index, name="baseline_reliability_flags"),
    )


def assess_baseline_reliability(
    batting_df: pd.DataFrame,
    bowling_df: pd.DataFrame,
    config: Optional[BaselineConfig] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Enrich batting and bowling baselines with reliability tags and build combined reliability dataset.

    Returns:
        Tuple of (enriched_batting_df, enriched_bowling_df, combined_reliability_df).
    """
    cfg = config or BaselineConfig()
    b_df = batting_df.copy()
    bw_df = bowling_df.copy()

    # Batting reliability
    b_score, b_level, b_flags = assess_batting_reliability(b_df, cfg)
    b_df["baseline_reliability_score"] = b_score
    b_df["baseline_reliability_level"] = b_level
    b_df["baseline_reliability_flags"] = b_flags

    # Bowling reliability
    bw_score, bw_level, bw_flags = assess_bowling_reliability(bw_df, cfg)
    bw_df["baseline_reliability_score"] = bw_score
    bw_df["baseline_reliability_level"] = bw_level
    bw_df["baseline_reliability_flags"] = bw_flags

    # Combined player reliability table
    rel_rows = []
    for idx, row in b_df.iterrows():
        rel_rows.append({
            "player_id": row["player_id"],
            "player_name": row["player_name"],
            "role": "batter",
            "baseline_type": row.get("baseline_type", "overall"),
            "sample_volume": row["total_balls_faced"],
            "reliability_score": row["baseline_reliability_score"],
            "reliability_level": row["baseline_reliability_level"],
            "reliability_flags": row["baseline_reliability_flags"],
        })
    for idx, row in bw_df.iterrows():
        rel_rows.append({
            "player_id": row["player_id"],
            "player_name": row["player_name"],
            "role": "bowler",
            "baseline_type": row.get("baseline_type", "overall"),
            "sample_volume": row["legal_balls_bowled"],
            "reliability_score": row["baseline_reliability_score"],
            "reliability_level": row["baseline_reliability_level"],
            "reliability_flags": row["baseline_reliability_flags"],
        })

    combined_rel_df = pd.DataFrame(rel_rows)
    return b_df, bw_df, combined_rel_df

