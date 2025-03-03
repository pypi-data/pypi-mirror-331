import pytest
import logging
from tracecolor import MLog
import io
import sys
import re

def test_mlog_creation():
    """Test basic logger creation."""
    logger = MLog("test_logger")
    assert isinstance(logger, MLog)
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"

def test_log_levels():
    """Test all log levels are properly defined."""
    logger = MLog("test_logger")
    assert logger.TRACE_LEVEL == 5
    assert logging.getLevelName(logger.TRACE_LEVEL) == "TRACE"
    
    # Test standard levels still work
    assert logger.level <= logging.DEBUG
    assert logger.level <= logging.INFO
    assert logger.level <= logging.WARNING
    assert logger.level <= logging.ERROR
    assert logger.level <= logging.CRITICAL

def test_log_output(capsys):
    """Test that log messages are properly formatted."""
    # Redirect stdout to capture log messages
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        logger = MLog("test_output")
        logger.info("Test info message")
        
        output = sys.stdout.getvalue()
        # Check for color codes and basic format
        assert "I |" in output
        assert "Test info message" in output
        
        # Check timestamp format using regex
        timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}"
        assert re.search(timestamp_pattern, output) is not None
        
    finally:
        sys.stdout = old_stdout

def test_trace_rate_limiting():
    """Test that trace messages are rate-limited."""
    logger = MLog("test_rate_limit")
    
    # Capture all handler calls
    calls = []
    
    class MockHandler(logging.Handler):
        def emit(self, record):
            calls.append(record)
    
    mock_handler = MockHandler()
    logger.handlers = [mock_handler]  # Replace the default handler
    
    # Two immediate trace calls should result in only one log
    logger.trace("First trace message")
    logger.trace("Second trace message")
    
    assert len(calls) == 1
    assert calls[0].message == "First trace message"