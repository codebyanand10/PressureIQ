"""Central Logging System for PressureIQ.

Provides configured console and file handlers with timestamping, module names,
automatic directory creation, and duplicate handler prevention.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Safe import of Config to obtain log path and defaults
try:
    from src.config import config
except ImportError:
    # Fallback if invoked directly or out of package context
    config = None  # type: ignore


# Track configured loggers to prevent duplicate handler registration
_CONFIGURED_LOGGERS: set[str] = set()


def get_logger(name: str = "PressureIQ", log_level: Optional[str] = None) -> logging.Logger:
    """Retrieve and configure a project logger.

    Args:
        name: Name of the logger, typically __name__ of the calling module.
        log_level: Optional override for log level ('DEBUG', 'INFO', 'WARNING', 'ERROR').

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Determine log level
    if log_level is not None:
        level_str = log_level.upper()
    elif config is not None:
        level_str = config.log_level
    else:
        level_str = os.getenv("LOG_LEVEL", "INFO").upper()

    numeric_level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(numeric_level)

    # Avoid duplicate handlers if already configured on this logger
    if name in _CONFIGURED_LOGGERS or len(logger.handlers) > 0:
        return logger

    # Resolve log file path
    if config is not None:
        log_file = config.log_file
        log_dir = config.logs_dir
    else:
        root_dir = Path(__file__).resolve().parent.parent
        log_dir = root_dir / "outputs" / "logs"
        log_file = log_dir / "pressureiq.log"

    # Automatically ensure log directory exists
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        sys.stderr.write(f"Warning: Could not create log directory {log_dir}: {e}\n")

    # Formatter with timestamp, level, module, line number, message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to attach file handler for {log_file}: {e}\n")

    # Prevent propagation to root logger to avoid duplicate log lines
    logger.propagate = False

    _CONFIGURED_LOGGERS.add(name)
    return logger


def run_logger_demo() -> bool:
    """Demonstrate and verify the logging system with an initialization test."""
    test_logger = get_logger("PressureIQ.DemoTest")
    test_logger.debug("Debug level log message (system diagnostic)")
    test_logger.info("PressureIQ logging system successfully initialized")
    test_logger.warning("Sample warning test (non-critical event)")
    test_logger.error("Sample error test (handled diagnostic check)")

    # Check that log file exists and is writable
    if config is not None and config.log_file.exists():
        return True
    return False


if __name__ == "__main__":
    success = run_logger_demo()
    print(f"Logger test completed. Log file status: {'OK' if success else 'Check path'}")
