"""Sample size reliability and uncertainty adjustment module for Phase 8.

Applies Empirical Bayes shrinkage and conservative confidence bounds:
- Rewards players with sustained evidence across multiple matches.
- Regresses smaller samples toward the cohort prior mean to avoid small-sample flukes.
- Derives 95% confidence intervals for the final ratings based on match-block bootstrap variance.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from src.ranking.ranking_config import RankingConfig

logger = logging.getLogger(__name__)


def apply_reliability_adjustment_batting(
    batting_components_df: pd.DataFrame,
    config: RankingConfig,
) -> pd.DataFrame:
    """Apply Empirical Bayes shrinkage and derive confidence intervals for batting ratings.

    Args:
        batting_components_df: DataFrame with component scores and raw_fbpr.
        config: Ranking configuration.

    Returns:
        DataFrame with final_fbpr, ranking_score, ci_lower_fbpr, ci_upper_fbpr.
    """
    df = batting_components_df.copy()

    # Prior mean from eligible cohort
    prior_mean = float(df["raw_fbpr"].median())
    n0 = config.shrinkage_prior_weight_batting
    balls = df["balls_faced"].fillna(0).astype(float)

    # Shrinkage weight: lambda = N / (N + N0)
    shrinkage_factor = (balls / (balls + n0)).clip(lower=0.0, upper=1.0)
    df["shrinkage_factor"] = shrinkage_factor.round(4)

    # Empirical Bayes adjusted rating
    shrunk_fbpr = shrinkage_factor * df["raw_fbpr"] + (1.0 - shrinkage_factor) * prior_mean
    df["final_fbpr"] = shrunk_fbpr.clip(lower=0.0, upper=100.0).round(2)

    # Standard error propagation from bootstrap
    se_sr = df.get("bootstrap_se_sr", pd.Series(5.0, index=df.index)).fillna(5.0).astype(float)
    # Scaled uncertainty band: 10 SE in SR ~ 3.5 points in FBPR
    se_fbpr = (se_sr * 0.35).clip(lower=1.0, upper=12.0)
    df["rating_standard_error"] = se_fbpr.round(2)

    z = 1.96  # 95% confidence level
    df["ci_lower_fbpr"] = (df["final_fbpr"] - z * se_fbpr).clip(lower=0.0, upper=100.0).round(2)
    df["ci_upper_fbpr"] = (df["final_fbpr"] + z * se_fbpr).clip(lower=0.0, upper=100.0).round(2)
    df["ci_width_fbpr"] = (df["ci_upper_fbpr"] - df["ci_lower_fbpr"]).round(2)

    # Primary ranking score (for sorting): uses final_fbpr
    df["ranking_score"] = df["final_fbpr"]

    if "reliability_level" not in df.columns:
        df["reliability_level"] = np.where(
            balls >= 120, "High",
            np.where(balls >= 40, "Medium", "Low")
        )

    logger.info(
        "Applied reliability adjustment for %d batters (Prior: %.2f, Mean FBPR: %.2f).",
        len(df),
        prior_mean,
        df["final_fbpr"].mean(),
    )
    return df


def apply_reliability_adjustment_bowling(
    bowling_components_df: pd.DataFrame,
    config: RankingConfig,
) -> pd.DataFrame:
    """Apply Empirical Bayes shrinkage and derive confidence intervals for bowling ratings.

    Args:
        bowling_components_df: DataFrame with component scores and raw_fbor.
        config: Ranking configuration.

    Returns:
        DataFrame with final_fbor, ranking_score, ci_lower_fbor, ci_upper_fbor.
    """
    df = bowling_components_df.copy()

    prior_mean = float(df["raw_fbor"].median())
    n0 = config.shrinkage_prior_weight_bowling
    balls = df["legal_balls_bowled"].fillna(0).astype(float)

    # Shrinkage weight: lambda = N / (N + N0)
    shrinkage_factor = (balls / (balls + n0)).clip(lower=0.0, upper=1.0)
    df["shrinkage_factor"] = shrinkage_factor.round(4)

    # Empirical Bayes adjusted rating
    shrunk_fbor = shrinkage_factor * df["raw_fbor"] + (1.0 - shrinkage_factor) * prior_mean
    df["final_fbor"] = shrunk_fbor.clip(lower=0.0, upper=100.0).round(2)

    # Standard error propagation from bootstrap economy
    se_econ = df.get("bootstrap_se_econ", pd.Series(0.8, index=df.index)).fillna(0.8).astype(float)
    # Scaled uncertainty band: 1.0 SE in econ ~ 4.0 points in FBOR
    se_fbor = (se_econ * 4.0).clip(lower=1.0, upper=12.0)
    df["rating_standard_error"] = se_fbor.round(2)

    z = 1.96  # 95% confidence level
    df["ci_lower_fbor"] = (df["final_fbor"] - z * se_fbor).clip(lower=0.0, upper=100.0).round(2)
    df["ci_upper_fbor"] = (df["final_fbor"] + z * se_fbor).clip(lower=0.0, upper=100.0).round(2)
    df["ci_width_fbor"] = (df["ci_upper_fbor"] - df["ci_lower_fbor"]).round(2)

    # Primary ranking score (for sorting): uses final_fbor
    df["ranking_score"] = df["final_fbor"]

    if "reliability_level" not in df.columns:
        df["reliability_level"] = np.where(
            balls >= 120, "High",
            np.where(balls >= 48, "Medium", "Low")
        )

    logger.info(
        "Applied reliability adjustment for %d bowlers (Prior: %.2f, Mean FBOR: %.2f).",
        len(df),
        prior_mean,
        df["final_fbor"].mean(),
    )
    return df

