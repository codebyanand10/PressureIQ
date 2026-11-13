"""Pressure score classification module.

Categorizes numeric pressure scores into standard analytical levels:
Very Low, Low, Moderate, High, and Extreme.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Union
from src.pressure.pressure_config import PressureConfig


def classify_pressure_score(
    score: float,
    config: Optional[PressureConfig] = None,
) -> str:
    """Classify a single numeric pressure score into an analytical level."""
    if np.isnan(score):
        return "Unknown"

    cfg = config or PressureConfig()
    th = cfg.classification_thresholds

    if score <= th["very_low_max"]:
        return "Very Low"
    elif score <= th["low_max"]:
        return "Low"
    elif score <= th["moderate_max"]:
        return "Moderate"
    elif score <= th["high_max"]:
        return "High"
    else:
        return "Extreme"


def classify_pressure_vector(
    scores: Union[pd.Series, np.ndarray],
    config: Optional[PressureConfig] = None,
) -> pd.Series:
    """Classify an array or Series of numeric pressure scores into analytical levels."""
    cfg = config or PressureConfig()
    th = cfg.classification_thresholds

    s_arr = np.asarray(scores, dtype=float)

    conditions = [
        np.isnan(s_arr),
        s_arr <= th["very_low_max"],
        s_arr <= th["low_max"],
        s_arr <= th["moderate_max"],
        s_arr <= th["high_max"],
    ]

    choices = [
        "Unknown",
        "Very Low",
        "Low",
        "Moderate",
        "High",
    ]

    result = np.select(conditions, choices, default="Extreme")
    index = scores.index if isinstance(scores, pd.Series) else None
    return pd.Series(result, index=index, name="pressure_level")

