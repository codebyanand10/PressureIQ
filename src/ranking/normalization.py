"""Normalization and robust scaling utilities for player ratings.

Ensures:
- Direction-aware transformations (e.g. higher strike rate is better; lower economy is better).
- Robust clipping and winsorization to prevent single-match outliers from dominating.
- Safe handling of missing values without fabricating zeros.
- Preservation of original values alongside transformed scores.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def safe_linear_scale(
    series: pd.Series,
    lower_bound: float,
    upper_bound: float,
    invert: bool = False,
    fill_value: float = 50.0,
) -> pd.Series:
    """Scale a series linearly to [0, 100] between lower_bound and upper_bound with clipping.

    Args:
        series: Metric series to scale.
        lower_bound: Value corresponding to score 0 (or 100 if inverted).
        upper_bound: Value corresponding to score 100 (or 0 if inverted).
        invert: If True, lower values yield higher scores (e.g. for economy, bowling average).
        fill_value: Default score for null or missing values.

    Returns:
        pd.Series of scaled scores bounded strictly in [0.0, 100.0].
    """
    if upper_bound <= lower_bound:
        raise ValueError(f"upper_bound ({upper_bound}) must be greater than lower_bound ({lower_bound})")

    s = pd.to_numeric(series, errors="coerce")
    clipped = s.clip(lower=lower_bound, upper=upper_bound)
    fraction = (clipped - lower_bound) / (upper_bound - lower_bound)

    if invert:
        score = (1.0 - fraction) * 100.0
    else:
        score = fraction * 100.0

    return score.fillna(fill_value).round(2)


def robust_percentile_scale(
    series: pd.Series,
    lower_percentile: float = 5.0,
    upper_percentile: float = 95.0,
    invert: bool = False,
    fill_value: float = 50.0,
) -> pd.Series:
    """Scale values based on observed empirical percentiles to minimize outlier influence."""
    valid = series.dropna()
    if len(valid) < 5:
        return pd.Series(fill_value, index=series.index)

    p_low = float(np.percentile(valid, lower_percentile))
    p_high = float(np.percentile(valid, upper_percentile))

    if p_high <= p_low:
        p_high = p_low + 1.0

    return safe_linear_scale(
        series,
        lower_bound=p_low,
        upper_bound=p_high,
        invert=invert,
        fill_value=fill_value,
    )


def winsorize_series(
    series: pd.Series,
    lower_quantile: float = 0.02,
    upper_quantile: float = 0.98,
) -> pd.Series:
    """Winsorize extreme values beyond specified quantiles."""
    valid = series.dropna()
    if len(valid) < 10:
        return series.copy()

    q_low = valid.quantile(lower_quantile)
    q_high = valid.quantile(upper_quantile)
    return series.clip(lower=q_low, upper=q_high)

