"""Statistical reliability and bootstrap confidence interval estimation module.

Evaluates sample adequacy across high-pressure deliveries using:
- Match-level block bootstrap resampling (500 iterations) to account for within-match delivery clustering.
- Reliability tier assignment: High, Medium, Low, Insufficient Data.
- Audit quality flags: small sample, zero dismissals, wide confidence interval.

Produces `batter_pressure_reliability.parquet`.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.batting_pressure.batting_pressure_config import BattingPressureConfig
from src.batting_pressure.batting_pressure_metrics import annotate_batting_deliveries

logger = logging.getLogger(__name__)


def calculate_match_block_bootstrap(
    player_deliveries_df: pd.DataFrame,
    iterations: int = 500,
    confidence_level: float = 0.95,
    random_seed: int = 42,
) -> Dict[str, float]:
    """Calculate match-level block bootstrap confidence intervals for a single player.

    Resamples matches with replacement to preserve clustered delivery correlation.
    Uses vectorized NumPy match aggregates for optimal computational efficiency.
    """
    match_agg = player_deliveries_df.groupby("match_id", as_index=False).agg(
        runs=("batter_runs_calc", "sum"),
        balls=("is_ball_faced", "sum"),
    )
    runs_arr = match_agg["runs"].to_numpy(dtype=float)
    balls_arr = match_agg["balls"].to_numpy(dtype=float)
    n_matches = len(runs_arr)

    if n_matches < 2 or balls_arr.sum() < 5:
        return {
            "ci_lower_sr": np.nan,
            "ci_upper_sr": np.nan,
            "ci_width_sr": np.nan,
            "bootstrap_se_sr": np.nan,
        }

    rng = np.random.default_rng(random_seed)
    # Fully vectorized index matrix: (iterations x n_matches)
    idx = rng.integers(0, n_matches, size=(iterations, n_matches))
    sampled_runs = runs_arr[idx].sum(axis=1)
    sampled_balls = balls_arr[idx].sum(axis=1)

    valid_mask = sampled_balls > 0
    if valid_mask.sum() < 20:
        return {
            "ci_lower_sr": np.nan,
            "ci_upper_sr": np.nan,
            "ci_width_sr": np.nan,
            "bootstrap_se_sr": np.nan,
        }

    sampled_srs = (sampled_runs[valid_mask] / sampled_balls[valid_mask]) * 100.0

    alpha = (1.0 - confidence_level) / 2.0
    lower = float(np.percentile(sampled_srs, alpha * 100))
    upper = float(np.percentile(sampled_srs, (1.0 - alpha) * 100))
    se = float(np.std(sampled_srs, ddof=1))

    return {
        "ci_lower_sr": round(lower, 2),
        "ci_upper_sr": round(upper, 2),
        "ci_width_sr": round(upper - lower, 2),
        "bootstrap_se_sr": round(se, 2),
    }


def assess_batting_reliability(
    bppi_df: pd.DataFrame,
    high_pressure_deliveries_df: pd.DataFrame,
    config: Optional[BattingPressureConfig] = None,
) -> pd.DataFrame:
    """Assess sample reliability tiers and calculate bootstrap confidence intervals.

    Args:
        bppi_df: Output from bppi_calculator containing batter metrics.
        high_pressure_deliveries_df: Raw annotated deliveries with pressure >= 60.0.
        config: Configuration parameters.

    Returns:
        DataFrame representing `batter_pressure_reliability.parquet`.
    """
    cfg = config or BattingPressureConfig()
    logger.info("Assessing batting pressure sample reliability and running bootstrap resampling...")

    df = bppi_df.copy()
    deliv = annotate_batting_deliveries(high_pressure_deliveries_df)

    # 1. Sample counts
    bf = df["balls_faced"].fillna(0).astype(int)
    matches = df["matches_count"].fillna(0).astype(int)
    inns = df["innings_count"].fillna(0).astype(int)
    dism = df["dismissals"].fillna(0).astype(int)
    base_rel = df.get("overall_baseline_reliability_level", pd.Series("Unknown", index=df.index))

    # 2. Assign Reliability Tier
    cond_high = (bf >= cfg.high_min_balls) & (matches >= cfg.min_matches) & (base_rel.isin(["High", "Medium"]))
    cond_med = (bf >= cfg.medium_min_balls) & (matches >= 3)
    cond_low = (bf >= cfg.low_min_balls) & (matches >= 2)

    tier = np.where(
        cond_high, "High",
        np.where(cond_med, "Medium",
        np.where(cond_low, "Low", "Insufficient Data"))
    )
    df["reliability_level"] = tier

    # Quantitative Reliability Score (0 to 100)
    score = (
        np.clip(bf / cfg.high_min_balls, 0.0, 1.0) * 50.0
        + np.clip(matches / cfg.min_matches, 0.0, 1.0) * 30.0
        + np.clip(inns / cfg.min_innings, 0.0, 1.0) * 20.0
    )
    df["reliability_score"] = score.round(2)
    df["is_statistically_reliable"] = df["reliability_level"].isin(["High", "Medium"])

    # 3. Quality Flags
    df["flag_small_sample"] = bf < cfg.medium_min_balls
    df["flag_zero_dismissals"] = dism == 0
    df["flag_insufficient_matches"] = matches < cfg.min_matches

    # 4. Block Bootstrap CIs
    logger.info("Running block bootstrap for %d batters with >= 15 balls...", (bf >= 15).sum())
    ci_records: Dict[str, Dict[str, float]] = {}
    deliv_by_player = {pid: grp for pid, grp in deliv.groupby("striker_id")}

    for pid in df["player_id"]:
        if pid in deliv_by_player and len(deliv_by_player[pid]) >= cfg.low_min_balls:
            ci = calculate_match_block_bootstrap(
                deliv_by_player[pid],
                iterations=cfg.bootstrap_iterations,
                confidence_level=cfg.bootstrap_confidence_level,
            )
            ci_records[pid] = ci
        else:
            ci_records[pid] = {
                "ci_lower_sr": np.nan,
                "ci_upper_sr": np.nan,
                "ci_width_sr": np.nan,
                "bootstrap_se_sr": np.nan,
            }

    ci_df = pd.DataFrame.from_dict(ci_records, orient="index").reset_index().rename(columns={"index": "player_id"})
    df = df.merge(ci_df, on="player_id", how="left")

    df["flag_high_variance"] = df["ci_width_sr"].fillna(100.0) > 40.0

    # Derive BPPI confidence intervals based on bootstrap strike rate bounds
    sr_val = df["strike_rate"].replace(0.0, np.nan)
    sr_lower_ratio = (df["ci_lower_sr"] / sr_val).clip(lower=0.5, upper=1.5)
    sr_upper_ratio = (df["ci_upper_sr"] / sr_val).clip(lower=0.5, upper=1.5)

    df["ci_lower_bppi"] = np.where(
        df["is_statistically_reliable"],
        (df["bppi"] * (0.70 + 0.30 * sr_lower_ratio)).clip(lower=0.0, upper=100.0).round(2),
        np.nan,
    )
    df["ci_upper_bppi"] = np.where(
        df["is_statistically_reliable"],
        (df["bppi"] * (0.70 + 0.30 * sr_upper_ratio)).clip(lower=0.0, upper=100.0).round(2),
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
