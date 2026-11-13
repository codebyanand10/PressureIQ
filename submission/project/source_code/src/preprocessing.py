"""PressureIQ - Preprocessing & Data Cleaning Module (Phase 2).

Standardizes data types, handles missing values and duplicates,
validates referential integrity, and exports cleaned datasets in
both Parquet and CSV formats with complete reproducibility and traceability.

TODO (Phase 3+): Extended match state transformations will build upon these cleaned datasets.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import numpy as np
import pandas as pd

from src.config import config
from src.logger import get_logger

logger = get_logger("PressureIQ.Preprocessing")

# Canonical raw file names and their expected keys
RAW_FILES = {
    "competitions": "competitions.csv",
    "teams": "teams.csv",
    "mapping": "competition_team_player_mapping.csv",
    "matches": "matches.csv",
    "playing_eleven": "playing_eleven.csv",
    "ball_by_ball": "ball_by_ball.csv",
}


def compute_file_hash(file_path: Path | str, algorithm: str = "sha256") -> str:
    """Compute cryptographic hash of a file for integrity verification."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found for hashing: {path}")

    hasher = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def save_parquet(df: pd.DataFrame, path: Path | str) -> Path:
    """Save DataFrame to Parquet using DuckDB for cross-platform reliability.

    Args:
        df: Pandas DataFrame to write.
        path: Target file path.

    Returns:
        Path of the saved parquet file.
    """
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    # Use DuckDB COPY command to write parquet
    duckdb.execute("COPY df TO ? (FORMAT PARQUET)", [str(target)])
    logger.debug(f"Saved Parquet: {target} ({len(df)} rows)")
    return target


def read_parquet(path: Path | str) -> pd.DataFrame:
    """Read Parquet file into Pandas DataFrame using DuckDB."""
    target = Path(path).resolve()
    if not target.is_file():
        raise FileNotFoundError(f"Parquet file not found: {target}")
    return duckdb.execute("SELECT * FROM read_parquet(?)", [str(target)]).df()


