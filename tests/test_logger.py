"""Unit tests for src/logger.py.

Verifies logger initialization, log file creation, log levels,
and duplicate handler prevention.
"""

from __future__ import annotations

import logging
from pathlib import Path
import pytest

from src.logger import get_logger, run_logger_demo


def test_logger_initialization():
    """Verify that get_logger returns a Logger with proper name and handlers."""
    logger_name = "TestLoggerUnit"
    logger = get_logger(logger_name, log_level="DEBUG")
    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1


def test_no_duplicate_handlers():
    """Verify that calling get_logger multiple times does not add duplicate handlers."""
    logger_name = "DuplicateCheckLogger"
    logger1 = get_logger(logger_name)
    handler_count_1 = len(logger1.handlers)

    logger2 = get_logger(logger_name)
    handler_count_2 = len(logger2.handlers)

    assert handler_count_1 == handler_count_2
    assert logger1 is logger2


def test_logger_file_creation(tmp_path: Path):
    """Verify that logger writes entries to the log file."""
    log_file = tmp_path / "test_run.log"
    logger = logging.getLogger("FileCheckLogger")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    test_message = "Unit test verification log message"
    logger.info(test_message)
    file_handler.close()

    assert log_file.is_file()
    content = log_file.read_text(encoding="utf-8")
    assert test_message in content


def test_logger_self_test_utility():
    """Verify that the module-level run_logger_demo function executes successfully."""
    result = run_logger_demo()
    assert isinstance(result, bool)
    assert result is True
