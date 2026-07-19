"""
Tests for server/logging/server_logger.py
"""
import sys, os
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, _ROOT)

from server.logging.server_logger import log


def test_log_does_not_raise(capsys):
    log("test message")
    captured = capsys.readouterr()
    assert "test message" in captured.out


def test_log_includes_timestamp(capsys):
    log("hello")
    out = capsys.readouterr().out
    # timestamp format is [HH:MM:SS]
    assert "[" in out and "]" in out


def test_log_flushes(capsys):
    log("flush test")
    out = capsys.readouterr().out
    assert "flush test" in out
