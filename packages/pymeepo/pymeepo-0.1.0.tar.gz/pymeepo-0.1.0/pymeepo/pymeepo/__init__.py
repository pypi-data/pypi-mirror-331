"""
pymeepo: A lightweight Python SDK for building AI agents.

This package provides tools for creating agents that can collaborate
in hierarchical structures like supervisor-worker models.
"""

__version__ = "0.1.0"

from contextlib import suppress
from importlib.metadata import PackageNotFoundError, version

with suppress(PackageNotFoundError):
    __version__ = version("pymeepo")

# Core components will be imported here once implemented
# from pymeepo.agents.base import Agent  # noqa: F401
