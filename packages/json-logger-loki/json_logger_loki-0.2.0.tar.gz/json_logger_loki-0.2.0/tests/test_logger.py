"""
Tests for the JSONLogger class from the json_logger module.

This module contains unit tests to ensure the correct functionality of the
JSONLogger, including logging behavior and integration with Loki.
"""

import json
import os
import pytest
from json_logger.logger import JSONLogger

LOG_FILE = "test.log"


@pytest.fixture
def logger():
    """Fixture that provides a JSONLogger instance."""
    return JSONLogger(log_file=LOG_FILE)


def test_log_info(logger):  # pylint: disable=W0621
    """
    Test logging functionality for the 'info' level, ensuring the log entry is written
    correctly with the expected fields in the log file.
    """
    logger_instance = logger
    logger_instance.info("Test info log", module="test")

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = f.readlines()

    assert len(logs) > 0
    log_entry = json.loads(logs[0])
    assert log_entry["level"] == "INFO"
    assert log_entry["message"] == "Test info log"
    assert log_entry["module"] == "test"


def test_no_loki_when_not_provided():
    """
    Ensures that no Loki URL or or labels are set.
    """
    logger_instance = JSONLogger(log_file=LOG_FILE)
    assert logger_instance.loki_url is None
    assert logger_instance.loki_labels is None


def test_loki_config():
    """
    Ensures that the Loki URL and labels are correct.
    """
    loki_url = "http://localhost:3100/loki/api/v1/push"
    loki_labels = {"job": "test_logger"}

    logger_instance = JSONLogger(
        log_file=LOG_FILE, loki_url=loki_url, loki_labels=loki_labels
    )

    assert logger_instance.loki_url == loki_url
    assert logger_instance.loki_labels == loki_labels


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    """
    Cleanup fixture that deletes the log file after each test.
    """
    yield
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
