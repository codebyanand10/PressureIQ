"""PressureIQ Phase 12 Runner – Final Audit & Competition Submission Packager.

Executes comprehensive audits across all project phases, verifies ranking
integrity and statistical validity, and prepares the official submission bundle.

Usage:
    python run_phase12.py --dry-run
    python run_phase12.py --audit
    python run_phase12.py --package
    python run_phase12.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Set MPLCONFIGDIR to writable cache directory
PROJECT_ROOT = Path(__file__).resolve().parent
mpl_cache = PROJECT_ROOT / "outputs" / ".mpl_cache"
mpl_cache.mkdir(parents=True, exist_ok=True)
import os
os.environ["MPLCONFIGDIR"] = str(mpl_cache)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.final_audit.competition_requirements import CompetitionRequirementsAuditor
from src.final_audit.dashboard_audit import DashboardAuditor
from src.final_audit.data_integrity_audit import DataIntegrityAuditor
from src.final_audit.final_report import FinalReportGenerator
from src.final_audit.methodology_audit import MethodologyAuditor
from src.final_audit.project_inventory import ProjectInventory
from src.final_audit.ranking_audit import RankingAuditor
from src.final_audit.reproducibility_audit import ReproducibilityAuditor
from src.final_audit.statistical_audit import StatisticalAuditor
from src.final_audit.submission_packager import SubmissionPackager
from src.logger import get_logger

logger = get_logger("PressureIQ.Phase12")


def run_dry_run(root_dir: Path) -> bool:
    """Verify presence of required inputs, configurations, and phase outputs."""
    print("=" * 70)
    print("PRESSUREIQ PHASE 12: DRY RUN VERIFICATION")
    print("=" * 70)

    inventory = ProjectInventory(root_dir).scan()
    print(f"Total files inventoried: {inventory.total_files}")
    print(f"Total size: {inventory.total_size_bytes / (1024*1024):.2f} MB")

    if inventory.missing_required_files:
        print("\n[ERROR] Missing required project files:")
        for mf in inventory.missing_required_files:
            print(f"  - {mf}")
        return False

    print("\n[SUCCESS] All core assets, configurations, and phase deliverables verified.")
    return True


def run_audit(root_dir: Path) -> dict:
    """Run all analytical, ranking, data integrity, and documentation audits."""
    print("=" * 70)
    print("PRESSUREIQ PHASE 12: COMPREHENSIVE PROJECT AUDIT")
    print("=" * 70)

    # 1. Project Inventory
    print("\n[1/7] Scanning project inventory...")
    inventory = ProjectInventory(root_dir).scan()
    print(f"  -> Inventoried {inventory.total_files} files.")

    # 2. Competition Requirements
    print("\n[2/7] Checking competition requirements traceability...")
    req_auditor = CompetitionRequirementsAuditor(root_dir)
    req_result = req_auditor.audit()
    print(f"  -> {req_result.pass_count} Passed, {req_result.warning_count} Warnings, {req_result.fail_count} Failed.")

    # 3. Ranking Audit
    print("\n[3/7] Auditing top 10 rankings integrity & concordance...")
    ranking_auditor = RankingAuditor(root_dir)
    rank_summary = ranking_auditor.audit()
    print(f"  -> Batters verified: {rank_summary.batting_verified}")
    print(f"  -> Bowlers verified: {rank_summary.bowling_verified}")
    print(f"  -> Cross-format concordance: {rank_summary.cross_format_concordance}")

    # 4. Data Integrity
    print("\n[4/7] Auditing data pipelines, ball cardinality & causality...")
    data_auditor = DataIntegrityAuditor(root_dir)
    data_report = data_auditor.audit()
    print(f"  -> Matches: {data_report.match_count}, Deliveries: {data_report.delivery_count}")
    print(f"  -> Duplicate delivery keys: {data_report.duplicate_deliveries_count}")
    print(f"  -> Raw files intact: {data_report.raw_files_intact}")

    # 5. Statistical Validity
    print("\n[5/7] Auditing statistical robustness scorecard & leakage...")
    stat_auditor = StatisticalAuditor(root_dir)
    stat_result = stat_auditor.audit()
    print(f"  -> Passed dimensions: {stat_result.dimensions_passed}/{stat_result.total_dimensions_checked}")
    print(f"  -> Data leakage detected: {stat_result.data_leakage_detected}")
    print(f"  -> Batting status: {stat_result.batting_readiness}, Bowling status: {stat_result.bowling_readiness}")

    # 6. Methodology & Mathematics
    print("\n[6/7] Auditing mathematical formula alignment...")
    method_auditor = MethodologyAuditor(root_dir)
    method_report = method_auditor.audit()
    print(f"  -> Fully aligned: {method_report.is_fully_aligned}")
    print(f"  -> Verified components: {len(method_report.verification_items)}")

    # 7. Dashboard & Telemetry
    print("\n[7/7] Auditing Streamlit dashboard pages & services...")
    dash_auditor = DashboardAuditor(root_dir)
    dash_result = dash_auditor.audit()
    print(f"  -> App entry valid: {dash_result.app_entrypoint_valid}")
    print(f"  -> Pages passing: {dash_result.pages_passing}/{dash_result.total_pages}")

    # Reproducibility
    repro_auditor = ReproducibilityAuditor(root_dir)
    repro_result = repro_auditor.audit()

    return {
        "inventory": inventory,
        "requirements": req_result,
        "ranking_summary": rank_summary,
        "integrity": data_report,
        "statistical": stat_result,
        "methodology": method_report,
        "dashboard": dash_result,
        "reproducibility": repro_result,
    }


def run_package(root_dir: Path) -> bool:
    """Assemble official submission directory."""
    print("=" * 70)
    print("PRESSUREIQ PHASE 12: SUBMISSION PACKAGING")
    print("=" * 70)

    # Generate dashboard visual screenshots
    dash_auditor = DashboardAuditor(root_dir)
    print("Generating dashboard visual screenshots...")
    shots = dash_auditor.generate_dashboard_evidence_screenshots()
    print(f"  -> Created {len(shots)} screenshots in submission/evidence/Final_Dashboard_Screenshots/")

    # Assemble package
    packager = SubmissionPackager(root_dir)
    print("Packaging deliverables...")
    pkg_result = packager.package()
    print(f"  -> Created {len(pkg_result.files_created)} submission files.")
    print(f"  -> Submission package ready at: {pkg_result.submission_dir}")
    return pkg_result.is_complete


def run_full(root_dir: Path) -> bool:
    """Run full Phase 12 sequence: Audit -> Packaging -> Final Report."""
    print("=" * 70)
    print("PRESSUREIQ PHASE 12: FULL AUDIT & SUBMISSION PREPARATION")
    print("=" * 70)

    # 1. Run Comprehensive Audit
    audit_data = run_audit(root_dir)

    # 2. Package Deliverables & Visuals
    print("\n" + "=" * 70)
    dash_auditor = DashboardAuditor(root_dir)
    shots = dash_auditor.generate_dashboard_evidence_screenshots()
    packager = SubmissionPackager(root_dir)
    pkg_result = packager.package()

    # 3. Generate Master Audit Report
    print("\n" + "=" * 70)
    print("Generating Master Audit Report (submission/FINAL_AUDIT_REPORT.md)...")
    report_gen = FinalReportGenerator(root_dir)
    rep_path = report_gen.generate_report(
        inventory=audit_data["inventory"],
        requirements=audit_data["requirements"],
        ranking_summary=audit_data["ranking_summary"],
        integrity=audit_data["integrity"],
        statistical=audit_data["statistical"],
        methodology=audit_data["methodology"],
        dashboard=audit_data["dashboard"],
        reproducibility=audit_data["reproducibility"],
        packaging=pkg_result,
    )
    print(f"  -> Report written to: {rep_path}")
    print("\n[SUCCESS] Phase 12 execution successfully completed.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="PressureIQ Phase 12 Final Audit Runner")
    parser.add_argument("--dry-run", action="store_true", help="Verify input files and configurations")
    parser.add_argument("--audit", action="store_true", help="Run audit checks only")
    parser.add_argument("--package", action="store_true", help="Assemble submission folder only")

    args = parser.parse_args()

    if args.dry_run:
        success = run_dry_run(PROJECT_ROOT)
    elif args.audit:
        results = run_audit(PROJECT_ROOT)
        success = results["requirements"].is_fully_passing
    elif args.package:
        success = run_package(PROJECT_ROOT)
    else:
        success = run_full(PROJECT_ROOT)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

