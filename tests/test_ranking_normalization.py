"""Unit tests for Phase 8 ranking normalization and scaling."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.ranking.normalization import (
    safe_linear_scale,
    robust_percentile_scale,
    winsorize_series,
)


def test_safe_linear_scale_direction():
    """Verify standard and inverted scaling with clipping."""
    # Standard: higher is better
    s1 = pd.Series([70.0, 80.0, 140.0, 200.0, 250.0])
    scaled1 = safe_linear_scale(s1, lower_bound=80.0, upper_bound=200.0)

    assert scaled1.iloc[0] == 0.0   # clipped at 80
    assert scaled1.iloc[1] == 0.0
    assert scaled1.iloc[2] == 50.0  # midpoint
    assert scaled1.iloc[3] == 100.0
    assert scaled1.iloc[4] == 100.0 # clipped at 200

    # Inverted: lower is better (e.g. economy)
    s2 = pd.Series([5.0, 6.0, 9.5, 13.0, 15.0])
    scaled2 = safe_linear_scale(s2, lower_bound=6.0, upper_bound=13.0, invert=True)

    assert scaled2.iloc[0] == 100.0 # best (<= 6.0)
    assert scaled2.iloc[1] == 100.0
    assert pytest.approx(scaled2.iloc[2], 0.1) == 50.0
    assert scaled2.iloc[3] == 0.0
    assert scaled2.iloc[4] == 0.0   # worst (>= 13.0)


def test_safe_linear_scale_null_handling():
    """Verify that NaN values are filled safely with fill_value without throwing exceptions."""
    s = pd.Series([np.nan, None, 100.0])
    scaled = safe_linear_scale(s, lower_bound=50.0, upper_bound=150.0, fill_value=45.0)

    assert scaled.iloc[0] == 45.0
    assert scaled.iloc[1] == 45.0
    assert scaled.iloc[2] == 50.0


def test_winsorize_series():
    """Verify extreme outlier bounding."""
    s = pd.Series(list(range(100)) + [1000.0, -500.0])
    w = winsorize_series(s, lower_quantile=0.05, upper_quantile=0.95)

    assert w.max() < 1000.0
    assert w.min() > -500.0

