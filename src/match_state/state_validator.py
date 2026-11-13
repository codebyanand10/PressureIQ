"""PressureIQ - Match State Diagnostic & Constraint Validator.

Validates reconstructed delivery match states against fundamental cricket
domain rules, mathematical monotonicity constraints, and quota bounds.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from src.logger import get_logger

logger = get_logger("PressureIQ.MatchState.StateValidator")


def validate_match_states(
    states_df: pd.DataFrame,
    max_wickets: int = 10,
    max_super_over_wickets: int = 2,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Execute comprehensive rule-based validation on reconstructed match states.

    Args:
        states_df: Reconstructed match state DataFrame.
        max_wickets: Maximum allowable wickets in standard innings (10).
        max_super_over_wickets: Maximum allowable wickets in Super Over (2).

    Returns:
        Tuple of:
        - Updated states_df with 'match_state_valid' and 'validation_flags'
        - Validation audit report DataFrame
        - Summary metrics dictionary
    """
    logger.info("Executing match state constraint validation...")
    df = states_df.copy()

    # Individual check masks
    neg_runs = (df["runs_before"] < 0) | (df["runs_after"] < 0)
    neg_wickets = (df["wickets_before"] < 0) | (df["wickets_after"] < 0)

    # Wickets cap
    so_mask = df["is_super_over"]
    excess_wickets = np.where(
        so_mask,
        df["wickets_after"] > max_super_over_wickets,
        df["wickets_after"] > max_wickets,
    )

    # Ball quota checks
    neg_balls_rem = (df["legal_balls_remaining_before"] < 0) | (df["legal_balls_remaining_after"] < 0)
    excess_balls_bowled = df["legal_balls_bowled_after"] > df["available_legal_balls"]

    # Monotonicity checks
    runs_decreased = df["runs_after"] < df["runs_before"]
    wickets_decreased = df["wickets_after"] < df["wickets_before"]
    balls_decreased = df["legal_balls_bowled_after"] < df["legal_balls_bowled_before"]

    # Team collision check
    same_team = df["batting_team_id"] == df["bowling_team_id"]

    # Target validity in chasing innings
    missing_target = df["is_chasing_innings"] & df["target_score"].isna()

    # Impossible run rate checks
    neg_crr = (df["current_run_rate_before"] < 0) | (df["current_run_rate_after"] < 0)
    neg_rrr = (df["required_run_rate_before"] < 0) | (df["required_run_rate_after"] < 0)

    # Compile validation flags per row
    flags_list = []
    for idx in range(len(df)):
        row_flags = []
        if neg_runs.iloc[idx]:
            row_flags.append("NEGATIVE_RUNS")
        if neg_wickets.iloc[idx]:
            row_flags.append("NEGATIVE_WICKETS")
        if excess_wickets[idx]:
            row_flags.append("EXCESS_WICKETS")
        if neg_balls_rem.iloc[idx]:
            row_flags.append("NEGATIVE_BALLS_REMAINING")
        if excess_balls_bowled.iloc[idx]:
            row_flags.append("EXCESS_LEGAL_BALLS")
        if runs_decreased.iloc[idx]:
            row_flags.append("RUNS_DECREASED")
        if wickets_decreased.iloc[idx]:
            row_flags.append("WICKETS_DECREASED")
        if balls_decreased.iloc[idx]:
            row_flags.append("BALLS_DECREASED")
        if same_team.iloc[idx]:
            row_flags.append("IDENTICAL_TEAMS")
        if missing_target.iloc[idx]:
            row_flags.append("MISSING_TARGET_IN_CHASE")
        if neg_crr.iloc[idx] or neg_rrr.iloc[idx]:
            row_flags.append("NEGATIVE_RUN_RATE")

        flags_list.append("; ".join(row_flags) if row_flags else "VALID")

    df["validation_flags"] = flags_list
    df["match_state_valid"] = df["validation_flags"] == "VALID"
    df["reconstruction_notes"] = np.where(
        df["match_state_valid"],
        "State reconstructed and verified compliant.",
        df["validation_flags"],
    )

    # Create summary report
    checks = [
        ("Negative Runs", int(neg_runs.sum()), "Innings runs must be >= 0"),
        ("Negative Wickets", int(neg_wickets.sum()), "Wickets lost must be >= 0"),
        ("Excess Wickets (>10 or >2 SO)", int(excess_wickets.sum()), "Wickets cannot exceed available batters"),
        ("Negative Balls Remaining", int(neg_balls_rem.sum()), "Balls remaining cannot be negative"),
        ("Excess Legal Balls Bowled", int(excess_balls_bowled.sum()), "Legal balls cannot exceed allocated quota"),
        ("Runs Decreased Unexpectedly", int(runs_decreased.sum()), "Cumulative runs must be non-decreasing"),
        ("Wickets Decreased Unexpectedly", int(wickets_decreased.sum()), "Cumulative wickets must be non-decreasing"),
        ("Legal Balls Decreased", int(balls_decreased.sum()), "Cumulative legal balls must be non-decreasing"),
        ("Batting Team == Bowling Team", int(same_team.sum()), "Participating teams must be distinct"),
        ("Missing Target in Chase", int(missing_target.sum()), "Second innings chase must have target"),
        ("Negative Run Rate", int((neg_crr | neg_rrr).sum()), "Run rates cannot be negative"),
    ]

    report_df = pd.DataFrame(
        [
            {
                "constraint_name": name,
                "violation_count": count,
                "violation_pct": round((count / len(df)) * 100, 4),
                "status": "PASSED" if count == 0 else "FLAGGED",
                "rule_description": desc,
            }
            for name, count, desc in checks
        ]
    )

    summary = {
        "total_deliveries": len(df),
        "valid_deliveries_count": int(df["match_state_valid"].sum()),
        "invalid_deliveries_count": int((~df["match_state_valid"]).sum()),
        "validity_pct": round((df["match_state_valid"].sum() / len(df)) * 100, 3),
        "total_violations": sum(count for _, count, _ in checks),
    }

    logger.info(
        f"Validation complete: {summary['valid_deliveries_count']:,} of {summary['total_deliveries']:,} "
        f"deliveries 100% valid ({summary['validity_pct']}%)."
    )
    return df, report_df, summary

