from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from pypdf import PdfReader


class PDFDocument:
    """A single PDF file on disk, with lazily-loaded page count."""

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        if self.path.suffix.lower() != ".pdf":
            raise ValueError(f"'{self.path}' is not a PDF file")
        if not self.path.is_file():
            raise FileNotFoundError(f"'{self.path}' does not exist")
        self._page_count: Optional[int] = None

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def page_count(self) -> int:
        if self._page_count is None:
            with self.path.open("rb") as handle:
                self._page_count = len(PdfReader(handle).pages)
        return self._page_count

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"PDFDocument({str(self.path)!r})"
