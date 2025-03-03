"""
Contains code for all formatting-related HTML elements.
"""

from ..core import HTMLBuilder
from ..types import AttributesType, ClassesType


class LineBreak(HTMLBuilder):
    """Constructs an HTML line break."""

    def __init__(
        self,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the LineBreak object."""

        # Initialize the builder
        super().__init__(
            elements=None,
            attributes=attributes,
            classes=classes,
        )
        self.tag = "br"

        self.elements.max_elements = 0

    def construct(self) -> str:
        """Generates HTML from the stored elements."""
        attributes_string = f" {self.attributes}" if self.attributes else ""
        return f"<{self.tag}{attributes_string}>"


class HorizontalRule(LineBreak):
    """Constructs an HTML horizontal rule."""

    def __init__(
        self,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the HorizontalRule object."""

        # Initialize the builder
        super().__init__(
            attributes=attributes,
            classes=classes,
        )
        self.tag = "hr"
