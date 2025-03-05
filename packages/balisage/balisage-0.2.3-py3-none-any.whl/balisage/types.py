"""
Contains types for the package.
"""

from typing import TypeAlias

from .attributes import Attributes, Classes, Elements
from .core import HTMLBuilder

# MARK: Builders

Builder: TypeAlias = HTMLBuilder

# MARK: Classes

ClassesType: TypeAlias = Classes | str

# MARK: Attributes

AttributeValue: TypeAlias = str | bool | None
AttributeMap: TypeAlias = dict[str, AttributeValue]
AttributesType: TypeAlias = Attributes | AttributeMap

# MARK: Elements

Element: TypeAlias = type[Builder] | str
ElementsType: TypeAlias = Elements | list[Element] | Element
