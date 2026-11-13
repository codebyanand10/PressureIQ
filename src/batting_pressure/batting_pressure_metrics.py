"""Batting metrics computation module under pressure conditions.

Calculates:
1. Scoring metrics: total runs, balls faced, strike rate, batting average, boundaries,
   boundary percentage, dot ball percentage, scoring delivery percentage.
2. Dismissal metrics: dismissals, dismissal rate, balls per dismissal, dismissal percentage.
3. Performance consistency metrics: innings scoring consistency, strike rate variability,
   average runs per innings, high score, low score, 30+ and 50+ innings counts.
"""

from __future__ import annotations

import logging
from typing import List, Union
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def annotate_batting_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """Add vectorized boolean and metric flags to delivery events.

    Strict cricket rules enforced:
    - Balls faced strictly excludes wides, includes no-balls, byes, leg-byes.
    - Batter runs strictly taken from batter_runs.
    - Dismissal counted only when is_wicket is True and dismissed_player_id == striker_id.
    """
    d = df.copy()
    d["striker_id"] = d["striker_id"].astype(str)

    # 1. Balls faced: strictly non-wides
    extras_type_clean = d["extras_type"].fillna("").astype(str).str.lower()
    d["is_ball_faced"] = (extras_type_clean != "wide").astype(int)

    # 2. Runs off the bat
    d["batter_runs_calc"] = d["batter_runs"].fillna(0).astype(int)

    # 3. Boundaries
    d["is_four_calc"] = d["is_four"].fillna(False).astype(bool).astype(int)
    d["is_six_calc"] = d["is_six"].fillna(False).astype(bool).astype(int)
    d["boundary_runs_calc"] = d["is_four_calc"] * 4 + d["is_six_calc"] * 6

    # 4. Dot balls faced (ball faced, 0 batter runs, 0 extras)
    extras_runs_val = d["extras_runs"].fillna(0).astype(int)
    d["is_dot_ball_calc"] = (
        (d["is_ball_faced"] == 1) & (d["batter_runs_calc"] == 0) & (extras_runs_val == 0)
    ).astype(int)

    # 5. Singles, Twos, Threes
    d["is_single_calc"] = (d["batter_runs_calc"] == 1).astype(int)
    d["is_two_calc"] = (d["batter_runs_calc"] == 2).astype(int)
    d["is_three_calc"] = (d["batter_runs_calc"] == 3).astype(int)

    # 6. Striker Dismissals
    if "dismissed_player_id" in d.columns:
        dismissed_id_str = (
            d["dismissed_player_id"]
            .astype(str)
            .replace({"<NA>": "", "nan": "", "None": ""})
        )
        is_wicket_bool = d["is_wicket"].fillna(False).astype(bool)
        d["is_striker_dismissed_calc"] = (
            is_wicket_bool & (dismissed_id_str == d["striker_id"])
        ).astype(int)
    else:
        d["is_striker_dismissed_calc"] = 0

    return d


