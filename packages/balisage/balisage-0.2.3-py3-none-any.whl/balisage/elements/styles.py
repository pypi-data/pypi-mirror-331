"""
Contains code for all style-related HTML elements.
"""

from ..core import GenericElement
from ..types import AttributesType, ClassesType, ElementsType


class Div(GenericElement):
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
            tag="div",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )


class Span(GenericElement):
    """Constructs an HTML span."""

    def __init__(
        self,
        elements: ElementsType | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Span object."""

        # Initialize the builder
        super().__init__(
            tag="span",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )


class Bold(GenericElement):
    """Constructs an HTML bold element."""

    def __init__(
        self,
        elements: ElementsType | str | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Bold object."""

        # Initialize the builder
        super().__init__(
            tag="b",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )


class Strong(GenericElement):
    """Constructs an HTML strong element."""

    def __init__(
        self,
        elements: ElementsType | str | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Strong object."""

        # Initialize the builder
        super().__init__(
            tag="strong",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )


class Italics(GenericElement):
    """Constructs an HTML italics element."""

    def __init__(
        self,
        elements: ElementsType | str | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Italics object."""

        # Initialize the builder
        super().__init__(
            tag="i",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )


class Emphasis(GenericElement):
    """Constructs an HTML emphasis element."""

    def __init__(
        self,
        elements: ElementsType | str | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Emphasis object."""

        # Initialize the builder
        super().__init__(
            tag="em",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )


class Underline(GenericElement):
    """Constructs an HTML underline element."""

    def __init__(
        self,
        elements: ElementsType | str | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Underline object."""

        # Initialize the builder
        super().__init__(
            tag="u",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )


class Strikethrough(GenericElement):
    """Constructs an HTML strikethrough element."""

    def __init__(
        self,
        elements: ElementsType | str | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Strikethrough object."""

        # Initialize the builder
        super().__init__(
            tag="s",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )


class Subscript(GenericElement):
    """Constructs an HTML subscript element."""

    def __init__(
        self,
        elements: ElementsType | str | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Subscript object."""

        # Initialize the builder
        super().__init__(
            tag="sub",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )


class Superscript(GenericElement):
    """Constructs an HTML superscript element."""

    def __init__(
        self,
        elements: ElementsType | str | None = None,
        attributes: AttributesType | None = None,
        classes: ClassesType | None = None,
    ) -> None:
        """Initializes the Superscript object."""

        # Initialize the builder
        super().__init__(
            tag="sup",
            elements=elements,
            attributes=attributes,
            classes=classes,
        )
