"""Bowling performance metrics computation module under pressure conditions.

Calculates:
1. Basic metrics: matches bowled, innings bowled, legal balls, overs, runs conceded,
   wickets credited, economy rate, bowling average, bowling strike rate.
2. Run control: dot balls, dot ball %, fours/sixes conceded, boundary runs conceded,
   boundary % conceded, scoring delivery percentage.
3. Wicket taking: wickets per legal ball, wickets per over.
4. Consistency: economy rate variability, dot ball consistency, wicket consistency across innings.
"""

from __future__ import annotations

import logging
from typing import List, Union
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

BOWLER_CREDITED_DISMISSALS = {
    "Bowled",
    "Caught",
    "LBW",
    "Stumped",
    "Hit Wicket",
}

BOWLER_CHARGED_EXTRAS = {
    "wide",
    "Overstep",
    "other",
}


def annotate_bowling_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """Add vectorized boolean and metric flags to delivery events for bowling analysis.

    Strict cricket rules enforced:
    - Legal balls: strictly deliveries where is_legal_delivery == True.
    - Bowler runs: batter runs + bowler extras (wides, oversteps, other no-balls).
      Byes and leg-byes are strictly EXCLUDED.
    - Bowler wickets: strictly Bowled, Caught, LBW, Stumped, Hit Wicket.
      Run outs, retired out, etc., are strictly EXCLUDED.
    - Dot balls: legal delivery with 0 batter runs and 0 extras.
    """
    d = df.copy()
    d["bowler_id"] = d["bowler_id"].astype(str)

    # 1. Legal deliveries
    d["is_legal_calc"] = d["is_legal_delivery"].fillna(False).astype(bool).astype(int)
    d["is_ball_calc"] = 1

    # 2. Runs conceded: batter runs + bowler extras (byes and leg-byes excluded)
    batter_runs = d["batter_runs"].fillna(0).astype(int)
    extras_type_clean = d["extras_type"].fillna("").astype(str)
    is_bowler_extra = extras_type_clean.isin(BOWLER_CHARGED_EXTRAS)
    bowler_extra_runs = np.where(is_bowler_extra, d["extras_runs"].fillna(0).astype(int), 0)
    d["bowler_runs_calc"] = batter_runs + bowler_extra_runs

    # 3. Bowler credited wickets
    is_wkt = d["is_wicket"].fillna(False).astype(bool) if "is_wicket" in d.columns else pd.Series(False, index=d.index)
    dism_col = "dismissal_type" if "dismissal_type" in d.columns else ("wicket_type" if "wicket_type" in d.columns else None)
    dism_type = d[dism_col].fillna("").astype(str) if dism_col else pd.Series("", index=d.index)
    d["is_bowler_wicket_calc"] = (is_wkt & dism_type.isin(BOWLER_CREDITED_DISMISSALS)).astype(int)
    d["is_any_wicket_calc"] = is_wkt.astype(int)

    # 4. Dot balls conceded (legal delivery, 0 batter runs, 0 extras)
    extras_total = d["extras_runs"].fillna(0).astype(int) if "extras_runs" in d.columns else pd.Series(0, index=d.index)
    d["is_dot_ball_calc"] = (
        (d["is_legal_calc"] == 1) & (batter_runs == 0) & (extras_total == 0)
    ).astype(int)

    # 5. Boundaries conceded
    d["is_four_calc"] = (d["is_four"].fillna(False).astype(bool) if "is_four" in d.columns else (batter_runs == 4)).astype(int)
    d["is_six_calc"] = (d["is_six"].fillna(False).astype(bool) if "is_six" in d.columns else (batter_runs == 6)).astype(int)
    d["boundary_runs_calc"] = d["is_four_calc"] * 4 + d["is_six_calc"] * 6

    # 6. Singles, Twos, Threes conceded off bat
    d["is_single_calc"] = (batter_runs == 1).astype(int)
    d["is_two_calc"] = (batter_runs == 2).astype(int)
    d["is_three_calc"] = (batter_runs == 3).astype(int)

    return d


