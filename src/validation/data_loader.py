"""Data loading module for Phase 9: Statistical Validation & Robustness Testing.

Loads Phase 8 official rankings, Phase 6 & 7 intermediate performance aggregates,
delivery-level pressure scores, baselines, and match metadata via DuckDB.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional
import duckdb
import pandas as pd

from src.config import config

logger = logging.getLogger(__name__)


def load_validation_inputs(
    base_dir: Optional[Path] = None,
) -> Dict[str, pd.DataFrame]:
    """Load all datasets required for Phase 9 validation.

    Args:
        base_dir: Optional root data/processed directory.

    Returns:
        Dictionary of loaded datasets.
    """
    proc = base_dir or config.data_processed_dir
    con = duckdb.connect()

    logger.info("Loading validation input datasets from %s...", proc)

    # 1. Official Phase 8 Rankings & Eligibility
    rankings_dir = proc / "rankings"
    batter_ratings = con.execute(f"SELECT * FROM '{rankings_dir / 'batter_ratings.parquet'}'").df()
    bowler_ratings = con.execute(f"SELECT * FROM '{rankings_dir / 'bowler_ratings.parquet'}'").df()
    batting_el = con.execute(f"SELECT * FROM '{rankings_dir / 'batting_eligibility.parquet'}'").df()
    bowling_el = con.execute(f"SELECT * FROM '{rankings_dir / 'bowling_eligibility.parquet'}'").df()
    ranking_components = con.execute(f"SELECT * FROM '{rankings_dir / 'ranking_components.parquet'}'").df()

    # 2. Metadata
    match_meta = con.execute(f"SELECT * FROM '{proc / 'match_metadata.parquet'}'").df()
    player_reg = con.execute(f"SELECT * FROM '{proc / 'player_registration_metadata.parquet'}'").df()

    # 3. Baselines
    base_dir_path = proc / "baselines"
    bat_baseline = con.execute(f"SELECT * FROM '{base_dir_path / 'batting_overall_baseline.parquet'}'").df()
    bowl_baseline = con.execute(f"SELECT * FROM '{base_dir_path / 'bowling_overall_baseline.parquet'}'").df()
    ctx_bat_baseline = con.execute(f"SELECT * FROM '{base_dir_path / 'batting_contextual_baseline.parquet'}'").df()
    ctx_bowl_baseline = con.execute(f"SELECT * FROM '{base_dir_path / 'bowling_contextual_baseline.parquet'}'").df()

    # 4. Phase 6 & Phase 7 Performance Metrics (for sensitivity & recalculation)
    bat_bppi = con.execute(f"SELECT * FROM '{proc / 'batting_pressure' / 'batter_pressure_performance_index.parquet'}'").df()
    bat_hp = con.execute(f"SELECT * FROM '{proc / 'batting_pressure' / 'batter_high_pressure_performance.parquet'}'").df()
    bat_comp = con.execute(f"SELECT * FROM '{proc / 'batting_pressure' / 'batter_baseline_comparison.parquet'}'").df()
    bat_rel = con.execute(f"SELECT * FROM '{proc / 'batting_pressure' / 'batter_pressure_reliability.parquet'}'").df()

    bowl_bppi = con.execute(f"SELECT * FROM '{proc / 'bowling_pressure' / 'bowler_pressure_performance_index.parquet'}'").df()
    bowl_hp = con.execute(f"SELECT * FROM '{proc / 'bowling_pressure' / 'bowler_high_pressure_performance.parquet'}'").df()
    bowl_comp = con.execute(f"SELECT * FROM '{proc / 'bowling_pressure' / 'bowler_baseline_comparison.parquet'}'").df()
    bowl_rel = con.execute(f"SELECT * FROM '{proc / 'bowling_pressure' / 'bowler_pressure_reliability.parquet'}'").df()
    bowl_roles = con.execute(f"SELECT * FROM '{proc / 'bowling_pressure' / 'bowler_role_analysis.parquet'}'").df()

    # 5. Delivery Level Pressure Summary (aggregated by player & match for fast block-bootstrap)
    # Aggregating by (player_id, match_id) allows fast match-level resampling without re-aggregating millions of rows on every iteration!
    logger.info("Building match-level player performance aggregates for block-bootstrap...")
    pressure_pq = proc / "pressure" / "pressure_scores.parquet"

    # Batting match-level high pressure aggregates
    bat_match_agg = con.execute(f"""
        SELECT 
            CAST(striker_id AS VARCHAR) AS player_id,
            match_id,
            COUNT(*) AS hp_balls,
            SUM(runs) AS hp_runs,
            SUM(CASE WHEN is_four = 1 THEN 1 ELSE 0 END) AS hp_fours,
            SUM(CASE WHEN is_six = 1 THEN 1 ELSE 0 END) AS hp_sixes,
            SUM(CASE WHEN runs = 0 THEN 1 ELSE 0 END) AS hp_dots,
            SUM(CASE WHEN is_wicket = 1 AND dismissed_player_id = striker_id THEN 1 ELSE 0 END) AS hp_dismissals
        FROM '{pressure_pq}'
        WHERE batting_pressure_level IN ('High', 'Extreme')
        GROUP BY striker_id, match_id
    """).df()

    # Bowling match-level high pressure aggregates
    bowl_match_agg = con.execute(f"""
        SELECT 
            CAST(bowler_id AS VARCHAR) AS player_id,
            match_id,
            SUM(CASE WHEN is_legal_delivery = 1 THEN 1 ELSE 0 END) AS hp_legal_balls,
            SUM(delivery_runs) AS hp_runs_conceded,
            SUM(CASE WHEN runs = 0 AND extras_runs = 0 THEN 1 ELSE 0 END) AS hp_dots,
            SUM(CASE WHEN is_wicket = 1 AND dismissal_type NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) AS hp_wickets
        FROM '{pressure_pq}'
        WHERE bowling_pressure_level IN ('High', 'Extreme')
        GROUP BY bowler_id, match_id
    """).df()

    logger.info(
        "Validation inputs loaded: %d ranked batters, %d ranked bowlers, %d match-batter rows, %d match-bowler rows.",
        len(batter_ratings),
        len(bowler_ratings),
        len(bat_match_agg),
        len(bowl_match_agg),
    )

    return {
        "batter_ratings": batter_ratings,
        "bowler_ratings": bowler_ratings,
        "batting_eligibility": batting_el,
        "bowling_eligibility": bowling_el,
        "ranking_components": ranking_components,
        "match_metadata": match_meta,
        "player_registry": player_reg,
        "batting_baseline": bat_baseline,
        "bowling_baseline": bowl_baseline,
        "contextual_batting_baseline": ctx_bat_baseline,
        "contextual_bowling_baseline": ctx_bowl_baseline,
        "batting_bppi": bat_bppi,
        "batting_hp": bat_hp,
        "batting_comp": bat_comp,
        "batting_rel": bat_rel,
        "bowling_bppi": bowl_bppi,
        "bowling_hp": bowl_hp,
        "bowling_comp": bowl_comp,
        "bowling_rel": bowl_rel,
        "bowling_roles": bowl_roles,
        "bat_match_agg": bat_match_agg,
        "bowl_match_agg": bowl_match_agg,
    }
