"""
Contains core functionality for the package.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from .attributes import Attributes, Classes, Elements
from .utilities.optional import requires_modules
from .utilities.validate import is_element

if TYPE_CHECKING:
    from .types import AttributesType, ClassesType, Element, ElementsType

# Import optional dependencies
try:
    from bs4 import BeautifulSoup
    from bs4.formatter import HTMLFormatter
except ImportError:
    pass


class HTMLBuilder(ABC):
    """Base class for HTML Builder objects."""

    def __init__(
        self,
        elements: ElementsType | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the HTMLTable object."""

        # Standardize the elements
        if elements is not None:
            if is_element(elements):
                elements = Elements(elements)
            elif isinstance(elements, list):
                elements = Elements(*elements)
            elif not isinstance(elements, Elements):
                raise TypeError(
                    f"Invalid type {type(elements).__name__} for Elements"
                )

        # Initialize instance variables
        self._elements = elements if elements else Elements()
        self._attributes = attributes if attributes else Attributes()

        # Set the classes if any were provided
        if classes is not None:
            self._attributes.classes = classes

    @abstractmethod
    def construct(self) -> str:
        """Generates HTML from the stored elements."""
        attributes_string = f" {self.attributes}" if self.attributes else ""
        html = f"<{self.tag}{attributes_string}>"
        for element in self.elements:
            html += f"{element}"
        html += f"</{self.tag}>"
        return html

    @requires_modules("bs4", "bs4.formatter")
    def prettify(self, indent: int = 2) -> str:
        """Generates HTML from the stored elements."""
        formatter = HTMLFormatter(void_element_close_prefix="", indent=indent)
        soup = BeautifulSoup(self.construct(), "html.parser")
        return soup.prettify(formatter=formatter)

    def save(self, filepath: str, prettify: bool = False) -> None:
        """Saves the HTML data to the specified filepath."""
        with open(filepath, "w", encoding="utf-8") as f:
            if not prettify:
                f.write(self.construct())
            else:
                try:
                    f.write(self.prettify())
                except ModuleNotFoundError:
                    f.write(self.construct())

    @property
    def elements(self) -> Elements:
        """Gets the stored elements."""
        return self._elements

    @property
    def attributes(self) -> Attributes:
        """Gets the stored attributes."""
        return self._attributes

    @property
    def classes(self) -> Classes | None:
        """Gets the stored classes."""
        return self._attributes.classes

    def __eq__(self, other: Any) -> bool:
        """Determines whether two HTMLBuilder objects are equal."""
        if isinstance(other, self.__class__):
            attributes_equal = self.attributes == other.attributes
            elements_equal = self.elements == other.elements
            return attributes_equal and elements_equal
        return False

    def __str__(self) -> str:
        """Gets a string version of the object."""
        return self.construct()

    def __repr__(self) -> str:
        """Gets a string representation of the object."""
        if not bool(self._attributes):
            return f"{self.__class__.__name__}()"
        return f"{self.__class__.__name__}(attributes={self._attributes!r})"


class GenericElement(HTMLBuilder):
    """Constructs a generic HTML element.

    This generic element class is useful for creating custom HTML elements that
    are simply containers for other sub-elements. Typically, the only difference
    between subclasses of GenericElement are the tags, but additional
    functionality may be implemented.

    It provides a convenient way to add, set, insert, update, remove, and pop
    elements, as well as a clear method to remove all elements.
    """

    def __init__(
        self,
        tag: str,
        elements: ElementsType | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the GenericElement object."""

        # Initialize the builder
        super().__init__(
            elements=elements,
            attributes=attributes,
            classes=classes,
        )
        self.tag = tag

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
