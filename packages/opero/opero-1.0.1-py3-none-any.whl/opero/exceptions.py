#!/usr/bin/env python3
# this_file: src/opero/exceptions.py
"""
Exception classes for the opero package.

This module defines custom exceptions used throughout the opero package.
"""


class OperoError(Exception):
    """Base class for all custom exceptions in opero."""


class AllFailedError(OperoError):
    """Raised when all fallback operations have failed."""

    def __init__(self, message="All fallback operations failed."):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