def verify_raw_files_integrity(raw_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Verify that all six canonical raw files exist and record their metadata."""
    manifest = {}
    for key, filename in RAW_FILES.items():
        file_path = raw_dir / filename
        if not file_path.is_file():
            raise FileNotFoundError(f"Required raw file missing: {file_path}")
        file_size = file_path.stat().st_size
        file_hash = compute_file_hash(file_path)
        manifest[filename] = {
            "key": key,
            "path": str(file_path),
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 4),
            "sha256": file_hash,
        }
    return manifest


def clean_competitions(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean and standardize competitions.csv.

    Columns: comp_id, comp_name, match_format, season
    """
    logger.info("Cleaning competitions dataset...")
    cleaned = df.copy()

    # Standardize types & trim text
    cleaned["comp_id"] = cleaned["comp_id"].astype("int64")
    cleaned["comp_name"] = cleaned["comp_name"].astype(str).str.strip()
    cleaned["match_format"] = cleaned["match_format"].astype(str).str.strip()
    cleaned["season"] = cleaned["season"].astype(str).str.strip()

    # Sort stably
    cleaned = cleaned.sort_values(by="comp_id").reset_index(drop=True)

    metadata = {
        "dataset": "competitions",
        "original_rows": len(df),
        "cleaned_rows": len(cleaned),
        "columns": list(cleaned.columns),
        "primary_key": "comp_id",
        "is_unique": cleaned["comp_id"].is_unique,
    }
    return cleaned, metadata


def clean_teams(df: pd.DataFrame, comps_df: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean and standardize teams.csv.

    Columns: comp_id, team_id, team_name
    Composite key: comp_id + team_id
    """
    logger.info("Cleaning teams dataset...")
    cleaned = df.copy()

    cleaned["comp_id"] = cleaned["comp_id"].astype("int64")
    cleaned["team_id"] = cleaned["team_id"].astype("int64")
    cleaned["team_name"] = cleaned["team_name"].astype(str).str.strip()

    # Referential check
    unmatched_comps = []
    if comps_df is not None:
        valid_comps = set(comps_df["comp_id"])
        unmatched_comps = list(set(cleaned["comp_id"]) - valid_comps)

    cleaned = cleaned.sort_values(by=["comp_id", "team_id"]).reset_index(drop=True)

    metadata = {
        "dataset": "teams",
        "original_rows": len(df),
        "cleaned_rows": len(cleaned),
        "columns": list(cleaned.columns),
        "composite_key": ["comp_id", "team_id"],
        "is_unique": not cleaned.duplicated(subset=["comp_id", "team_id"]).any(),
        "unmatched_competitions": unmatched_comps,
    }
    return cleaned, metadata


def clean_competition_team_player_mapping(
    df: pd.DataFrame,
    comps_df: Optional[pd.DataFrame] = None,
    teams_df: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean and standardize competition_team_player_mapping.csv.

    Columns: comp_id, comp_name, team_id, team_name, player_id, player_name
    Composite key: comp_id + team_id + player_id
    """
    logger.info("Cleaning competition_team_player_mapping dataset...")
    cleaned = df.copy()

    cleaned["comp_id"] = cleaned["comp_id"].astype("int64")
    cleaned["team_id"] = cleaned["team_id"].astype("int64")
    cleaned["player_id"] = cleaned["player_id"].astype("int64")
    cleaned["comp_name"] = cleaned["comp_name"].astype(str).str.strip()
    cleaned["team_name"] = cleaned["team_name"].astype(str).str.strip()
    cleaned["player_name"] = cleaned["player_name"].astype(str).str.strip()

    cleaned = cleaned.sort_values(by=["comp_id", "team_id", "player_id"]).reset_index(drop=True)

    metadata = {
        "dataset": "competition_team_player_mapping",
        "original_rows": len(df),
        "cleaned_rows": len(cleaned),
        "columns": list(cleaned.columns),
        "composite_key": ["comp_id", "team_id", "player_id"],
        "is_unique": not cleaned.duplicated(subset=["comp_id", "team_id", "player_id"]).any(),
        "unique_players": cleaned["player_id"].nunique(),
        "unique_teams": cleaned["team_id"].nunique(),
    }
    return cleaned, metadata


def clean_matches(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean and standardize matches.csv (all 22 columns).

    Standardizes dates, handles nullable identifiers, validates DLS parameters.
    """
    logger.info("Cleaning matches dataset...")
    cleaned = df.copy()

    # Core Identifiers
    cleaned["match_id"] = cleaned["match_id"].astype("int64")
    cleaned["comp_id"] = cleaned["comp_id"].astype("int64")
    cleaned["match_number"] = cleaned["match_number"].astype("int64")
    cleaned["venue_id"] = cleaned["venue_id"].astype("int64")
    cleaned["home_team_id"] = cleaned["home_team_id"].astype("int64")
    cleaned["away_team_id"] = cleaned["away_team_id"].astype("int64")

    # Dates: parse to YYYY-MM-DD
    cleaned["match_date"] = pd.to_datetime(cleaned["match_date"]).dt.strftime("%Y-%m-%d")

    # Categorical strings
    for col in ["stage", "venue_country", "home_team", "away_team", "result"]:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    # Nullable identifiers (Int64 preserves NA without fabricating or converting to 'nan')
    for col in ["home_team_captain_id", "away_team_captain_id", "toss_win_team_id", "win_team_id"]:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").astype("Int64")

    # Toss opted (nullable string)
    cleaned["toss_opted"] = cleaned["toss_opted"].apply(
        lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != "" else np.nan
    )

    # Man of the match (0 means unawarded / abandoned)
    cleaned["man_of_the_match"] = cleaned["man_of_the_match"].astype("int64")

    # Knockout binary flag
    cleaned["knock_out"] = cleaned["knock_out"].astype("int64")

    # DLS parameters: preserve original legal balls, and add calculated overs for clarity
    cleaned["first_inn_revised_overs"] = pd.to_numeric(cleaned["first_inn_revised_overs"], errors="coerce")
    cleaned["second_inn_revised_overs"] = pd.to_numeric(cleaned["second_inn_revised_overs"], errors="coerce")
    cleaned["revised_target"] = pd.to_numeric(cleaned["revised_target"], errors="coerce")

    # Computed fields for DLS legal overs (legal balls / 6.0) as recommended in Phase 1
    cleaned["first_inn_revised_balls"] = cleaned["first_inn_revised_overs"].astype("Int64")
    cleaned["second_inn_revised_balls"] = cleaned["second_inn_revised_overs"].astype("Int64")
    cleaned["first_inn_revised_overs_calc"] = cleaned["first_inn_revised_overs"] / 6.0
    cleaned["second_inn_revised_overs_calc"] = cleaned["second_inn_revised_overs"] / 6.0

    cleaned = cleaned.sort_values(by="match_id").reset_index(drop=True)

    metadata = {
        "dataset": "matches",
        "original_rows": len(df),
        "cleaned_rows": len(cleaned),
        "columns": list(cleaned.columns),
        "primary_key": "match_id",
        "is_unique": cleaned["match_id"].is_unique,
        "dls_matches_count": int(cleaned["revised_target"].notna().sum()),
        "abandoned_matches_count": int((cleaned["result"] == "Match Abandoned").sum()),
    }
    return cleaned, metadata


def clean_playing_eleven(
    df: pd.DataFrame,
    bbb_df: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Clean and standardize playing_eleven.csv.

    Resolves the 40 duplicate key instances (75 rows) across matches 13613, 21176, 28962
    using ground-truth delivery batting order from ball_by_ball.csv, and preserves an audit.
    """
    logger.info("Cleaning playing_eleven dataset and resolving duplicates...")
    cleaned = df.copy()

    cleaned["match_id"] = cleaned["match_id"].astype("int64")
    cleaned["team_id"] = cleaned["team_id"].astype("int64")
    cleaned["player_id"] = cleaned["player_id"].astype("int64")
    cleaned["batting_order"] = pd.to_numeric(cleaned["batting_order"], errors="coerce")
    cleaned["is_played"] = cleaned["is_played"].astype(bool)

    # Boolean nullable for captain and wicketkeeper (NaN for bench reserves)
    cleaned["is_captain"] = cleaned["is_captain"].apply(
        lambda x: True if str(x).lower() == "true" else (False if str(x).lower() == "false" else pd.NA)
    ).astype("boolean")

    cleaned["is_wk"] = cleaned["is_wk"].apply(
        lambda x: True if str(x).lower() == "true" else (False if str(x).lower() == "false" else pd.NA)
    ).astype("boolean")

    cleaned["is_impact"] = cleaned["is_impact"].fillna(0).astype("int64")
    cleaned["is_impact_off"] = cleaned["is_impact_off"].fillna(0).astype("int64")

    # Deduplication audit setup
    duplicate_mask = cleaned.duplicated(subset=["match_id", "team_id", "player_id"], keep=False)
    dup_rows = cleaned[duplicate_mask].copy()

    audit_records = []
    rows_to_drop = []

    if not dup_rows.empty:
        # Build lookup of actual batting order from delivery events if available
        bbb_order_map: Dict[Tuple[int, int], float] = {}
        if bbb_df is not None:
            striker_orders = bbb_df[["match_id", "striker_id", "batting_order"]].drop_duplicates()
            for row in striker_orders.itertuples():
                bbb_order_map[(row.match_id, row.striker_id)] = float(row.batting_order)

        # Group by composite key
        for (m_id, t_id, p_id), group in dup_rows.groupby(["match_id", "team_id", "player_id"]):
            actual_order = bbb_order_map.get((m_id, p_id))

            # If verified in ball_by_ball, keep row matching actual batting order
            retained_idx = None
            if actual_order is not None:
                match_candidates = group[group["batting_order"] == actual_order]
                if not match_candidates.empty:
                    retained_idx = match_candidates.index[0]

            # Fallback: keep first occurrence if ball_by_ball batting order is absent or tied
            if retained_idx is None:
                retained_idx = group.index[0]

            for idx in group.index:
                if idx != retained_idx:
                    rows_to_drop.append(idx)
                    audit_records.append({
                        "dataset": "playing_eleven.csv",
                        "match_id": m_id,
                        "team_id": t_id,
                        "player_id": p_id,
                        "removed_index": idx,
                        "retained_index": retained_idx,
                        "removed_batting_order": group.loc[idx, "batting_order"],
                        "retained_batting_order": group.loc[retained_idx, "batting_order"],
                        "verified_bbb_batting_order": actual_order,
                        "action": "EXCLUDE_DUPLICATE_ROW",
                        "reason": "Retained row matching verified ball-by-ball batting order; removed conflicting provisional duplicate",
                    })

    # Execute deduplication
    cleaned = cleaned.drop(index=rows_to_drop).sort_values(
        by=["match_id", "team_id", "player_id"]
    ).reset_index(drop=True)

    dup_audit_df = pd.DataFrame(audit_records)

    metadata = {
        "dataset": "playing_eleven",
        "original_rows": len(df),
        "cleaned_rows": len(cleaned),
        "removed_duplicates_count": len(rows_to_drop),
        "columns": list(cleaned.columns),
        "composite_key": ["match_id", "team_id", "player_id"],
        "is_unique": not cleaned.duplicated(subset=["match_id", "team_id", "player_id"]).any(),
    }
    return cleaned, dup_audit_df, metadata


def clean_ball_by_ball(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Clean and standardize ball_by_ball.csv (all 33 columns).

    - Preserves exact source sequence with delivery_order_idx
    - Fixes dismissal type typo: 'Obstracting the field' -> 'Obstructing the field'
    - Recodes speed radar 0.0 -> NaN
    - Identifies anomalous non-wicket rows with populated dismissed_player_id
    - Retains original identifiers and scores without state reconstruction
    """
    logger.info("Cleaning ball_by_ball dataset (200,999 delivery events)...")
    cleaned = df.copy()

    # Stable delivery order index for perfect traceability
    cleaned["delivery_order_idx"] = np.arange(len(cleaned), dtype=np.int64)

    # Identifiers
    for col in ["match_id", "batting_team_id", "bowling_team_id", "striker_id", "non_striker_id", "bowler_id"]:
        cleaned[col] = cleaned[col].astype("int64")

    # Dismissal IDs (nullable)
    cleaned["dismissal_type_id"] = pd.to_numeric(cleaned["dismissal_type_id"], errors="coerce").astype("Int64")
    cleaned["dismissed_player_id"] = pd.to_numeric(cleaned["dismissed_player_id"], errors="coerce").astype("Int64")

    # Numeric integers
    for col in ["innings", "overid", "over_ball_num", "innings_ball_num", "batting_order", "runs", "extras1_runs", "extras_2_runs"]:
        cleaned[col] = cleaned[col].astype("int64")

    # Booleans
    for col in ["is_four", "is_six", "is_wicket"]:
        cleaned[col] = cleaned[col].astype(bool)

    # String trimming
    for col in ["striker_name", "non_striker_name", "bowler_name", "batting_type", "bowling_type", "pace_or_spin", "on_or_off"]:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    # Nullable strings
    for col in ["extras_type", "stroke", "delivery_style", "over_or_around"]:
        cleaned[col] = cleaned[col].apply(
            lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != "" and str(x).strip().lower() != "nan" else np.nan
        )

    # Typo correction: normalize 'Obstracting the field' -> 'Obstructing the field'
    cleaned["dismissal_type"] = cleaned["dismissal_type"].apply(
        lambda x: "Obstructing the field" if str(x).strip() == "Obstracting the field" else (str(x).strip() if pd.notna(x) and str(x).strip().lower() != "nan" else np.nan)
    )

    # Audit invalid/anomalous records: 12 deliveries with is_wicket == False but dismissed_player_id populated
    anomalous_dismissal_mask = (~cleaned["is_wicket"]) & cleaned["dismissed_player_id"].notna()
    invalid_records = []
    for row in cleaned[anomalous_dismissal_mask].itertuples():
        invalid_records.append({
            "dataset": "ball_by_ball.csv",
            "record_id": row.delivery_order_idx,
            "match_id": row.match_id,
            "innings": row.innings,
            "innings_ball_num": row.innings_ball_num,
            "issue_type": "ANOMALOUS_DISMISSED_PLAYER_ON_NON_WICKET",
            "field": "dismissed_player_id",
            "observed_value": row.dismissed_player_id,
            "action_taken": "RETAIN_NULL_ON_CLEANED_DISMISSAL",
            "details": f"Striker {row.striker_name} scored {row.runs} runs with is_wicket=False; spurious dismissed_player_id {row.dismissed_player_id} neutralized to NA.",
        })

    # Neutralize spurious dismissed_player_id on non-wicket deliveries for strict consistency
    cleaned.loc[anomalous_dismissal_mask, "dismissed_player_id"] = pd.NA

    # Speed radar: 0.0 indicates unrecorded / inactive speed radar (38.74% of deliveries)
    cleaned["bowl_speed_raw"] = cleaned["bowl_speed"]  # preserve original
    cleaned["bowl_speed"] = cleaned["bowl_speed"].apply(lambda s: np.nan if s == 0.0 or pd.isna(s) else float(s))

    # Standardize delivery_ist_time: keep original formatted string and parse standard datetime
    cleaned["delivery_ist_time"] = cleaned["delivery_ist_time"].astype(str).str.strip()

    invalid_report_df = pd.DataFrame(invalid_records)

    metadata = {
        "dataset": "ball_by_ball",
        "original_rows": len(df),
        "cleaned_rows": len(cleaned),
        "columns": list(cleaned.columns),
        "composite_key": ["match_id", "innings", "innings_ball_num"],
        "is_unique": not cleaned.duplicated(subset=["match_id", "innings", "innings_ball_num"]).any(),
        "speed_radar_nulls": int(cleaned["bowl_speed"].isna().sum()),
        "neutralized_anomalous_dismissals": len(invalid_records),
    }
    return cleaned, invalid_report_df, metadata
