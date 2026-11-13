"""PressureIQ - Innings Configuration & Metadata Resolver.

Determines scheduled overs, revised overs, legal ball quotas, and target
characteristics for every innings in every match based on empirical metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from src.logger import get_logger

logger = get_logger("PressureIQ.MatchState.InningsConfig")


@dataclass(frozen=True)
class InningsConfig:
    """Configuration and allocation parameters for a specific match innings."""

    match_id: int
    innings: int
    comp_id: int
    match_format: str
    season: str
    is_first_innings: bool
    is_chasing_innings: bool
    is_super_over: bool
    scheduled_overs: float
    available_overs: float
    available_legal_balls: int
    is_reduced_overs: bool
    has_target: bool
    target_score: Optional[float]
    target_source: str


def resolve_innings_configs(
    matches_df: pd.DataFrame,
    targets_map: Dict[Tuple[int, int], Tuple[Optional[float], str]],
    default_t20_overs: int = 20,
    default_super_over_overs: int = 1,
) -> Dict[Tuple[int, int], InningsConfig]:
    """Resolve allocation quotas and target parameters for all match innings.

    Args:
        matches_df: Match metadata containing DLS parameters and formats.
        targets_map: Lookup mapping (match_id, innings) -> (target_score, target_source).
        default_t20_overs: Standard T20 overs (20 overs = 120 legal balls).
        default_super_over_overs: Standard Super Over overs (1 over = 6 legal balls).

    Returns:
        Dictionary mapping (match_id, innings) to InningsConfig.
    """
    logger.info("Resolving innings configurations and legal ball quotas...")
    configs: Dict[Tuple[int, int], InningsConfig] = {}

    matches_lookup = matches_df.set_index("match_id").to_dict(orient="index")

    for (m_id, inn), (target_score, target_source) in targets_map.items():
        m_info = matches_lookup.get(m_id, {})
        comp_id = int(m_info.get("comp_id", 0))
        match_format = str(m_info.get("match_format", "T20"))
        season = str(m_info.get("season", ""))

        is_super_over = inn in [3, 4]
        is_first_innings = inn in [1, 3]
        is_chasing = inn in [2, 4]

        if is_super_over:
            scheduled_overs = float(default_super_over_overs)
            available_overs = float(default_super_over_overs)
            available_legal_balls = int(default_super_over_overs * 6)
            is_reduced = False
        else:
            scheduled_overs = float(default_t20_overs)

            # Check rain revision in matches metadata (stored as legal balls)
            rev_balls = None
            if inn == 1 and pd.notna(m_info.get("first_inn_revised_overs")):
                rev_balls = float(m_info["first_inn_revised_overs"])
            elif inn == 2 and pd.notna(m_info.get("second_inn_revised_overs")):
                rev_balls = float(m_info["second_inn_revised_overs"])

            if rev_balls is not None and rev_balls > 0:
                available_legal_balls = int(rev_balls)
                available_overs = round(rev_balls / 6.0, 3)
                is_reduced = available_legal_balls < (default_t20_overs * 6)
            else:
                available_legal_balls = int(default_t20_overs * 6)
                available_overs = float(default_t20_overs)
                is_reduced = False

        has_target = is_chasing and (target_score is not None and not np.isnan(target_score))

        configs[(m_id, inn)] = InningsConfig(
            match_id=m_id,
            innings=inn,
            comp_id=comp_id,
            match_format=match_format,
            season=season,
            is_first_innings=is_first_innings,
            is_chasing_innings=is_chasing,
            is_super_over=is_super_over,
            scheduled_overs=scheduled_overs,
            available_overs=available_overs,
            available_legal_balls=available_legal_balls,
            is_reduced_overs=is_reduced,
            has_target=has_target,
            target_score=target_score if has_target else None,
            target_source=target_source,
        )

    logger.info(f"Successfully configured {len(configs)} match innings.")
    return configs

