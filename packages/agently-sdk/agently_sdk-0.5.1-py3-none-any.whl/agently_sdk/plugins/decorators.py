"""
Decorators for Agently plugins.

This module provides decorators for use in Agently plugins.
"""

import functools
import inspect
import time
from typing import Any, Callable, Optional, TypeVar, Union, cast, overload

from agently_sdk.plugins.variables import ExecutionResult

# Import the original kernel_function from semantic_kernel
try:
    from semantic_kernel.functions import kernel_function as sk_kernel_function

    # Check what parameters sk_kernel_function accepts
    sk_params = inspect.signature(sk_kernel_function).parameters
    SK_ACCEPTS_INPUT_DESC = "input_description" in sk_params
except ImportError:
    # Fallback implementation if semantic_kernel is not installed
    sk_kernel_function = None  # type: ignore
    SK_ACCEPTS_INPUT_DESC = False

F = TypeVar("F", bound=Callable[..., Any])
DecoratorFunc = Callable[[F], F]

# Global flag to control execution reporting
_COLLECT_EXECUTION_INFO = False


def track_function_calls(enabled: bool = True) -> None:
    """
    Globally enable or disable tracking of function calls.

    When enabled, functions decorated with @agently_function or @kernel_function
    will return ExecutionResult objects containing the actual value and metadata.
    When disabled, they will return the actual value directly.

    Args:
        enabled: Whether to enable function call tracking
    """
    global _COLLECT_EXECUTION_INFO
    _COLLECT_EXECUTION_INFO = enabled


@overload
def agently_function(func: F) -> F: ...


@overload
def agently_function(
    func: None = None,
    *,
    description: Optional[str] = None,
    name: Optional[str] = None,
    input_description: Optional[str] = None,
    action: Optional[str] = None,
) -> DecoratorFunc: ...


def agently_function(
    func: Optional[F] = None,
    *,
    description: Optional[str] = None,
    name: Optional[str] = None,
    input_description: Optional[str] = None,
    action: Optional[str] = None,
) -> Union[F, DecoratorFunc]:
    """
    Decorator for functions that should be exposed as Agently functions.

    This wraps the semantic_kernel.functions.kernel_function decorator
    while maintaining compatibility with our existing code.

    This can be used with or without arguments:

    @agently_function
    def my_func(): ...

    or

    @agently_function(description="My function", action="performing an action")
    def my_func(): ...

    Args:
        func: The function to decorate (when used without arguments)
        description: The description of the function
        name: The name of the function (defaults to the function name)
        input_description: The description of the input parameter
        action: A human-readable description of what the function does

    Returns:
        The decorated function
    """

    def apply_our_decorator(f: F) -> F:
        """Apply our decorator logic to ensure compatibility with our Plugin class."""

        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Only collect execution info if globally enabled
            collect_info = _COLLECT_EXECUTION_INFO

            # Start timing
            start_time = time.time()

            # Call the original function
            result = f(*args, **kwargs)

            # If we're collecting execution info, wrap the result
            if collect_info:
                # Calculate duration
                duration = time.time() - start_time

                # Create metadata
                metadata = {
                    "function_name": getattr(f, "_name", None) or f.__name__,
                    "duration": duration,
                    # Skip 'self' if this is a method call
                    "args": args[1:] if args and hasattr(args[0], "__class__") else args,
                    "kwargs": kwargs,
                }

                # Get the action (human-readable description of what the function does)
                action_str = action or f.__name__

                # Wrap the result
                return ExecutionResult(value=result, action=action_str, metadata=metadata)
            else:
                # Return the original result
                return result

        # Ensure our Plugin class can find this function
        wrapper._is_kernel_function = True  # type: ignore
        wrapper._is_agently_function = True  # type: ignore
        wrapper._description = description  # type: ignore
        wrapper._name = name  # type: ignore
        wrapper._input_description = input_description  # type: ignore
        wrapper._action = action  # type: ignore

        # Add the __kernel_function__ attribute for compatibility with Semantic Kernel
        setattr(wrapper, "__kernel_function__", True)

        return cast(F, wrapper)

    # If semantic_kernel is available, use its decorator first
    if sk_kernel_function is not None:
        # Handle the case where decorator is used without arguments
        if func is not None:
            # First apply the SK decorator, then our compatibility layer
            sk_decorated = sk_kernel_function(func)
            return apply_our_decorator(cast(F, sk_decorated))

        # Handle the case where decorator is used with arguments
        def decorator(inner_func: F) -> F:
            # First apply the SK decorator with arguments
            # Only pass parameters that SK accepts
            sk_kwargs: dict[str, Optional[str]] = {"description": description, "name": name}
            if SK_ACCEPTS_INPUT_DESC and input_description is not None:
                sk_kwargs["input_description"] = input_description

            sk_decorated = sk_kernel_function(**sk_kwargs)(inner_func)  # type: ignore
            # Then apply our compatibility layer
            return apply_our_decorator(cast(F, sk_decorated))

        return decorator
    else:
        # Fallback to our implementation if semantic_kernel is not available
        # Handle the case where decorator is used without arguments
        if func is not None:
            return apply_our_decorator(func)

        # Handle the case where decorator is used with arguments
        def decorator(inner_func: F) -> F:
            return apply_our_decorator(inner_func)

        return decorator


# Keep kernel_function as an alias for backward compatibility
kernel_function = agently_function


__all__ = ["agently_function", "kernel_function", "track_function_calls"]
