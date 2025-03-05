"""
This module provides the main entry point for the agentopera.chatflow package.
It includes logger names for trace and event logs, and retrieves the package version.
"""

import importlib.metadata

TRACE_LOGGER_NAME = "agentopera.chatflow"
"""Logger name for trace logs."""

EVENT_LOGGER_NAME = "agentopera.chatflow.events"
"""Logger name for event logs."""

__version__ = importlib.metadata.version("agentopera.chatflow")
