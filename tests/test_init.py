"""Tests for accqsure __init__.py module."""
import logging
import pytest

# Import to trigger the trace method addition
import accqsure  # noqa: F401
from accqsure import logger


class InitTests:
    """Tests for __init__.py module."""

    def test_trace_logging(self):
        """Test trace logging functionality."""
        # Test that trace method exists and can be called
        assert hasattr(logger, 'trace')
        assert callable(logger.trace)
        
        # TRACE level is added in __init__.py
        TRACE = 5
        # Test trace logging when enabled
        logger.setLevel(TRACE)
        logger.trace("Test trace message")
        
        # Test trace logging when disabled (should not error)
        logger.setLevel(logging.INFO)
        logger.trace("Test trace message disabled")

