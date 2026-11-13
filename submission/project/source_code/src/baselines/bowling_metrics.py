"""Bowling performance metrics computation module.

Calculates verified bowling statistics:
- Basic: innings, matches, legal balls, overs, runs conceded, wickets credited, average, economy, strike rate
- Bowling behaviour: dot balls, dot ball %, boundaries conceded, fours/sixes conceded, boundary % conceded
- Excludes byes/leg-byes from bowler runs and excludes run outs from bowler wickets.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

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


def compute_bowling_metrics(
    df: pd.DataFrame,
    group_col: str = "bowler_id",
) -> pd.DataFrame:
    """Compute comprehensive bowling metrics aggregated by player (or player + context).

    Args:
        df: Delivery-level DataFrame containing bowling events.
        group_col: Primary grouping column or list of columns.

    Returns:
        DataFrame with aggregated bowling statistics.
    """
    if len(df) == 0:
        return pd.DataFrame()

    d = df.copy()
    d["bowler_id"] = d["bowler_id"].astype(str)

    # 1. Legal balls bowled
    d["is_legal_calc"] = d["is_legal_delivery"].fillna(False).astype(bool).astype(int)

    # 2. Runs conceded by the bowler: batter runs + bowler extras (wides, oversteps, other no-balls)
    # Byes and leg-byes are EXCLUDED from bowler conceded runs
    batter_runs = d["batter_runs"].fillna(0).astype(int)
    is_bowler_extra = d["extras_type"].isin(BOWLER_CHARGED_EXTRAS)
    extras_runs = np.where(is_bowler_extra, d["extras_runs"].fillna(0).astype(int), 0)
    d["bowler_runs_conceded"] = batter_runs + extras_runs

    # 3. Bowler credited wickets (excluding run outs, retired out, etc.)
    d["is_bowler_wicket"] = (
        (d["is_wicket"].fillna(False).astype(bool))
        & (d["dismissal_type"].isin(BOWLER_CREDITED_DISMISSALS))
    ).astype(int)

    # 4. Dot balls (0 total delivery runs on the ball)
    d["is_dot_ball_conceded"] = (d["delivery_runs"].fillna(0) == 0).astype(int)

    # 5. Boundaries conceded
    d["is_four_conceded"] = d["is_four"].fillna(False).astype(bool).astype(int)
    d["is_six_conceded"] = d["is_six"].fillna(False).astype(bool).astype(int)

    # Grouping
    groups = [group_col] if isinstance(group_col, str) else list(group_col)

    # Innings bowled
    innings_df = (
        d.groupby(groups + ["match_id", "innings"], as_index=False)
        .size()
        .groupby(groups, as_index=False)
        .agg(innings_bowled=("innings", "count"))
    )

    # Matches bowled
    matches_df = (
        d.groupby(groups + ["match_id"], as_index=False)
        .size()
        .groupby(groups, as_index=False)
        .agg(matches_bowled=("match_id", "count"))
    )

    agg_df = d.groupby(groups, as_index=False).agg(
        total_deliveries=("delivery_sequence", "count"),
        legal_balls_bowled=("is_legal_calc", "sum"),
        runs_conceded=("bowler_runs_conceded", "sum"),
        wickets_credited=("is_bowler_wicket", "sum"),
        dot_balls=("is_dot_ball_conceded", "sum"),
        fours_conceded=("is_four_conceded", "sum"),
        sixes_conceded=("is_six_conceded", "sum"),
    )

    m = agg_df.merge(innings_df, on=groups, how="left").merge(matches_df, on=groups, how="left")
    m["innings_bowled"] = m["innings_bowled"].fillna(0).astype(int)
    m["matches_bowled"] = m["matches_bowled"].fillna(0).astype(int)

    # Overs bowled
    m["overs_bowled"] = np.round(m["legal_balls_bowled"] / 6.0, 2)

    # Economy Rate: (runs * 6) / legal_balls
    m["economy_rate"] = np.where(
        m["legal_balls_bowled"] > 0,
        np.round((m["runs_conceded"] * 6.0) / m["legal_balls_bowled"], 2),
        0.0,
    )

    # Bowling Average: runs / wickets (NaN if 0 wickets)
    m["bowling_average"] = np.where(
        m["wickets_credited"] > 0,
        np.round(m["runs_conceded"] / m["wickets_credited"], 2),
        np.nan,
    )

    # Bowling Strike Rate: legal_balls / wickets (NaN if 0 wickets)
    m["bowling_strike_rate"] = np.where(
        m["wickets_credited"] > 0,
        np.round(m["legal_balls_bowled"] / m["wickets_credited"], 2),
        np.nan,
    )

    # Dot ball %
    m["dot_ball_percentage"] = np.where(
        m["legal_balls_bowled"] > 0,
        np.round((m["dot_balls"] / m["legal_balls_bowled"]) * 100.0, 2),
        0.0,
    )

    # Boundaries conceded
    m["boundaries_conceded"] = m["fours_conceded"] + m["sixes_conceded"]
    m["boundary_percentage_conceded"] = np.where(
        m["legal_balls_bowled"] > 0,
        np.round((m["boundaries_conceded"] / m["legal_balls_bowled"]) * 100.0, 2),
        0.0,
    )

    # Wickets per legal ball
    m["wickets_per_legal_ball"] = np.where(
        m["legal_balls_bowled"] > 0,
        np.round(m["wickets_credited"] / m["legal_balls_bowled"], 4),
        0.0,
    )

    return m

