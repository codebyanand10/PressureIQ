"""Unit tests for the pressure classifier module.

Tests scalar and vectorized classification into the five standard tiers.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import pytest

from src.pressure.pressure_classifier import (
    classify_pressure_score,
    classify_pressure_vector,
)
from src.pressure.pressure_config import PressureConfig


def test_classify_pressure_score_tiers():
    """Verify tier mappings according to configured thresholds."""
    cfg = PressureConfig()

    assert classify_pressure_score(10.0, cfg) == "Very Low"
    assert classify_pressure_score(25.0, cfg) == "Low"
    assert classify_pressure_score(50.0, cfg) == "Moderate"
    assert classify_pressure_score(70.0, cfg) == "High"
    assert classify_pressure_score(92.0, cfg) == "Extreme"
    assert classify_pressure_score(np.nan, cfg) == "Unknown"


def test_classify_pressure_vector():
    """Verify vectorized classification over a pandas Series."""
    s = pd.Series([5.0, 35.0, 55.0, 75.0, 95.0, np.nan])
    res = classify_pressure_vector(s)

    expected = ["Very Low", "Low", "Moderate", "High", "Extreme", "Unknown"]
    assert res.tolist() == expected

