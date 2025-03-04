"""
Tests for the ExecutionResult functionality.
"""

import time

from agently_sdk.plugins import (
    ExecutionResult,
    Plugin,
    PluginVariable,
    agently_function,
    track_function_calls,
)


class SamplePluginForTests(Plugin):
    """Test plugin for ExecutionResult tests."""

    name = "test_plugin"
    description = "A plugin for testing ExecutionResult"

    test_var = PluginVariable(name="test_var", description="A test variable", default="default")

    @agently_function(action="Adding numbers")
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    @agently_function
    def greet(self, name: str) -> str:
        """Greet someone."""
        return f"Hello, {name}!"

    @agently_function(action="Using a variable")
    def use_var(self) -> str:
        """Use a plugin variable."""
        return self.test_var


def test_execution_result_enabled():
    """Test that ExecutionResult is returned when enabled."""
    # Make sure execution reporting is enabled
    track_function_calls(True)

    plugin = SamplePluginForTests()

    # Test with action specified
    result = plugin.add(2, 3)
    assert isinstance(result, ExecutionResult)
    assert result.value == 5
    assert result.action == "Adding numbers"
    assert "duration" in result.metadata
    assert result.metadata["args"] == (2, 3)

    # Test with default action (function name)
    result = plugin.greet("World")
    assert isinstance(result, ExecutionResult)
    assert result.value == "Hello, World!"
    assert result.action == "greet"

    # Test string representation
    assert str(result) == "greet: Hello, World!"


def test_execution_result_disabled():
    """Test that raw results are returned when disabled."""
    # Disable execution reporting
    track_function_calls(False)

    plugin = SamplePluginForTests()

    # Test direct result
    result = plugin.add(2, 3)
    assert not isinstance(result, ExecutionResult)
    assert result == 5

    # Re-enable for other tests
    track_function_calls(True)


def test_execution_result_performance():
    """Test that ExecutionResult adds minimal overhead."""
    plugin = SamplePluginForTests()

    # Time with ExecutionResult
    track_function_calls(True)
    start = time.time()
    for _ in range(1000):
        result = plugin.add(2, 3)
        assert result.value == 5
    with_result_time = time.time() - start

    # Time without ExecutionResult
    track_function_calls(False)
    start = time.time()
    for _ in range(1000):
        result = plugin.add(2, 3)
        assert result == 5
    without_result_time = time.time() - start

    # The overhead should be reasonable (less than 10x)
    assert with_result_time < without_result_time * 10

    # Re-enable for other tests
    track_function_calls(True)
