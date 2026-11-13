"""Statistical shrinkage module for small sample handling.

Implements Empirical Bayes shrinkage towards competition and role reference baselines:
theta_hat = w * X + (1 - w) * mu_ref
where w = N / (N + K).

Preserves original raw metrics and documents reference values and shrinkage strength.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from src.baselines.baseline_config import BaselineConfig

logger = logging.getLogger(__name__)


def apply_empirical_bayes_shrinkage(
    raw_vals: pd.Series,
    sample_sizes: pd.Series,
    k_constant: float,
    reference_val: Optional[float] = None,
) -> Tuple[pd.Series, pd.Series]:
    """Apply Empirical Bayes shrinkage to a metric series.

    Returns:
        Tuple of (shrunk_series, shrinkage_strength_series).
    """
    n = np.maximum(sample_sizes.fillna(0).astype(float), 0.0)
    ref = reference_val if reference_val is not None else float(raw_vals.dropna().median())

    # Shrinkage weight w = N / (N + K)
    w = n / (n + k_constant)
    shrunk = w * raw_vals.fillna(ref) + (1.0 - w) * ref
    strength = 1.0 - w

    return (pd.Series(np.round(shrunk, 2), index=raw_vals.index), pd.Series(np.round(strength, 4), index=raw_vals.index))


def apply_baseline_shrinkage(
    batting_df: pd.DataFrame,
    bowling_df: pd.DataFrame,
    config: Optional[BaselineConfig] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Apply shrinkage to batting and bowling baselines and construct audit report.

    Args:
        batting_df: Batting baseline DataFrame with raw statistics.
        bowling_df: Bowling baseline DataFrame with raw statistics.
        config: Optional BaselineConfig.

    Returns:
        Tuple of (enriched_batting_df, enriched_bowling_df, shrinkage_report_df).
    """
    cfg = config or BaselineConfig()
    logger.info("Applying Empirical Bayes shrinkage to player baselines...")

    b_df = batting_df.copy()
    bw_df = bowling_df.copy()
    report_rows = []

    # 1. Batting Shrinkage
    # Strike Rate: N = balls_faced, K = cfg.batting_sr_k, Ref = median SR
    ref_sr = 125.0
    shrunk_sr, strength_sr = apply_empirical_bayes_shrinkage(
        b_df["strike_rate"], b_df["total_balls_faced"], cfg.batting_sr_k, reference_val=ref_sr
    )
    b_df["shrunk_strike_rate"] = shrunk_sr
    b_df["strike_rate_shrinkage_strength"] = strength_sr

    # Batting Average: N = dismissals, K = cfg.batting_avg_k, Ref = median Avg
    ref_bat_avg = 22.0
    shrunk_b_avg, strength_b_avg = apply_empirical_bayes_shrinkage(
        b_df["batting_average"], b_df["dismissals"], cfg.batting_avg_k, reference_val=ref_bat_avg
    )
    b_df["shrunk_batting_average"] = shrunk_b_avg
    b_df["batting_avg_shrinkage_strength"] = strength_b_avg

    # Build report rows for batting
    for idx, row in b_df.iterrows():
        p_id = row["player_id"]
        # Strike rate row
        report_rows.append({
            "player_id": p_id,
            "metric": "strike_rate",
            "raw_metric": row["strike_rate"],
            "adjusted_metric": row["shrunk_strike_rate"],
            "reference_value": ref_sr,
            "sample_size": row["total_balls_faced"],
            "shrinkage_method": "Empirical Bayes (w = N / (N + K))",
            "shrinkage_strength": row["strike_rate_shrinkage_strength"],
        })
        # Batting average row
        report_rows.append({
            "player_id": p_id,
            "metric": "batting_average",
            "raw_metric": row["batting_average"],
            "adjusted_metric": row["shrunk_batting_average"],
            "reference_value": ref_bat_avg,
            "sample_size": row["dismissals"],
            "shrinkage_method": "Empirical Bayes (w = N / (N + K))",
            "shrinkage_strength": row["batting_avg_shrinkage_strength"],
        })

    # 2. Bowling Shrinkage
    # Economy Rate: N = legal_balls_bowled, K = cfg.bowling_econ_k, Ref = 8.2
    ref_econ = 8.20
    shrunk_econ, strength_econ = apply_empirical_bayes_shrinkage(
        bw_df["economy_rate"], bw_df["legal_balls_bowled"], cfg.bowling_econ_k, reference_val=ref_econ
    )
    bw_df["shrunk_economy_rate"] = shrunk_econ
    bw_df["economy_shrinkage_strength"] = strength_econ

    # Bowling Average: N = wickets_credited, K = cfg.bowling_avg_k, Ref = 24.0
    ref_bowl_avg = 24.0
    shrunk_bw_avg, strength_bw_avg = apply_empirical_bayes_shrinkage(
        bw_df["bowling_average"], bw_df["wickets_credited"], cfg.bowling_avg_k, reference_val=ref_bowl_avg
    )
    bw_df["shrunk_bowling_average"] = shrunk_bw_avg
    bw_df["bowling_avg_shrinkage_strength"] = strength_bw_avg

    # Build report rows for bowling
    for idx, row in bw_df.iterrows():
        p_id = row["player_id"]
        # Economy rate row
        report_rows.append({
            "player_id": p_id,
            "metric": "economy_rate",
            "raw_metric": row["economy_rate"],
            "adjusted_metric": row["shrunk_economy_rate"],
            "reference_value": ref_econ,
            "sample_size": row["legal_balls_bowled"],
            "shrinkage_method": "Empirical Bayes (w = N / (N + K))",
            "shrinkage_strength": row["economy_shrinkage_strength"],
        })
        # Bowling average row
        report_rows.append({
            "player_id": p_id,
            "metric": "bowling_average",
            "raw_metric": row["bowling_average"],
            "adjusted_metric": row["shrunk_bowling_average"],
            "reference_value": ref_bowl_avg,
            "sample_size": row["wickets_credited"],
            "shrinkage_method": "Empirical Bayes (w = N / (N + K))",
            "shrinkage_strength": row["bowling_avg_shrinkage_strength"],
        })

    report_df = pd.DataFrame(report_rows)
    logger.info("Shrinkage applied: generated %d shrinkage audit records.", len(report_df))

    return b_df, bw_df, report_df

