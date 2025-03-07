#!/usr/bin/env python3
# this_file: src/opero/decorators/__init__.py
"""
Decorator interfaces for the opero package.

This module provides the decorator interfaces for the opero package,
including the @opero and @opmap decorators.
"""

from opero.decorators.opero import opero
from opero.decorators.opmap import opmap

__all__ = ["opero", "opmap"]
