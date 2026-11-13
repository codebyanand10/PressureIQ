"""PressureIQ - Data Loader Module.

Provides streamlined accessors for raw, cleaned, and integrated datasets.
Supports Parquet and CSV formats using DuckDB and Pandas.

TODO (Phase 3+): Extend with lazy loading, chunked iteration, and memory optimization.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import duckdb
import pandas as pd

from src.config import config
from src.logger import get_logger
from src.preprocessing import read_parquet

logger = get_logger("PressureIQ.DataLoader")


def load_cleaned_competitions() -> pd.DataFrame:
    """Load cleaned competitions CSV."""
    path = config.data_processed_dir / "cleaned_competitions.csv"
    return pd.read_csv(path)


def load_cleaned_teams() -> pd.DataFrame:
    """Load cleaned teams CSV."""
    path = config.data_processed_dir / "cleaned_teams.csv"
    return pd.read_csv(path)


def load_cleaned_mapping() -> pd.DataFrame:
    """Load cleaned competition team player mapping CSV."""
    path = config.data_processed_dir / "cleaned_competition_team_player_mapping.csv"
    return pd.read_csv(path)


def load_cleaned_matches() -> pd.DataFrame:
    """Load cleaned matches CSV."""
    path = config.data_processed_dir / "cleaned_matches.csv"
    return pd.read_csv(path)


def load_cleaned_playing_eleven() -> pd.DataFrame:
    """Load cleaned playing eleven lineups CSV."""
    path = config.data_processed_dir / "cleaned_playing_eleven.csv"
    return pd.read_csv(path)


def load_cleaned_ball_by_ball(use_parquet: bool = True) -> pd.DataFrame:
    """Load cleaned delivery events (Parquet or CSV)."""
    if use_parquet:
        path = config.data_processed_dir / "cleaned_ball_by_ball.parquet"
        return read_parquet(path)
    path = config.data_processed_dir / "cleaned_ball_by_ball.csv"
    return pd.read_csv(path, low_memory=False)


def load_integrated_ball_by_ball(use_parquet: bool = True) -> pd.DataFrame:
    """Load integrated ball-by-ball dataset with match and competition context."""
    if use_parquet:
        path = config.data_processed_dir / "integrated_ball_by_ball.parquet"
        return read_parquet(path)
    path = config.data_processed_dir / "integrated_ball_by_ball.csv"
    return pd.read_csv(path, low_memory=False)


def load_match_metadata(use_parquet: bool = True) -> pd.DataFrame:
    """Load integrated match metadata."""
    if use_parquet:
        path = config.data_processed_dir / "match_metadata.parquet"
        return read_parquet(path)
    path = config.data_processed_dir / "match_metadata.csv"
    return pd.read_csv(path)
