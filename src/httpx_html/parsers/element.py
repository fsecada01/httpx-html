"""Element parser class."""

from typing import TYPE_CHECKING

from .base import BaseParser

if TYPE_CHECKING:
    from collections.abc import MutableMapping
    
    _Attrs = MutableMapping
    _Url = str


class Element(BaseParser):
    """An element of HTML.

    :param element: The element from which to base the parsing upon.
    :param url: The URL from which the HTML originated, used for ``absolute_links``.
    :param default_encoding: Which encoding to default to.
    """

    __slots__ = "tag", "lineno", "_attrs"

    def __init__(
        self,
        *,
        element,
        url: "_Url",
        default_encoding: str | None = None,
    ) -> None:
        super().__init__(element=element, url=url, default_encoding=default_encoding)
        self.element = element
        self.tag = element.tag
        self.lineno = element.sourceline
        self._attrs = None

    def __repr__(self) -> str:
        attrs = [f"{a}={self.attrs[a]!r}" for a in self.attrs]
        return f'<Element {self.element.tag!r} {" ".join(attrs)}>'

    @property
    def attrs(self) -> "_Attrs":
        """Returns a dictionary of the attributes of the :class:`Element <Element>`
        (`learn more <https://www.w3schools.com/tags/ref_attributes.asp>`_).
        """
        if self._attrs is None:
            self._attrs = {k: v for k, v in self.element.items()}

            # split class and rel up, as there are usually many of them
            for attr in ["class", "rel"]:
                if attr in self._attrs:
                    self._attrs[attr] = tuple(self._attrs[attr].split())

        return self._attrs