"""Define custom exceptions used in the Turbograph library."""

from collections.abc import Iterable


class NotFoundError(Exception):
    """Error raised when an element is not found in a collection."""

    def __init__(
        self,
        element_name: str,
        element: object,
        valid_elements: Iterable[object],
        elements_name: str | None = None,
    ) -> None:
        """Initialize the error with the element and valid elements.

        Args:
            element_name: The name of the element type.
            element: The element that was not found.
            valid_elements: The valid elements that could have been found.
            elements_name: The name of the element type in plural

        """
        self.element = element
        """The element that was not found."""

        self.valid_elements = valid_elements
        """The valid elements that could have been found."""

        if elements_name is None:
            elements_name = element_name + "s"

        super().__init__(
            f"{element_name} {element!r} not found. "
            f"Valid {elements_name}s are: {', '.join(map(repr, valid_elements))}"
        )

    def __reduce__(self) -> tuple[type, tuple]:  # pragma: no cover
        """Return a tuple of the class and its arguments for pickling."""
        return self.__class__, (self.element, self.valid_elements)
