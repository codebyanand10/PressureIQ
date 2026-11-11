"""PressureIQ - Application Entry Point (Phase 0).

Initializes project configuration, validates directories, displays system status,
and logs startup diagnostics.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import config
from src.logger import get_logger

logger = get_logger("PressureIQ.Main")


def main() -> int:
    """Execute Phase 0 initialization and system health check."""
    logger.info("Initializing PressureIQ application environment...")

    print("=" * 70)
    print(f"  {config.project_name.upper()} — Phase 0 Environment Verification")
    print("=" * 70)
    print(f"Title:        {config.project_settings.get('title')}")
    print(f"Competition:  {config.project_settings.get('competition')}")
    print(f"Version:      {config.version}")
    print(f"Environment:  {config.environment}")
    print(f"Project Root: {config.project_root}")
    print(f"Log Level:    {config.log_level}")
    print("-" * 70)

    # Verify and create directory structure
    dir_status = config.validate_directories(create_missing=True)
    all_valid = all(dir_status.values())

    print("Directory Architecture Check:")
    for name, exists in dir_status.items():
        status_symbol = "✓" if exists else "✗"
        print(f"  [{status_symbol}] {name:<20}: {'Ready' if exists else 'Failed'}")

    print("-" * 70)
    if all_valid:
        print("Status: ALL DIRECTORIES INITIALIZED AND VERIFIED.")
        logger.info("Project directories successfully verified and ready.")
    else:
        print("Status: WARNING — SOME DIRECTORIES COULD NOT BE CREATED.")
        logger.warning("Directory verification detected issues.")
        return 1

    print("Phase 0 Status: Complete. Ready for Phase 1 (Dataset Exploration).")
    print("=" * 70)
    logger.info("Phase 0 execution completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

