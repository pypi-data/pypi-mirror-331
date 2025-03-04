# Agently SDK

[![PyPI version](https://badge.fury.io/py/agently-sdk.svg)](https://badge.fury.io/py/agently-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official SDK for developing extensions for the [Agently](https://github.com/onwardplatforms/agently) framework. Currently focused on plugin development, with more capabilities planned for future releases.

## Installation

```bash
pip install agently-sdk
```

## Quick Start

Create a simple plugin:

```python
from agently_sdk.plugins import Plugin, PluginVariable, kernel_function

class HelloPlugin(Plugin):
    name = "hello"
    description = "A simple hello world plugin"
    
    default_name = PluginVariable(
        name="default_name",
        description="Default name to use in greetings",
        default="World"
    )
    
    @kernel_function
    def greet(self, name=None) -> str:
        """Greet the user."""
        return f"Hello, {name or self.default_name}!"
```

## Plugin Development

### Plugin Class

The `Plugin` class is the base class for all Agently plugins. It provides the structure and interface for creating plugins that can be used by Agently agents.

| Attribute     | Type  | Required | Description                                     |
| ------------- | ----- | -------- | ----------------------------------------------- |
| `name`        | `str` | Yes      | The name of the plugin, used for identification |
| `description` | `str` | Yes      | A brief description of what the plugin does     |

#### Methods

| Method                   | Description                                                                 |
| ------------------------ | --------------------------------------------------------------------------- |
| `get_kernel_functions()` | Returns a dictionary of all methods decorated with `@kernel_function`       |
| `get_plugin_variables()` | Returns a dictionary of all `PluginVariable` instances defined in the class |

### PluginVariable

The `PluginVariable` class represents a configurable variable for a plugin. It allows plugins to be configured with different values when they are loaded by Agently.

| Parameter     | Type                    | Required | Default | Description                                    |
| ------------- | ----------------------- | -------- | ------- | ---------------------------------------------- |
| `name`        | `str`                   | Yes      | -       | The name of the variable                       |
| `description` | `str`                   | Yes      | -       | A description of what the variable is used for |
| `default`     | `Any`                   | No       | `None`  | The default value if none is provided          |
| `required`    | `bool`                  | No       | `False` | Whether this variable must be provided         |
| `validator`   | `Callable[[Any], bool]` | No       | `None`  | Optional function that validates the value     |
| `choices`     | `List[Any]`             | No       | `None`  | Optional list of valid choices for the value   |
| `type`        | `Type`                  | No       | `None`  | Optional type constraint for the value         |

#### Methods

| Method            | Description                                           |
| ----------------- | ----------------------------------------------------- |
| `validate(value)` | Validates a value against this variable's constraints |
| `to_dict()`       | Converts this variable to a dictionary representation |

### Kernel Function Decorator

Agently SDK provides two decorators for marking methods as callable by agents:

1. `@agently_function` - The recommended decorator for Agently plugins
2. `@kernel_function` - An alias for `@agently_function` provided for backward compatibility

Both decorators wrap the `kernel_function` decorator from `semantic_kernel.functions` while maintaining compatibility with our existing code. If the Semantic Kernel package is not available, they fall back to a compatible implementation.

```python
from agently_sdk.plugins import Plugin, PluginVariable, agently_function

class MyPlugin(Plugin):
    name = "my_plugin"
    description = "A sample plugin"
    
    @agently_function(action="Performing calculation")
    def my_function(self, param1: str, param2: int = 0) -> str:
        """
        Function docstring that describes what this function does.
        
        Args:
            param1: Description of param1
            param2: Description of param2
            
        Returns:
            Description of the return value
        """
        # Implementation
        return result
```

The `action` parameter provides a human-readable description of what the function does, which is useful for tracking and reporting.

### Function Tracking and Execution Results

Agently SDK provides functionality to track function execution and get detailed information about each function call.

#### ExecutionResult

When function tracking is enabled, decorated functions return `ExecutionResult` objects that include:

- The actual return value of the function (`value`)
- The human-readable action description (`action`)
- Metadata about the execution (`metadata`), such as:
  - Duration of the function call
  - Function name
  - Arguments passed to the function

```python
from agently_sdk.plugins import track_function_calls

# Enable function tracking
track_function_calls(True)

# Call a plugin function
result = my_plugin.some_function("arg1", "arg2")

# Access the execution information
print(f"Action: {result.action}")
print(f"Duration: {result.metadata['duration']} seconds")
print(f"Actual value: {result.value}")
```

#### Getting Raw Results

For backward compatibility, you can use the `get_result` helper function to extract the raw return value from either an `ExecutionResult` or a direct value:

```python
from agently_sdk.plugins import get_result

# Works with both ExecutionResult objects and direct values
raw_value = get_result(result)
```

#### Enabling and Disabling Function Tracking

Function tracking is disabled by default for backward compatibility. You can enable it globally:

```python
from agently_sdk.plugins import track_function_calls

# Enable function tracking
track_function_calls(True)

# Disable function tracking
track_function_calls(False)
```

## Best Practices

### Plugin Design

1. **Clear Purpose**: Each plugin should have a clear, focused purpose
2. **Descriptive Names**: Use descriptive names for plugins, variables, and functions
3. **Comprehensive Documentation**: Include detailed docstrings for all functions
4. **Input Validation**: Validate all inputs to ensure robust behavior
5. **Error Handling**: Handle errors gracefully and provide informative error messages

### Variable Configuration

1. **Default Values**: Provide sensible default values for variables when possible
2. **Validation**: Use validators to ensure variables meet requirements
3. **Type Constraints**: Specify value types to catch type errors early
4. **Descriptive Names**: Use clear, descriptive names for variables

## License

MIT 