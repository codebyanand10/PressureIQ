"""PressureIQ - ranking_engine.py

Top-level module exposing the Unified Player Rating & Ranking Engine (Phase 8).
Orchestrates multi-dimensional clutch player ratings, deterministic tie-breaking,
sample-size reliability shrinkage, and official Top 10 rankings under pressure.

TODO (Phase 9+): Advanced stress testing, robustness evaluation, and Streamlit interactive dashboard integration.
"""

from __future__ import annotations

from src.ranking.ranking_config import RankingConfig, RankingConfigError
from src.ranking.data_loader import load_ranking_inputs
from src.ranking.eligibility import (
    evaluate_batting_eligibility,
    evaluate_bowling_eligibility,
)
from src.ranking.normalization import (
    safe_linear_scale,
    robust_percentile_scale,
    winsorize_series,
)
from src.ranking.batting_rating import calculate_batting_rating_components
from src.ranking.bowling_rating import calculate_bowling_rating_components
from src.ranking.reliability import (
    apply_reliability_adjustment_batting,
    apply_reliability_adjustment_bowling,
)
from src.ranking.ranking_explainability import (
    generate_batting_ranking_explanations,
    generate_bowling_ranking_explanations,
)
from src.ranking.ranking_validation import validate_rankings, audit_ranking_fairness
from src.ranking.export import (
    export_rankings_datasets,
    export_ranking_reports,
    generate_ranking_visualizations,
)
from src.ranking.ranking_engine import calculate_unified_player_rankings

__all__ = [
    "RankingConfig",
    "RankingConfigError",
    "load_ranking_inputs",
    "evaluate_batting_eligibility",
    "evaluate_bowling_eligibility",
    "safe_linear_scale",
    "robust_percentile_scale",
    "winsorize_series",
    "calculate_batting_rating_components",
    "calculate_bowling_rating_components",
    "apply_reliability_adjustment_batting",
    "apply_reliability_adjustment_bowling",
    "generate_batting_ranking_explanations",
    "generate_bowling_ranking_explanations",
    "validate_rankings",
    "audit_ranking_fairness",
    "export_rankings_datasets",
    "export_ranking_reports",
    "generate_ranking_visualizations",
    "calculate_unified_player_rankings",
]
