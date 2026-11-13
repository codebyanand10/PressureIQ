"""PressureIQ - Innings Phase Classifier.

Partitions delivery events into analytical innings phases (Powerplay, Middle Overs,
Death Overs, Super Over) proportionally based on completed legal balls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd

from src.logger import get_logger

logger = get_logger("PressureIQ.MatchState.InningsPhase")


@dataclass(frozen=True)
class InningsPhaseConfig:
    """Configurable boundaries for innings phases."""

    powerplay_end: float = 0.30
    middle_overs_end: float = 0.75


def classify_phase_single(
    legal_balls: int,
    available_legal_balls: int,
    is_super_over: bool = False,
    config: Optional[InningsPhaseConfig] = None,
) -> str:
    """Classify a single delivery state into an innings phase.

    Args:
        legal_balls: Cumulative legal balls bowled at this state.
        available_legal_balls: Total legal balls allocated to the innings.
        is_super_over: True if innings is a Super Over.
        config: InningsPhaseConfig with phase thresholds.

    Returns:
        One of 'POWERPLAY', 'MIDDLE_OVERS', 'DEATH_OVERS', or 'SUPER_OVER'.
    """
    if is_super_over or available_legal_balls <= 6:
        return "SUPER_OVER"

    if available_legal_balls <= 0:
        return "MIDDLE_OVERS"

    cfg = config or InningsPhaseConfig()
    ratio = legal_balls / available_legal_balls

    if ratio <= cfg.powerplay_end:
        return "POWERPLAY"
    elif ratio <= cfg.middle_overs_end:
        return "MIDDLE_OVERS"
    else:
        return "DEATH_OVERS"


def classify_innings_phase(
    legal_balls_series: pd.Series,
    available_legal_balls_series: pd.Series,
    is_super_over_series: pd.Series,
    config: Optional[InningsPhaseConfig] = None,
) -> pd.Series:
    """Vectorized classification of innings phases across all deliveries.

    Args:
        legal_balls_series: Cumulative legal balls bowled.
        available_legal_balls_series: Total legal balls available.
        is_super_over_series: Boolean indicator of Super Over.
        config: Optional phase thresholds.

    Returns:
        Series of phase category strings.
    """
    cfg = config or InningsPhaseConfig()

    # Calculate progress fraction
    safe_denom = np.where(available_legal_balls_series > 0, available_legal_balls_series, 120)
    ratio = legal_balls_series / safe_denom

    conditions = [
        is_super_over_series | (available_legal_balls_series <= 6),
        ratio <= cfg.powerplay_end,
        ratio <= cfg.middle_overs_end,
    ]
    choices = [
        "SUPER_OVER",
        "POWERPLAY",
        "MIDDLE_OVERS",
    ]

    phase_series = np.select(conditions, choices, default="DEATH_OVERS")
    return pd.Series(phase_series, index=legal_balls_series.index)

