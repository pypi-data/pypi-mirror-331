#!/usr/bin/env python3
# this_file: src/opero/utils/logging.py
"""
Logging utility functions for the opero package.

This module provides utility functions for logging in the opero package.
"""

import logging
import sys
from typing import TextIO

# Default logger
logger = logging.getLogger("opero")


def configure_logging(
    level: int | str = logging.INFO,
    format_string: str | None = None,
    stream: TextIO | None = None,
    verbose: bool = False,
) -> logging.Logger:
    """
    Configure logging for the opero package.

    Args:
        level: Logging level
        format_string: Format string for log messages
        stream: Stream to log to
        verbose: Whether to enable verbose logging

    Returns:
        Configured logger
    """
    # Set the logging level
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    # Set the format string
    if format_string is None:
        if verbose:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            format_string = "%(levelname)s: %(message)s"

    # Configure the logger
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(logging.Formatter(format_string))

    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger for the opero package.

    Args:
        name: Name of the logger

    Returns:
        Logger
    """
    if name is None:
        return logger

    return logging.getLogger(f"opero.{name}")
