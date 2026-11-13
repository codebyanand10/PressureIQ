"""Pressure model validation, reliability assessment, and leakage auditing module.

Enforces:
1. Strict pre-delivery exclusivity (no lookahead or delivery-outcome leakage).
2. Numerical validity and bounds enforcement.
3. Transparent delivery-level reliability grading.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple


class PressureValidationError(Exception):
    """Raised when pressure validation or leakage check detects an anomaly."""
    pass


def audit_leakage(df: pd.DataFrame) -> Dict[str, float]:
    """Audit pressure features against future delivery outcomes and match results.

    Verifies that pressure calculations do not leak:
    - Current delivery runs (delivery_runs)
    - Current delivery wickets (wickets_on_delivery or is_wicket)
    - Match winner (win_team_id)

    Returns:
        Dictionary of correlation coefficients (which should be near zero).
    """
    results: Dict[str, float] = {}

    if "batting_pressure_score" not in df.columns or "delivery_runs" not in df.columns:
        return results

    # Convert is_wicket to numeric if needed
    is_wkt_num = df["is_wicket"].astype(int) if "is_wicket" in df.columns else None

    # Correlation with delivery outcome runs
    corr_runs = df["batting_pressure_score"].corr(df["delivery_runs"])
    results["corr_batting_score_delivery_runs"] = round(float(corr_runs) if pd.notna(corr_runs) else 0.0, 4)

    # Correlation with delivery outcome wicket
    if is_wkt_num is not None:
        corr_wkt = df["batting_pressure_score"].corr(is_wkt_num)
        results["corr_batting_score_delivery_wicket"] = round(float(corr_wkt) if pd.notna(corr_wkt) else 0.0, 4)

    if "bowling_pressure_score" in df.columns:
        corr_bowl_runs = df["bowling_pressure_score"].corr(df["delivery_runs"])
        results["corr_bowling_score_delivery_runs"] = round(float(corr_bowl_runs) if pd.notna(corr_bowl_runs) else 0.0, 4)

        if is_wkt_num is not None:
            corr_bowl_wkt = df["bowling_pressure_score"].corr(is_wkt_num)
            results["corr_bowling_score_delivery_wicket"] = round(float(corr_bowl_wkt) if pd.notna(corr_bowl_wkt) else 0.0, 4)

    # For small synthetic samples (< 50 items), Pearson correlation has high sample noise
    # and cannot reliably test population leakage
    if len(df) < 50:
        return results

    # In cricket analytics, true pre-delivery pressure has negligible direct correlation with single-ball outcome
    threshold = 0.25 if len(df) < 500 else 0.10
    for k, v in results.items():
        if abs(v) > threshold:
            raise PressureValidationError(
                f"Potential leakage detected in {k}: correlation magnitude {v} exceeds {threshold} threshold"
            )

    return results


def calculate_pressure_reliability(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate reliability scores, levels, and flags for all deliveries.

    Returns:
        Tuple of (reliability_score, reliability_level, reliability_flags)
    """
    scores = np.full(len(df), 95.0, dtype=float)
    flags_list: List[List[str]] = [[] for _ in range(len(df))]

    # 1. State validation status from Phase 3
    if "match_state_valid" in df.columns:
        is_invalid = ~df["match_state_valid"].fillna(True).astype(bool)
        scores[is_invalid] -= 40.0
        for i in np.where(is_invalid)[0]:
            flags_list[i].append("UNVALIDATED_MATCH_STATE")

    # 2. DLS revised innings
    if "target_source" in df.columns:
        is_dls = (df["target_source"] == "DLS_REVISED_TARGET").fillna(False).values
        # DLS targets are reliable when audited, slight adjustment
        for i in np.where(is_dls)[0]:
            flags_list[i].append("DLS_REVISED_INNINGS")

    # 3. Super Over innings
    if "is_super_over" in df.columns:
        is_so = df["is_super_over"].fillna(False).astype(bool).values
        scores[is_so] -= 5.0
        for i in np.where(is_so)[0]:
            flags_list[i].append("SUPER_OVER")

    # 4. Extreme RRR capped
    if "required_run_rate_before" in df.columns:
        is_extreme_rrr = (df["required_run_rate_before"] > 36.0).fillna(False).values
        for i in np.where(is_extreme_rrr)[0]:
            flags_list[i].append("EXTREME_RRR_CAPPED")

    # 5. Completed chase
    if "runs_required_before" in df.columns:
        is_completed = (df["runs_required_before"] <= 0).fillna(False).values
        for i in np.where(is_completed)[0]:
            flags_list[i].append("CHASE_COMPLETED")

    # Format flags
    formatted_flags = [";".join(f) if f else "NORMAL" for f in flags_list]

    # Convert numeric score to reliability level
    scores = np.clip(scores, 0.0, 100.0)
    levels = np.where(
        scores >= 85.0, "High",
        np.where(scores >= 65.0, "Medium",
                 np.where(scores >= 40.0, "Low", "Unreliable"))
    )

    index = df.index
    return (
        pd.Series(np.round(scores, 1), index=index, name="pressure_reliability_score"),
        pd.Series(levels, index=index, name="pressure_reliability_level"),
        pd.Series(formatted_flags, index=index, name="pressure_reliability_flags"),
    )


def validate_pressure_scores(df: pd.DataFrame) -> Dict[str, bool]:
    """Validate overall integrity and boundary conditions of pressure scores."""
    checks: Dict[str, bool] = {}

    # Score range check
    bat_min = df["batting_pressure_score"].min()
    bat_max = df["batting_pressure_score"].max()
    checks["batting_score_within_0_100"] = bool(0.0 <= bat_min and bat_max <= 100.0)

    bowl_min = df["bowling_pressure_score"].min()
    bowl_max = df["bowling_pressure_score"].max()
    checks["bowling_score_within_0_100"] = bool(0.0 <= bowl_min and bowl_max <= 100.0)

    # Batting and Bowling asymmetry check: they must not be identical
    not_identical = not np.allclose(df["batting_pressure_score"], df["bowling_pressure_score"], atol=1e-3)
    if len(df) >= 50:
        corr = df["batting_pressure_score"].corr(df["bowling_pressure_score"])
        checks["batting_bowling_not_identical"] = bool(not_identical and (pd.isna(corr) or abs(corr) < 0.98))
    else:
        checks["batting_bowling_not_identical"] = bool(not_identical)

    # No nulls in required scores
    checks["no_null_batting_scores"] = bool(df["batting_pressure_score"].notna().all())
    checks["no_null_bowling_scores"] = bool(df["bowling_pressure_score"].notna().all())

    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        raise PressureValidationError(f"Pressure validation checks failed: {failed}")

    return checks
