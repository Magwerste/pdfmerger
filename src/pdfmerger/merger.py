from __future__ import annotations

from pathlib import Path
from typing import List, NamedTuple, Union

from pypdf import PdfReader, PdfWriter

from .document import PDFDocument
from .page_range import PageRange


class MergeEntry(NamedTuple):
    """A document paired with the pages to take from it."""

    document: PDFDocument
    page_range: PageRange


class PDFMergerService:
    """Combines selected pages from multiple PDF documents into one file."""

    def merge(self, entries: List[MergeEntry], output_path: Union[str, Path]) -> Path:
        if not entries:
            raise ValueError("No documents provided to merge")

        writer = PdfWriter()
        for entry in entries:
            with entry.document.path.open("rb") as handle:
                reader = PdfReader(handle)
                indices = entry.page_range.resolve(len(reader.pages))
                for index in indices:
                    writer.add_page(reader.pages[index])

        output_path = self._with_pdf_suffix(Path(output_path))
        with output_path.open("wb") as handle:
            writer.write(handle)
        return output_path

    @staticmethod
    def _with_pdf_suffix(path: Path) -> Path:
        if path.suffix.lower() == ".pdf":
            return path
        return path.with_name(path.name + ".pdf")
