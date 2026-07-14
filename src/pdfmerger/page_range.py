from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


class InvalidPageRangeError(ValueError):
    """Raised when a page range string cannot be parsed or is out of bounds."""


@dataclass(frozen=True)
class PageRange:
    """A selection of pages to take from a document.

    Internally stores zero-based page indices, since that is what PDF
    libraries expect, but is parsed from and reported in one-based page
    numbers, since that is what users expect.
    """

    indices: Optional[List[int]]  # None means "every page"

    @classmethod
    def all_pages(cls) -> "PageRange":
        return cls(indices=None)

    @classmethod
    def parse(cls, text: str) -> "PageRange":
        """Parse strings such as '1-5', '1,3,5-7', or 'all' (case-insensitive).

        An empty string is treated the same as 'all'.
        """
        normalized = text.strip().lower()
        if normalized in ("", "all"):
            return cls.all_pages()

        indices = set()
        for part in normalized.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start_str, _, end_str = part.partition("-")
                start, end = cls._parse_bounds(start_str, end_str)
                indices.update(range(start - 1, end))
            else:
                indices.add(cls._parse_page_number(part) - 1)

        if not indices:
            raise InvalidPageRangeError(f"No valid pages found in '{text}'")
        return cls(indices=sorted(indices))

    @staticmethod
    def _parse_page_number(value: str) -> int:
        try:
            number = int(value)
        except ValueError as exc:
            raise InvalidPageRangeError(f"'{value}' is not a valid page number") from exc
        if number < 1:
            raise InvalidPageRangeError("Page numbers must be 1 or greater")
        return number

    @classmethod
    def _parse_bounds(cls, start_str: str, end_str: str) -> Tuple[int, int]:
        start = cls._parse_page_number(start_str)
        end = cls._parse_page_number(end_str)
        if end < start:
            raise InvalidPageRangeError(f"Range '{start}-{end}' is out of order")
        return start, end

    @property
    def is_all(self) -> bool:
        return self.indices is None

    def resolve(self, page_count: int) -> List[int]:
        """Return concrete, validated zero-based indices for a document
        with the given page count."""
        if self.is_all:
            return list(range(page_count))

        out_of_bounds = [i for i in self.indices if i >= page_count]
        if out_of_bounds:
            bad = ", ".join(str(i + 1) for i in out_of_bounds)
            raise InvalidPageRangeError(
                f"Page(s) {bad} exceed document length of {page_count}"
            )
        return self.indices
