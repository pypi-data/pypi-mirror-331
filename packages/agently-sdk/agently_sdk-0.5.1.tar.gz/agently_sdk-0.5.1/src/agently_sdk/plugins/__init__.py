"""
Plugin system for Agently - provides base classes and utilities for creating plugins.

This package contains the core components needed to develop plugins for the Agently framework.
"""

from agently_sdk.plugins.base import Plugin
from agently_sdk.plugins.decorators import agently_function, kernel_function, track_function_calls
from agently_sdk.plugins.variables import (
    ExecutionResult,
    PluginVariable,
    VariableValidation,
    get_result,
)

__all__ = [
    "Plugin",
    "PluginVariable",
    "VariableValidation",
    "agently_function",
    "kernel_function",
    "ExecutionResult",
    "track_function_calls",
    "get_result",
]
