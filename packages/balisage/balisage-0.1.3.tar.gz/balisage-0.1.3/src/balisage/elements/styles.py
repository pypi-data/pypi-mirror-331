"""
Contains code for all style-related HTML elements.
"""

from typing import Any

from ..attributes import Elements
from ..core import HTMLBuilder
from ..types import AttributesType, ClassesType, Element, ElementsType


class Div(HTMLBuilder):
    """Constructs an HTML div."""

    def __init__(
        self,
        elements: ElementsType | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Div object."""

        # Initialize the builder
        super().__init__(
            elements=elements,
            attributes=attributes,
            classes=classes,
        )
        self.tag = "div"

    def add(self, *elements: Element) -> None:
        """Convenience wrapper for the self.elements.add method."""
        self.elements.add(*elements)

    def set(self, *elements: Element) -> None:
        """Convenience wrapper for the self.elements.set method."""
        self.elements.set(*elements)

    def insert(self, index: int, element: Element) -> None:
        """Convenience wrapper for the self.elements.insert method."""
        self.elements.insert(index, element)

    def update(self, index: int, element: Element) -> None:
        """Convenience wrapper for the self.elements.update method."""
        self.elements.update(index, element)

    def remove(self, index: int) -> None:
        """Convenience wrapper for the self.elements.remove method."""
        self.elements.remove(index)

    def pop(self, index: int = -1) -> Element:
        """Convenience wrapper for the self.elements.pop method."""
        return self.elements.pop(index)

    def clear(self) -> None:
        """Convenience wrapper for the self.elements.clear method."""
        self.elements.clear()

    def construct(self) -> str:
        """Generates HTML from the stored elements."""
        return super().construct()


class Span(Div):
    """Constructs an HTML span."""

    def __init__(
        self,
        elements: ElementsType | str | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Span object."""

        # Convert a string into an Elements object
        if isinstance(elements, str):
            elements = Elements(elements)

        # Initialize the builder
        super().__init__(
            elements=elements,
            attributes=attributes,
            classes=classes,
        )
        self.tag = "span"

    def __add__(self, other: Any) -> str:
        """Overloads the addition operator when the instance is on the left."""
        if isinstance(other, str):
            return self.construct() + other
        raise TypeError(
            f"Invalid type {type(other).__name__} for addition on "
            f"{self.__class__.__name__}; must be {str.__name__}"
        )

    def __radd__(self, other: Any) -> str:
        """Overloads the addition operator when the instance is on the right."""
        if isinstance(other, str):
            return other + self.construct()
        raise TypeError(
            f"Invalid type {type(other).__name__} for reverse addition on "
            f"{self.__class__.__name__}; must be {str.__name__}"
        )
