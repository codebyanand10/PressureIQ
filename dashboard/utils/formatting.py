"""PressureIQ Dashboard Value Formatting Utilities.

Provides reliable formatting of numbers, percentages, deltas, and confidence intervals.
"""

from __future__ import annotations
from typing import Any, Union
import math
import pandas as pd
import numpy as np


def format_number(val: Any, decimals: int = 1, default: str = "—") -> str:
    """Format numeric values safely."""
    if val is None or pd.isna(val):
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f"{f:.{decimals}f}"
    except (ValueError, TypeError):
        return default


def format_int(val: Any, default: str = "—") -> str:
    """Format integer counts with commas."""
    if val is None or pd.isna(val):
        return default
    try:
        i = int(round(float(val)))
        return f"{i:,}"
    except (ValueError, TypeError):
        return default


def format_pct(val: Any, decimals: int = 1, default: str = "—") -> str:
    """Format percentage values."""
    if val is None or pd.isna(val):
        return default
    try:
        f = float(val)
        if math.isnan(f):
            return default
        return f"{f:.{decimals}f}%"
    except (ValueError, TypeError):
        return default


def format_delta(val: Any, decimals: int = 1, default: str = "—") -> str:
    """Format positive/negative delta strings (e.g. +14.2 or -3.1)."""
    if val is None or pd.isna(val):
        return default
    try:
        f = float(val)
        if math.isnan(f):
            return default
        prefix = "+" if f > 0 else ""
        return f"{prefix}{f:.{decimals}f}"
    except (ValueError, TypeError):
        return default


def format_ci(lower: Any, upper: Any, decimals: int = 1, default: str = "—") -> str:
    """Format confidence interval bracket [lower, upper]."""
    if lower is None or upper is None or pd.isna(lower) or pd.isna(upper):
        return default
    try:
        l_val = float(lower)
        u_val = float(upper)
        return f"[{l_val:.{decimals}f}, {u_val:.{decimals}f}]"
    except (ValueError, TypeError):
        return default


def format_overs(legal_balls: Any) -> str:
    """Convert legal ball count into standard cricket overs (e.g. 23 balls -> 3.5 ov)."""
    if legal_balls is None or pd.isna(legal_balls):
        return "0.0"
    try:
        balls = int(round(float(legal_balls)))
        overs = balls // 6
        remaining_balls = balls % 6
        return f"{overs}.{remaining_balls}"
    except (ValueError, TypeError):
        return "0.0"


def format_rank(rank_val: Any) -> str:
    """Format rank as #1, #2, etc."""
    if rank_val is None or pd.isna(rank_val):
        return "—"
    try:
        r = int(round(float(rank_val)))
        return f"#{r}"
    except (ValueError, TypeError):
        return "—"