def compute_bowling_pressure_metrics(
    deliveries_df: pd.DataFrame,
    group_col: Union[str, List[str]] = "bowler_id",
) -> pd.DataFrame:
    """Compute aggregate bowling metrics across delivery slices.

    Args:
        deliveries_df: Delivery-level DataFrame containing bowling events.
        group_col: Column or list of columns to group by.

    Returns:
        DataFrame of comprehensive bowling metrics.
    """
    if len(deliveries_df) == 0:
        return pd.DataFrame()

    d = annotate_bowling_deliveries(deliveries_df)
    group_cols = [group_col] if isinstance(group_col, str) else list(group_col)

    # Delivery-level aggregation
    agg_funcs = {
        "is_legal_calc": "sum",
        "is_ball_calc": "sum",
        "bowler_runs_calc": "sum",
        "is_bowler_wicket_calc": "sum",
        "is_any_wicket_calc": "sum",
        "is_dot_ball_calc": "sum",
        "is_four_calc": "sum",
        "is_six_calc": "sum",
        "boundary_runs_calc": "sum",
        "is_single_calc": "sum",
        "is_two_calc": "sum",
        "is_three_calc": "sum",
        "match_id": "nunique",
    }
    if "bowler_name" in d.columns and "bowler_name" not in group_cols:
        agg_funcs["bowler_name"] = "first"

    grouped = d.groupby(group_cols, as_index=False).agg(agg_funcs)

    grouped = grouped.rename(
        columns={
            "is_legal_calc": "legal_balls_bowled",
            "is_ball_calc": "total_balls_bowled",
            "bowler_runs_calc": "runs_conceded",
            "is_bowler_wicket_calc": "wickets_credited",
            "is_any_wicket_calc": "total_wickets_in_over",
            "is_dot_ball_calc": "dot_balls",
            "is_four_calc": "fours_conceded",
            "is_six_calc": "sixes_conceded",
            "boundary_runs_calc": "boundary_runs_conceded",
            "is_single_calc": "singles_conceded",
            "is_two_calc": "twos_conceded",
            "is_three_calc": "threes_conceded",
            "match_id": "matches_bowled",
        }
    )

    # Innings count: unique (match_id, innings)
    inn_counts = (
        d.groupby(group_cols + ["match_id", "innings"], as_index=False)
        .size()
        .groupby(group_cols, as_index=False)
        .size()
        .rename(columns={"size": "innings_bowled"})
    )
    grouped = grouped.merge(inn_counts, on=group_cols, how="left")
    grouped["innings_bowled"] = grouped["innings_bowled"].fillna(0).astype(int)

    # Overs bowled
    lb = grouped["legal_balls_bowled"].astype(float)
    runs = grouped["runs_conceded"].astype(float)
    wkts = grouped["wickets_credited"].astype(float)
    dots = grouped["dot_balls"].astype(float)
    b_runs = grouped["boundary_runs_conceded"].astype(float)

    grouped["overs_bowled"] = (lb / 6.0).round(1)

    # Economy rate: (runs * 6) / legal_balls
    grouped["economy_rate"] = np.where(lb > 0, (runs * 6.0) / lb, np.nan)

    # Bowling average: runs / wickets (NaN when 0 wickets)
    grouped["bowling_average"] = np.where(wkts > 0, runs / wkts, np.nan)

    # Bowling strike rate: legal_balls / wickets (NaN when 0 wickets)
    grouped["bowling_strike_rate"] = np.where(wkts > 0, lb / wkts, np.nan)

    # Dot-ball %: (dot_balls / legal_balls) * 100
    grouped["dot_ball_percentage"] = np.where(lb > 0, (dots / lb) * 100.0, 0.0)

    # Boundaries conceded: fours + sixes
    grouped["boundaries_conceded"] = grouped["fours_conceded"] + grouped["sixes_conceded"]

    # Boundary % conceded: (boundary_runs / runs_conceded) * 100
    grouped["boundary_percentage_conceded"] = np.where(runs > 0, (b_runs / runs) * 100.0, 0.0)

    # Scoring delivery % conceded: (legal_balls - dot_balls) / legal_balls
    scoring_balls = np.maximum(lb - dots, 0)
    grouped["scoring_delivery_percentage"] = np.where(lb > 0, (scoring_balls / lb) * 100.0, 0.0)

    # Wickets per legal ball & per over
    grouped["wickets_per_legal_ball"] = np.where(lb > 0, wkts / lb, 0.0)
    grouped["wickets_per_over"] = grouped["wickets_per_legal_ball"] * 6.0

    # Consistency across innings
    cons_df = compute_bowling_innings_consistency(d, group_cols)
    grouped = grouped.merge(cons_df, on=group_cols, how="left")

    return grouped


def compute_bowling_innings_consistency(
    annotated_df: pd.DataFrame,
    group_cols: List[str],
) -> pd.DataFrame:
    """Compute spell-level and innings-level bowling consistency metrics.

    Evaluates:
    - economy_rate_variability (std of economy per innings)
    - dot_ball_consistency (std of dot-ball % per innings)
    - wicket_taking_consistency (std of wickets per innings)
    - average_runs_conceded_per_innings
    """
    if len(annotated_df) == 0:
        return pd.DataFrame()

    inn_group = group_cols + ["match_id", "innings"]
    inn_stats = annotated_df.groupby(inn_group, as_index=False).agg(
        inn_runs=("bowler_runs_calc", "sum"),
        inn_balls=("is_legal_calc", "sum"),
        inn_dots=("is_dot_ball_calc", "sum"),
        inn_wkts=("is_bowler_wicket_calc", "sum"),
    )
    inn_stats["inn_econ"] = np.where(
        inn_stats["inn_balls"] > 0,
        (inn_stats["inn_runs"] * 6.0) / inn_stats["inn_balls"],
        np.nan,
    )
    inn_stats["inn_dot_pct"] = np.where(
        inn_stats["inn_balls"] > 0,
        (inn_stats["inn_dots"] / inn_stats["inn_balls"]) * 100.0,
        np.nan,
    )

    records = []
    for keys, sub in inn_stats.groupby(group_cols):
        key_dict = {col: val for col, val in zip(group_cols, keys if isinstance(keys, tuple) else [keys])}
        runs = sub["inn_runs"].values
        econs = sub["inn_econ"].dropna().values
        dots = sub["inn_dot_pct"].dropna().values
        wkts = sub["inn_wkts"].values

        econ_std = float(np.std(econs, ddof=1)) if len(econs) > 1 else 0.0
        dot_std = float(np.std(dots, ddof=1)) if len(dots) > 1 else 0.0
        wkt_std = float(np.std(wkts, ddof=1)) if len(wkts) > 1 else 0.0
        avg_runs = float(np.mean(runs)) if len(runs) > 0 else 0.0

        key_dict.update({
            "economy_rate_variability": round(econ_std, 2),
            "dot_ball_consistency": round(dot_std, 2),
            "wicket_taking_consistency": round(wkt_std, 2),
            "average_runs_conceded_per_innings": round(avg_runs, 2),
        })
        records.append(key_dict)

    return pd.DataFrame(records)