def compute_batting_pressure_metrics(
    deliveries_df: pd.DataFrame,
    group_col: Union[str, List[str]] = "striker_id",
) -> pd.DataFrame:
    """Compute aggregate batting metrics across delivery slices.

    Args:
        deliveries_df: Annotated or raw delivery-level DataFrame.
        group_col: Column or list of columns to group by.

    Returns:
        DataFrame of comprehensive batting metrics.
    """
    if len(deliveries_df) == 0:
        return pd.DataFrame()

    d = annotate_batting_deliveries(deliveries_df)
    group_cols = [group_col] if isinstance(group_col, str) else list(group_col)

    # Delivery-level aggregation
    agg_funcs = {
        "batter_runs_calc": "sum",
        "is_ball_faced": "sum",
        "is_striker_dismissed_calc": "sum",
        "is_four_calc": "sum",
        "is_six_calc": "sum",
        "boundary_runs_calc": "sum",
        "is_dot_ball_calc": "sum",
        "is_single_calc": "sum",
        "is_two_calc": "sum",
        "is_three_calc": "sum",
        "match_id": "nunique",
    }
    # If striker_name is present, keep first
    if "striker_name" in d.columns and "striker_name" not in group_cols:
        agg_funcs["striker_name"] = "first"

    grouped = d.groupby(group_cols, as_index=False).agg(agg_funcs)

    # Rename to canonical fields
    grouped = grouped.rename(
        columns={
            "batter_runs_calc": "total_runs",
            "is_ball_faced": "balls_faced",
            "is_striker_dismissed_calc": "dismissals",
            "is_four_calc": "fours",
            "is_six_calc": "sixes",
            "boundary_runs_calc": "boundary_runs",
            "is_dot_ball_calc": "dot_balls",
            "is_single_calc": "singles",
            "is_two_calc": "twos",
            "is_three_calc": "threes",
            "match_id": "matches_count",
        }
    )

    # Innings count: unique (match_id, innings)
    inn_counts = (
        d.groupby(group_cols + ["match_id", "innings"], as_index=False)
        .size()
        .groupby(group_cols, as_index=False)
        .size()
        .rename(columns={"size": "innings_count"})
    )
    grouped = grouped.merge(inn_counts, on=group_cols, how="left")
    grouped["innings_count"] = grouped["innings_count"].fillna(0).astype(int)

    # Derived Rate Metrics
    bf = grouped["balls_faced"].astype(float)
    runs = grouped["total_runs"].astype(float)
    dism = grouped["dismissals"].astype(float)
    dots = grouped["dot_balls"].astype(float)
    b_runs = grouped["boundary_runs"].astype(float)

    # Strike rate
    grouped["strike_rate"] = np.where(bf > 0, (runs / bf) * 100.0, np.nan)

    # Batting average: preserve NULL / NaN when dismissals == 0
    grouped["batting_average"] = np.where(dism > 0, runs / dism, np.nan)

    # Boundary %
    grouped["boundary_percentage"] = np.where(runs > 0, (b_runs / runs) * 100.0, 0.0)

    # Dot ball %
    grouped["dot_ball_percentage"] = np.where(bf > 0, (dots / bf) * 100.0, 0.0)

    # Scoring delivery %: (balls_faced - dot_balls) / balls_faced
    scoring_balls = np.maximum(bf - dots, 0)
    grouped["scoring_delivery_percentage"] = np.where(bf > 0, (scoring_balls / bf) * 100.0, 0.0)

    # Dismissal metrics
    grouped["dismissal_rate"] = np.where(bf > 0, dism / bf, 0.0)
    grouped["dismissal_percentage"] = grouped["dismissal_rate"] * 100.0
    grouped["balls_per_dismissal"] = np.where(dism > 0, bf / dism, np.nan)

    # Consistency metrics from innings-level aggregation
    cons_df = compute_innings_consistency(d, group_cols)
    grouped = grouped.merge(cons_df, on=group_cols, how="left")

    return grouped


def compute_innings_consistency(
    annotated_df: pd.DataFrame,
    group_cols: List[str],
) -> pd.DataFrame:
    """Compute innings-level batting scoring consistency metrics.

    Evaluates:
    - average_runs_per_innings
    - innings_scoring_consistency (std of innings scores)
    - strike_rate_variability (std of innings strike rates)
    - high_score
    - low_score
    - innings_with_30_plus_runs
    - innings_with_50_plus_runs
    """
    if len(annotated_df) == 0:
        return pd.DataFrame()

    # Aggregate per innings
    inn_group = group_cols + ["match_id", "innings"]
    inn_stats = annotated_df.groupby(inn_group, as_index=False).agg(
        inn_runs=("batter_runs_calc", "sum"),
        inn_balls=("is_ball_faced", "sum"),
    )
    inn_stats["inn_sr"] = np.where(
        inn_stats["inn_balls"] > 0,
        (inn_stats["inn_runs"] / inn_stats["inn_balls"]) * 100.0,
        np.nan,
    )

    # Summarize across innings for each player/group
    consistency_records = []
    for keys, sub in inn_stats.groupby(group_cols):
        key_dict = {col: val for col, val in zip(group_cols, keys if isinstance(keys, tuple) else [keys])}
        scores = sub["inn_runs"].values
        srs = sub["inn_sr"].dropna().values

        high_score = int(np.max(scores)) if len(scores) > 0 else 0
        low_score = int(np.min(scores)) if len(scores) > 0 else 0
        avg_runs_inn = float(np.mean(scores)) if len(scores) > 0 else 0.0
        score_std = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
        sr_std = float(np.std(srs, ddof=1)) if len(srs) > 1 else 0.0
        inn_30 = int(np.sum(scores >= 30))
        inn_50 = int(np.sum(scores >= 50))

        key_dict.update({
            "average_runs_per_innings": round(avg_runs_inn, 2),
            "innings_scoring_consistency": round(score_std, 2),
            "strike_rate_variability": round(sr_std, 2),
            "high_score": high_score,
            "low_score": low_score,
            "innings_with_30_plus_runs": inn_30,
            "innings_with_50_plus_runs": inn_50,
        })
        consistency_records.append(key_dict)

    return pd.DataFrame(consistency_records)
