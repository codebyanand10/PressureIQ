"""Statistical reliability and bootstrap confidence interval estimation module for bowling.

Evaluates sample adequacy across high-pressure deliveries using:
- Match-level block bootstrap resampling (500 iterations) to account for within-match delivery clustering.
- Reliability tier assignment: High, Medium, Low, Insufficient Data.
- Audit quality flags: small sample, zero wickets, wide confidence interval.

Produces `bowler_pressure_reliability.parquet`.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bowling_pressure_metrics import annotate_bowling_deliveries

logger = logging.getLogger(__name__)


def calculate_match_block_bootstrap_bowling(
    player_deliveries_df: pd.DataFrame,
    iterations: int = 500,
    confidence_level: float = 0.95,
    random_seed: int = 42,
) -> Dict[str, float]:
    """Calculate match-level block bootstrap confidence intervals for bowling economy.

    Resamples matches with replacement to preserve clustered delivery correlation.
    Uses vectorized NumPy match aggregates for optimal computational efficiency.
    """
    match_agg = player_deliveries_df.groupby("match_id", as_index=False).agg(
        runs=("bowler_runs_calc", "sum"),
        balls=("is_legal_calc", "sum"),
    )
    runs_arr = match_agg["runs"].to_numpy(dtype=float)
    balls_arr = match_agg["balls"].to_numpy(dtype=float)
    n_matches = len(runs_arr)

    if n_matches < 2 or balls_arr.sum() < 6:
        return {
            "ci_lower_econ": np.nan,
            "ci_upper_econ": np.nan,
            "ci_width_econ": np.nan,
            "bootstrap_se_econ": np.nan,
        }

    rng = np.random.default_rng(random_seed)
    # Fully vectorized index matrix: (iterations x n_matches)
    idx = rng.integers(0, n_matches, size=(iterations, n_matches))
    sampled_runs = runs_arr[idx].sum(axis=1)
    sampled_balls = balls_arr[idx].sum(axis=1)

    valid_mask = sampled_balls > 0
    if valid_mask.sum() < 20:
        return {
            "ci_lower_econ": np.nan,
            "ci_upper_econ": np.nan,
            "ci_width_econ": np.nan,
            "bootstrap_se_econ": np.nan,
        }

    sampled_econs = (sampled_runs[valid_mask] * 6.0) / sampled_balls[valid_mask]

    alpha = (1.0 - confidence_level) / 2.0
    lower = float(np.percentile(sampled_econs, alpha * 100))
    upper = float(np.percentile(sampled_econs, (1.0 - alpha) * 100))
    se = float(np.std(sampled_econs, ddof=1))

    return {
        "ci_lower_econ": round(lower, 2),
        "ci_upper_econ": round(upper, 2),
        "ci_width_econ": round(upper - lower, 2),
        "bootstrap_se_econ": round(se, 2),
    }


def assess_bowling_reliability(
    bppi_df: pd.DataFrame,
    high_pressure_deliveries_df: pd.DataFrame,
    config: Optional[BowlingPressureConfig] = None,
) -> pd.DataFrame:
    """Assess sample reliability tiers and calculate bootstrap confidence intervals.

    Args:
        bppi_df: Output from bppi_b_calculator containing bowler metrics.
        high_pressure_deliveries_df: Raw annotated deliveries with pressure >= 60.0.
        config: Configuration parameters.

    Returns:
        DataFrame representing `bowler_pressure_reliability.parquet`.
    """
    cfg = config or BowlingPressureConfig()
    logger.info("Assessing bowling pressure sample reliability and running bootstrap resampling...")

    df = bppi_df.copy()
    deliv = annotate_bowling_deliveries(high_pressure_deliveries_df)

    # 1. Sample counts
    lb = df["legal_balls_bowled"].fillna(0).astype(int)
    matches = df["matches_bowled"].fillna(0).astype(int)
    inns = df["innings_bowled"].fillna(0).astype(int)
    wkts = df["wickets_credited"].fillna(0).astype(int)
    base_rel = df.get("overall_baseline_reliability_level", pd.Series("Unknown", index=df.index))

    # 2. Assign Reliability Tier
    cond_high = (lb >= cfg.high_min_balls) & (matches >= cfg.min_matches) & (base_rel.isin(["High", "Medium"]))
    cond_med = (lb >= cfg.medium_min_balls) & (matches >= 3)
    cond_low = (lb >= cfg.low_min_balls) & (matches >= 2)

    tier = np.where(
        cond_high, "High",
        np.where(cond_med, "Medium",
        np.where(cond_low, "Low", "Insufficient Data"))
    )
    df["reliability_level"] = tier

    # Quantitative Reliability Score (0 to 100)
    score = (
        np.clip(lb / cfg.high_min_balls, 0.0, 1.0) * 50.0
        + np.clip(matches / cfg.min_matches, 0.0, 1.0) * 30.0
        + np.clip(inns / cfg.min_innings, 0.0, 1.0) * 20.0
    )
    df["reliability_score"] = score.round(2)
    df["is_statistically_reliable"] = df["reliability_level"].isin(["High", "Medium"])

    # 3. Quality Flags
    df["flag_small_sample"] = lb < cfg.medium_min_balls
    df["flag_zero_wickets"] = wkts == 0
    df["flag_insufficient_matches"] = matches < cfg.min_matches

    # 4. Block Bootstrap CIs
    logger.info("Running block bootstrap for %d bowlers with >= 18 legal balls...", (lb >= cfg.low_min_balls).sum())
    ci_records: Dict[str, Dict[str, float]] = {}
    deliv_by_player = {pid: grp for pid, grp in deliv.groupby("bowler_id")}

    for pid in df["player_id"]:
        if pid in deliv_by_player and len(deliv_by_player[pid]) >= cfg.low_min_balls:
            ci = calculate_match_block_bootstrap_bowling(
                deliv_by_player[pid],
                iterations=cfg.bootstrap_iterations,
                confidence_level=cfg.bootstrap_confidence_level,
            )
            ci_records[pid] = ci
        else:
            ci_records[pid] = {
                "ci_lower_econ": np.nan,
                "ci_upper_econ": np.nan,
                "ci_width_econ": np.nan,
                "bootstrap_se_econ": np.nan,
            }

    ci_df = pd.DataFrame.from_dict(ci_records, orient="index").reset_index().rename(columns={"index": "player_id"})
    df = df.merge(ci_df, on="player_id", how="left")

    df["flag_high_variance"] = df["ci_width_econ"].fillna(10.0) > 4.0

    # Derive BPPI-B confidence intervals based on bootstrap economy bounds
    econ_series = df.get("economy_rate", pd.Series(np.nan, index=df.index))
    econ_val = econ_series.replace(0.0, np.nan)
    # Note: lower economy is favorable, so upper econ leads to lower BPPI-B
    econ_lower_ratio = (df["ci_lower_econ"] / econ_val).clip(lower=0.5, upper=1.5)
    econ_upper_ratio = (df["ci_upper_econ"] / econ_val).clip(lower=0.5, upper=1.5)

    df["ci_lower_bppi_b"] = np.where(
        df["is_statistically_reliable"],
        (df["bppi_b"] * (0.70 + 0.30 * (2.0 - econ_upper_ratio))).clip(lower=0.0, upper=100.0).round(2),
        np.nan,
    )
    df["ci_upper_bppi_b"] = np.where(
        df["is_statistically_reliable"],
        (df["bppi_b"] * (0.70 + 0.30 * (2.0 - econ_lower_ratio))).clip(lower=0.0, upper=100.0).round(2),
        np.nan,
    )

    logger.info(
        "Reliability distribution: High=%d, Medium=%d, Low=%d, Insufficient Data=%d",
        (df["reliability_level"] == "High").sum(),
        (df["reliability_level"] == "Medium").sum(),
        (df["reliability_level"] == "Low").sum(),
        (df["reliability_level"] == "Insufficient Data").sum(),
    )
    return df
