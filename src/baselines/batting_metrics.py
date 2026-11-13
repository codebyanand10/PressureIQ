"""Batting performance metrics computation module.

Calculates verified batting statistics:
- Basic: innings, runs, balls faced, not outs, dismissals, average, strike rate
- Scoring behaviour: boundaries, dot balls, singles/twos/threes, scoring delivery %
- Dismissal behaviour: balls per dismissal, dismissal rate
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_batting_metrics(
    df: pd.DataFrame,
    group_col: str = "striker_id",
) -> pd.DataFrame:
    """Compute comprehensive batting metrics aggregated by player (or player + context).

    Args:
        df: Delivery-level DataFrame containing batting events.
        group_col: Primary grouping column or list of columns.

    Returns:
        DataFrame with aggregated batting statistics.
    """
    if len(df) == 0:
        return pd.DataFrame()

    d = df.copy()
    d["striker_id"] = d["striker_id"].astype(str)

    # 1. Balls faced: strictly deliveries where extras_type != 'wide'
    d["is_ball_faced"] = (d["extras_type"] != "wide").astype(int)

    # 2. Runs off the bat
    d["batter_runs_calc"] = d["batter_runs"].fillna(0).astype(int)

    # 3. Boundaries
    d["is_four_calc"] = d["is_four"].fillna(False).astype(bool).astype(int)
    d["is_six_calc"] = d["is_six"].fillna(False).astype(bool).astype(int)

    # 4. Dot balls faced (0 batter runs, 0 extras, not a wide)
    d["is_dot_ball"] = (
        (d["is_ball_faced"] == 1) & (d["batter_runs_calc"] == 0) & (d["extras_runs"].fillna(0) == 0)
    ).astype(int)

    # 5. Singles, Twos, Threes
    d["is_single"] = (d["batter_runs_calc"] == 1).astype(int)
    d["is_two"] = (d["batter_runs_calc"] == 2).astype(int)
    d["is_three"] = (d["batter_runs_calc"] == 3).astype(int)

    # 6. Dismissals: wicket occurred where dismissed_player_id == striker_id
    if "dismissed_player_id" in d.columns:
        d["is_striker_dismissed"] = (
            (d["is_wicket"].fillna(False).astype(bool))
            & (d["dismissed_player_id"].astype(str) == d["striker_id"])
        ).astype(int)
    else:
        d["is_striker_dismissed"] = d["is_wicket"].fillna(False).astype(bool).astype(int)

    # Aggregations
    groups = [group_col] if isinstance(group_col, str) else list(group_col)

    # Unique innings per group
    innings_df = (
        d.groupby(groups + ["match_id", "innings"], as_index=False)
        .size()
        .groupby(groups, as_index=False)
        .agg(innings_batted=("innings", "count"))
    )

    # Unique matches per group
    matches_df = (
        d.groupby(groups + ["match_id"], as_index=False)
        .size()
        .groupby(groups, as_index=False)
        .agg(matches_batted=("match_id", "count"))
    )

    agg_df = d.groupby(groups, as_index=False).agg(
        total_deliveries=("delivery_sequence", "count"),
        total_runs=("batter_runs_calc", "sum"),
        total_balls_faced=("is_ball_faced", "sum"),
        dismissals=("is_striker_dismissed", "sum"),
        fours=("is_four_calc", "sum"),
        sixes=("is_six_calc", "sum"),
        dot_balls=("is_dot_ball", "sum"),
        singles=("is_single", "sum"),
        twos=("is_two", "sum"),
        threes=("is_three", "sum"),
    )

    # Merge innings and matches
    m = agg_df.merge(innings_df, on=groups, how="left").merge(matches_df, on=groups, how="left")
    m["innings_batted"] = m["innings_batted"].fillna(0).astype(int)
    m["matches_batted"] = m["matches_batted"].fillna(0).astype(int)

    # Derived calculations
    m["not_outs"] = np.maximum(m["innings_batted"] - m["dismissals"], 0)

    # Batting Average: runs / dismissals (NaN when dismissals == 0)
    m["batting_average"] = np.where(
        m["dismissals"] > 0,
        np.round(m["total_runs"] / m["dismissals"], 2),
        np.nan,
    )

    # Strike Rate: (runs / balls_faced) * 100
    m["strike_rate"] = np.where(
        m["total_balls_faced"] > 0,
        np.round((m["total_runs"] / m["total_balls_faced"]) * 100.0, 2),
        0.0,
    )

    # Boundaries
    m["boundary_runs"] = m["fours"] * 4 + m["sixes"] * 6
    m["boundary_percentage"] = np.where(
        m["total_runs"] > 0,
        np.round((m["boundary_runs"] / m["total_runs"]) * 100.0, 2),
        0.0,
    )

    # Dot ball %
    m["dot_ball_percentage"] = np.where(
        m["total_balls_faced"] > 0,
        np.round((m["dot_balls"] / m["total_balls_faced"]) * 100.0, 2),
        0.0,
    )

    # Scoring delivery %: (balls_faced - dot_balls) / balls_faced
    scoring_balls = np.maximum(m["total_balls_faced"] - m["dot_balls"], 0)
    m["scoring_delivery_percentage"] = np.where(
        m["total_balls_faced"] > 0,
        np.round((scoring_balls / m["total_balls_faced"]) * 100.0, 2),
        0.0,
    )

    # Dismissal behaviour
    m["dismissal_rate"] = np.where(
        m["total_balls_faced"] > 0,
        np.round(m["dismissals"] / m["total_balls_faced"], 4),
        0.0,
    )
    m["balls_per_dismissal"] = np.where(
        m["dismissals"] > 0,
        np.round(m["total_balls_faced"] / m["dismissals"], 2),
        np.nan,
    )

    return m

