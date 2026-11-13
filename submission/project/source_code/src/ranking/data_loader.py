"""Data loader module for Phase 8 Unified Player Rating & Ranking Engine.

Loads validated Parquet datasets from:
- Phase 6 (Batting Performance Under Pressure)
- Phase 7 (Bowling Performance Under Pressure)
- Phase 5 (Player Baselines and Master Registry)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Tuple
import duckdb
import pandas as pd

from src.config import config

logger = logging.getLogger(__name__)


def load_ranking_inputs() -> Dict[str, pd.DataFrame]:
    """Load and validate all necessary Phase 5, Phase 6, and Phase 7 input datasets.

    Returns:
        Dictionary of DataFrames with keys:
        - batting_bppi
        - batting_hp
        - batting_comparison
        - batting_reliability
        - bowling_bppi
        - bowling_hp
        - bowling_comparison
        - bowling_reliability
        - bowling_roles
        - player_registry
        - batting_baseline
        - bowling_baseline
    """
    con = duckdb.connect()
    inputs: Dict[str, pd.DataFrame] = {}

    files_to_load = [
        ("batting_bppi", config.batting_pressure_data_dir / "batter_pressure_performance_index.parquet"),
        ("batting_hp", config.batting_pressure_data_dir / "batter_high_pressure_performance.parquet"),
        ("batting_comparison", config.batting_pressure_data_dir / "batter_baseline_comparison.parquet"),
        ("batting_reliability", config.batting_pressure_data_dir / "batter_pressure_reliability.parquet"),
        ("bowling_bppi", config.bowling_pressure_data_dir / "bowler_pressure_performance_index.parquet"),
        ("bowling_hp", config.bowling_pressure_data_dir / "bowler_high_pressure_performance.parquet"),
        ("bowling_comparison", config.bowling_pressure_data_dir / "bowler_baseline_comparison.parquet"),
        ("bowling_reliability", config.bowling_pressure_data_dir / "bowler_pressure_reliability.parquet"),
        ("bowling_roles", config.bowling_pressure_data_dir / "bowler_role_analysis.parquet"),
        ("player_registry", config.baselines_data_dir / "player_registry.parquet"),
        ("batting_baseline", config.baselines_data_dir / "batting_overall_baseline.parquet"),
        ("bowling_baseline", config.baselines_data_dir / "bowling_overall_baseline.parquet"),
    ]

    for key, path in files_to_load:
        if not path.is_file():
            raise FileNotFoundError(f"Required Phase dataset not found: {path}")
        df = con.execute("SELECT * FROM read_parquet([?])", [str(path)]).df()
        inputs[key] = df
        logger.info("Loaded %s (%d records) from %s", key, len(df), path.name)

    return inputs

