"""
Contains validation-related code for the package.
"""

import re
from typing import Any

# MARK: Types


def is_builder(object: Any) -> bool:
    """Determines whether an object is a subclass of HTMLBuilder."""
    from ..types import Builder

    return issubclass(type(object), Builder) and type(object) is not Builder


def is_element(object: Any) -> bool:
    """Determines whether an object is a valid Element."""
    return is_builder(object) or isinstance(object, str)


# MARK: Classes


def is_valid_class_name(name: str) -> bool:
    """Determines whether a string is a valid HTML/CSS class name."""
    return re.match(r"^-?[_a-zA-Z]+[_a-zA-Z0-9-]*$", name) is not None


def sanitize_class_name(
    name: str,
    lower: bool = True,
    strip: bool = True,
    replacements: dict[str, str] | None = None,
) -> str:
    """Converts a class string into a valid class name."""
    if replacements is None:
        replacements = {" ": "-"}
    original_name = name
    name = name.lower() if lower else name
    name = name.strip() if strip else name
    for k, v in replacements.items():
        name = name.replace(k, v)
    if not is_valid_class_name(name):
        raise ValueError(
            f"Class name '{original_name}' (sanitized to '{name}') is invalid"
        )
    return name


# MARK: Attributes


def split_preserving_quotes(string: str) -> list[str]:
    """Splits an attribute string into a list of strings, preserving quotes."""
    return re.findall(r"[^'\s]+='[^']*'|\S+", string)
