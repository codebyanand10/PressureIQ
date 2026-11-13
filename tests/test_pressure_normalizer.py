"""Unit tests for the pressure normalizer module.

Tests percentile scaling, group-level fitting, fallback behavior on small samples,
and preservation of bounds.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.pressure.pressure_normalizer import PressureNormalizer
from src.pressure.pressure_config import PressureConfig


def test_pressure_normalizer_global():
    """Verify global percentile ranking and monotonicity."""
    vals = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0])
    norm = PressureNormalizer()
    scaled = norm.fit_transform(vals)

    assert len(scaled) == 10
    assert scaled.min() >= 0.0
    assert scaled.max() <= 100.0
    # Strictly increasing
    assert (scaled.diff().dropna() >= 0).all()


def test_pressure_normalizer_small_sample_fallback():
    """Verify small groups (< min_group_size) safely fall back to global quantiles."""
    cfg = PressureConfig({"normalization": {"minimum_group_size": 50, "fallback_to_global": True}})
    norm = PressureNormalizer(config=cfg)

    # 150 items for IPL, 10 items for Associate (should fall back to global)
    vals = pd.Series(list(range(100, 250)) + list(range(10, 20)))
    groups = pd.Series(["IPL"] * 150 + ["Associate"] * 10)

    norm.fit(vals, groups)
    assert "IPL" in norm.group_quantiles
    assert "Associate" not in norm.group_quantiles

    transformed = norm.transform(pd.Series([15.0]), groups=pd.Series(["Associate"]))
    assert not np.isnan(transformed[0])
    assert 0.0 <= transformed[0] <= 100.0

