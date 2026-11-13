"""PressureIQ - Target Score & Sourcing Calculator.

Determines chase targets for second innings and super overs, distinguishing
DLS rain-revised targets from standard cumulative first-innings targets.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from src.logger import get_logger

logger = get_logger("PressureIQ.MatchState.TargetCalculator")


def calculate_targets(
    bbb_df: pd.DataFrame,
    matches_df: pd.DataFrame,
) -> Dict[Tuple[int, int], Tuple[Optional[float], str]]:
    """Determine target score and target source for every match innings.

    Args:
        bbb_df: Processed delivery records.
        matches_df: Cleaned matches metadata with DLS fields.

    Returns:
        Dictionary mapping (match_id, innings) to (target_score, target_source).
    """
    logger.info("Calculating innings target scores and target sources...")
    targets_map: Dict[Tuple[int, int], Tuple[Optional[float], str]] = {}

    # Compute actual innings total runs from delivery events
    # total runs = sum(runs + extras1_runs + extras_2_runs)
    delivery_runs = bbb_df["runs"].fillna(0) + bbb_df["extras1_runs"].fillna(0) + bbb_df["extras_2_runs"].fillna(0)
    inn_totals = (
        bbb_df.assign(_tot=delivery_runs)
        .groupby(["match_id", "innings"])["_tot"]
        .sum()
        .to_dict()
    )

    matches_lookup = matches_df.set_index("match_id").to_dict(orient="index")
    all_innings = bbb_df[["match_id", "innings"]].drop_duplicates()

    for row in all_innings.itertuples():
        m_id = row.match_id
        inn = row.innings
        m_info = matches_lookup.get(m_id, {})

        # First innings (Innings 1 or 3) has no target to chase
        if inn in [1, 3]:
            targets_map[(m_id, inn)] = (None, "NOT_APPLICABLE_FIRST_INNINGS")
            continue

        # Second innings (Innings 2):
        if inn == 2:
            # Check for DLS revised target in match metadata
            rev_target = m_info.get("revised_target")
            if pd.notna(rev_target) and float(rev_target) > 0:
                targets_map[(m_id, inn)] = (float(rev_target), "DLS_REVISED_TARGET")
                continue

            # Standard chase: First innings total + 1
            inn1_tot = inn_totals.get((m_id, 1))
            if inn1_tot is not None and not np.isnan(inn1_tot):
                targets_map[(m_id, inn)] = (float(inn1_tot + 1), "FIRST_INNINGS_TOTAL")
                continue

            # Unavailable target
            targets_map[(m_id, inn)] = (None, "UNAVAILABLE")
            continue

        # Super Over chase (Innings 4):
        if inn == 4:
            inn3_tot = inn_totals.get((m_id, 3))
            if inn3_tot is not None and not np.isnan(inn3_tot):
                targets_map[(m_id, inn)] = (float(inn3_tot + 1), "SUPER_OVER_TARGET")
            else:
                targets_map[(m_id, inn)] = (None, "UNAVAILABLE")
            continue

        # Default fallback
        targets_map[(m_id, inn)] = (None, "UNAVAILABLE")

    target_counts = pd.Series([src for _, src in targets_map.values()]).value_counts().to_dict()
    logger.info(f"Target calculation complete. Sources breakdown: {target_counts}")
    return targets_map

