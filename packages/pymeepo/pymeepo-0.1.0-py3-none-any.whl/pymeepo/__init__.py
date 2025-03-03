"""
Meepo SDK: A flexible, extensible framework for creating, deploying,
and orchestrating AI agents.

This package provides a comprehensive set of tools for building intelligent
agents that can leverage various LLM providers and collaborate in hierarchies.
"""

__version__ = "0.1.0"

from contextlib import suppress
from importlib.metadata import PackageNotFoundError, version

with suppress(PackageNotFoundError):
    __version__ = version("pymeepo")

# Core components will be imported here once implemented
# from pymeepo.agents.base import Agent  # noqa: F401
