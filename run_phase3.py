"""PressureIQ - Phase 3 Master Orchestration Pipeline.

Executes match state reconstruction across all 200,999 delivery events,
builds pre- and post-delivery situations, generates aggregated innings summaries,
performs domain validation, and exports analytics-ready datasets, reports, and charts.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import config
from src.data_loader import (
    load_cleaned_ball_by_ball,
    load_cleaned_competitions,
    load_cleaned_matches,
)
from src.logger import get_logger
from src.match_state.match_state_engine import reconstruct_match_states
from src.match_state.reports import (
    generate_all_reports,
    generate_phase3_final_report,
    generate_visualizations,
)
from src.preprocessing import compute_file_hash, save_parquet, verify_raw_files_integrity

logger = get_logger("PressureIQ.RunPhase3")


def execute_phase3_pipeline(dry_run: bool = False) -> Dict[str, Any]:
    """Execute complete Phase 3 Match State Reconstruction Engine."""
    start_time = time.time()
    logger.info("=" * 80)
    logger.info(f"STARTING PRESSUREIQ PHASE 3 PIPELINE (dry_run={dry_run})")
    logger.info("=" * 80)

    raw_dir = config.data_raw_dir
    processed_dir = config.data_processed_dir
    match_state_dir = config.match_state_dir

    if not dry_run:
        match_state_dir.mkdir(parents=True, exist_ok=True)

    # 1. Verify raw source preservation before execution
    logger.info("Verifying raw source file integrity and baseline hashes...")
    raw_manifest_before = verify_raw_files_integrity(raw_dir)
    for fname, info in raw_manifest_before.items():
        logger.info(f"  Source: {fname:<35} | SHA256: {info['sha256'][:16]}...")

    # 2. Load Phase 2 cleaned datasets
    logger.info("Loading Phase 2 cleaned datasets from data/processed/...")
    cleaned_bbb = load_cleaned_ball_by_ball(use_parquet=True)
    cleaned_matches = load_cleaned_matches()
    cleaned_comps = load_cleaned_competitions()

    logger.info(f"  Loaded cleaned_ball_by_ball: {len(cleaned_bbb):,} rows")
    logger.info(f"  Loaded cleaned_matches:      {len(cleaned_matches):,} rows")
    logger.info(f"  Loaded cleaned_competitions: {len(cleaned_comps):,} rows")

    # 3. Validate required columns
    required_bbb_cols = [
        "match_id", "innings", "overid", "over_ball_num", "innings_ball_num",
        "striker_id", "bowler_id", "runs", "extras1_runs", "extras_2_runs", "extras_type", "is_wicket",
    ]
    missing_bbb = [c for c in required_bbb_cols if c not in cleaned_bbb.columns]
    if missing_bbb:
        raise ValueError(f"Cleaned ball_by_ball is missing essential columns: {missing_bbb}")

    # 4. Reconstruct match states
    logger.info("Reconstructing pre- and post-delivery match states across all innings...")
    states_df, innings_summary_df, validation_report_df = reconstruct_match_states(
        ball_by_ball=cleaned_bbb,
        matches=cleaned_matches,
        competitions=cleaned_comps,
        config=config,
    )

    validation_summary = {
        "total_deliveries": len(states_df),
        "valid_deliveries_count": int(states_df["match_state_valid"].sum()),
        "invalid_deliveries_count": int((~states_df["match_state_valid"]).sum()),
        "validity_pct": round((states_df["match_state_valid"].sum() / len(states_df)) * 100, 3),
    }

    logger.info(f"  Reconstructed Delivery States: {len(states_df):,} rows, {states_df.shape[1]} columns")
    logger.info(f"  Reconstructed Innings Summaries: {len(innings_summary_df):,} rows")
    logger.info(f"  State Constraint Validity:      {validation_summary['validity_pct']}%")

    # 5. Export processed datasets
    if not dry_run:
        logger.info("Exporting reconstructed match states to data/processed/...")

        # Match states dataset (Parquet and CSV)
        out_states_parquet = processed_dir / "match_state_reconstructed.parquet"
        save_parquet(states_df, out_states_parquet)
        out_states_csv = processed_dir / "match_state_reconstructed.csv"
        states_df.to_csv(out_states_csv, index=False)
        logger.info(f"  Saved: {out_states_parquet.name} ({len(states_df):,} rows)")

        # Innings summary dataset (Parquet and CSV)
        out_summary_parquet = processed_dir / "innings_state_summary.parquet"
        save_parquet(innings_summary_df, out_summary_parquet)
        out_summary_csv = processed_dir / "innings_state_summary.csv"
        innings_summary_df.to_csv(out_summary_csv, index=False)
        logger.info(f"  Saved: {out_summary_parquet.name} ({len(innings_summary_df):,} rows)")

        # 6. Generate diagnostic reports
        logger.info("Generating CSV diagnostic reports in outputs/match_state/...")
        reports = generate_all_reports(
            states_df=states_df,
            innings_summary_df=innings_summary_df,
            validation_report_df=validation_report_df,
            validation_summary=validation_summary,
            output_dir=match_state_dir,
        )

        # 7. Generate diagnostic charts
        logger.info("Generating visual analytics charts...")
        charts = generate_visualizations(
            states_df=states_df,
            innings_summary_df=innings_summary_df,
            output_dir=match_state_dir,
        )

    # 8. Post-execution raw source verification
    logger.info("Verifying post-execution source file preservation...")
    raw_manifest_after = verify_raw_files_integrity(raw_dir)
    for fname, info_before in raw_manifest_before.items():
        info_after = raw_manifest_after[fname]
        if info_before["sha256"] != info_after["sha256"]:
            raise RuntimeError(f"CRITICAL ERROR: Source file {fname} was modified during Phase 3 execution!")
        logger.info(f"  Preserved: {fname:<35} | Hash matches: {info_after['sha256'][:16]}... (UNTOUCHED)")

    elapsed_time = round(time.time() - start_time, 2)

    # 9. Generate final Phase 3 report
    if not dry_run:
        final_report_path = match_state_dir / "PHASE_3_FINAL_REPORT.md"
        generate_phase3_final_report(
            states_df=states_df,
            innings_summary_df=innings_summary_df,
            validation_report_df=validation_report_df,
            validation_summary=validation_summary,
            elapsed_time=elapsed_time,
            output_path=final_report_path,
        )
        logger.info(f"Saved final report to: {final_report_path}")

    logger.info("=" * 80)
    logger.info(f"PRESSUREIQ PHASE 3 COMPLETED SUCCESSFULLY IN {elapsed_time}s")
    logger.info("=" * 80)

    return {
        "status": "COMPLETED",
        "dry_run": dry_run,
        "elapsed_seconds": elapsed_time,
        "total_deliveries": len(states_df),
        "total_innings": len(innings_summary_df),
        "validity_pct": validation_summary["validity_pct"],
    }


def main() -> None:
    """CLI entrypoint for Phase 3 pipeline execution."""
    parser = argparse.ArgumentParser(description="PressureIQ Phase 3 Match State Reconstruction Engine")
    parser.add_argument("--dry-run", action="store_true", help="Simulate pipeline without writing outputs")
    args = parser.parse_args()

    try:
        execute_phase3_pipeline(dry_run=args.dry_run)
    except Exception as e:
        logger.exception(f"Phase 3 execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

