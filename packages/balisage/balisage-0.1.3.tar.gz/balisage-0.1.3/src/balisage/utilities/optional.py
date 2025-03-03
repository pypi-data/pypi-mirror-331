"""
Contains code for optional dependencies.
"""

import importlib
from functools import wraps
from typing import Any, Callable


def module_exists(module_name: str) -> bool:
    """Determines whether or not a module exists."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def requires_modules(*dependencies: str) -> Callable[[Callable], Callable]:
    """Raises an exception if any of the specified modules are not installed.

    Module names should be passed as separate string arguments.
    """

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Callable:
            # Check if all required dependencies are installed
            if missing := [d for d in dependencies if not module_exists(d)]:
                module_string = "module" if len(missing) == 1 else "modules"
                raise ModuleNotFoundError(
                    f"Function {function.__name__} requires the missing "
                    f"optional {module_string}: {', '.join(missing)}"
                )
            return function(*args, **kwargs)

        return wrapper

    return decorator
