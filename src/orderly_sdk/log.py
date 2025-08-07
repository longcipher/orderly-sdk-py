
"""
Logging module for Orderly SDK.

Provides a pre-configured loguru logger and a function to set log level.
"""

import sys

from loguru import logger

logger.add(
    sys.stderr,
    format='{{"timestamp":"{time}","level":"{level}","message":"{message}"}}',
    level="INFO",
)


def set_level(level):
    """
    Set the log level for the SDK logger.

    Args:
        level (str): Log level (e.g., "INFO", "DEBUG").
    """
    global logger
    logger.remove()
    logger.add(
        sys.stderr,
        format='{{"timestamp":"{time}","level":"{level}","message":"{message}"}}',
        level=level,
    )
