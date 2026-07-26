"""
Tests for server/logging/server_logger.py
"""
import sys, os
import logging
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, _ROOT)

from server.logging.server_logger import log


def test_log_info_captured(caplog):
    with caplog.at_level(logging.INFO, logger="server"):
        log("test message")
    assert "test message" in caplog.text


def test_log_warning_captured(caplog):
    with caplog.at_level(logging.WARNING, logger="server"):
        log("something bad", level="warning")
    assert "something bad" in caplog.text


def test_log_warning_label(caplog):
    with caplog.at_level(logging.WARNING, logger="server"):
        log("warn msg", level="warning")
    assert "WARNING" in caplog.text


def test_log_info_label(caplog):
    with caplog.at_level(logging.INFO, logger="server"):
        log("info msg")
    assert "INFO" in caplog.text


def test_log_does_not_raise():
    log("no crash")
