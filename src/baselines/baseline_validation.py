"""Baseline validation and integrity enforcement module.

Verifies:
- Mathematical correctness of averages, strike rates, and economies
- Non-negativity of counting metrics
- Clean handling of zero-dismissal and zero-wicket edge cases
- Referential consistency across baseline tables
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class BaselineValidationError(Exception):
    """Raised when baseline data integrity validation fails."""
    pass


def validate_baselines(
    batting_overall_df: pd.DataFrame,
    bowling_overall_df: pd.DataFrame,
    batting_lp_df: Optional[pd.DataFrame] = None,
    bowling_lp_df: Optional[pd.DataFrame] = None,
) -> Dict[str, bool]:
    """Execute mathematical and structural validation on baseline datasets.

    Returns:
        Dictionary of validation check names and Boolean pass statuses.
    """
    logger.info("Executing baseline validation checks...")
    checks: Dict[str, bool] = {}

    # 1. Batting Non-Negativity Checks
    checks["batting_runs_non_negative"] = bool((batting_overall_df["total_runs"] >= 0).all())
    checks["batting_balls_non_negative"] = bool((batting_overall_df["total_balls_faced"] >= 0).all())
    checks["batting_dismissals_non_negative"] = bool((batting_overall_df["dismissals"] >= 0).all())

    # 2. Batting Formula Consistency
    # Strike rate formula check
    valid_sr_mask = batting_overall_df["total_balls_faced"] > 0
    sub_sr = batting_overall_df[valid_sr_mask]
    calc_sr = np.round((sub_sr["total_runs"] / sub_sr["total_balls_faced"]) * 100.0, 2)
    checks["batting_strike_rate_formula_consistent"] = bool(np.allclose(sub_sr["strike_rate"], calc_sr, atol=0.05))

    # Average formula check (where dismissals > 0)
    valid_avg_mask = batting_overall_df["dismissals"] > 0
    sub_avg = batting_overall_df[valid_avg_mask]
    calc_avg = np.round(sub_avg["total_runs"] / sub_avg["dismissals"], 2)
    checks["batting_average_formula_consistent"] = bool(np.allclose(sub_avg["batting_average"], calc_avg, atol=0.05))

    # Boundary consistency
    calc_b_runs = batting_overall_df["fours"] * 4 + batting_overall_df["sixes"] * 6
    checks["batting_boundary_runs_consistent"] = bool((batting_overall_df["boundary_runs"] == calc_b_runs).all())

    # 3. Bowling Non-Negativity Checks
    checks["bowling_legal_balls_non_negative"] = bool((bowling_overall_df["legal_balls_bowled"] >= 0).all())
    checks["bowling_runs_conceded_non_negative"] = bool((bowling_overall_df["runs_conceded"] >= 0).all())
    checks["bowling_wickets_non_negative"] = bool((bowling_overall_df["wickets_credited"] >= 0).all())

    # 4. Bowling Formula Consistency
    # Economy rate check
    valid_econ_mask = bowling_overall_df["legal_balls_bowled"] > 0
    sub_econ = bowling_overall_df[valid_econ_mask]
    calc_econ = np.round((sub_econ["runs_conceded"] * 6.0) / sub_econ["legal_balls_bowled"], 2)
    checks["bowling_economy_formula_consistent"] = bool(np.allclose(sub_econ["economy_rate"], calc_econ, atol=0.05))

    # Bowling average check (where wickets > 0)
    valid_bw_avg_mask = bowling_overall_df["wickets_credited"] > 0
    sub_bw_avg = bowling_overall_df[valid_bw_avg_mask]
    calc_bw_avg = np.round(sub_bw_avg["runs_conceded"] / sub_bw_avg["wickets_credited"], 2)
    checks["bowling_average_formula_consistent"] = bool(np.allclose(sub_bw_avg["bowling_average"], calc_bw_avg, atol=0.05))

    # 5. Referential Integrity: No duplicate player records in overall table
    checks["batting_no_duplicate_players"] = bool(batting_overall_df["player_id"].nunique() == len(batting_overall_df))
    checks["bowling_no_duplicate_players"] = bool(bowling_overall_df["player_id"].nunique() == len(bowling_overall_df))

    # 6. Low pressure consistency
    if batting_lp_df is not None:
        checks["batting_low_pressure_valid"] = bool(len(batting_lp_df) <= len(batting_overall_df))
    if bowling_lp_df is not None:
        checks["bowling_low_pressure_valid"] = bool(len(bowling_lp_df) <= len(bowling_overall_df))

    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        raise BaselineValidationError(f"Baseline validation failed on checks: {failed}")

    logger.info("All baseline validation checks passed successfully.")
    return checks


def generate_validation_report_csv(checks: Dict[str, bool], output_path: Path) -> Path:
    """Export validation checks to CSV."""
    rows = [{"check_name": k, "status": "PASSED" if v else "FAILED"} for k, v in checks.items()]
    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Saved baseline validation report to: %s", output_path)
    return output_path

