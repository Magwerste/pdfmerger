from __future__ import annotations

from pathlib import Path
from typing import List, Union

from pypdf import PdfReader, PdfWriter

from .document import PDFDocument
from .page_range import PageRange


class PDFSplitterService:
    """Splits a single PDF document into multiple output files."""

    def split_by_ranges(
        self,
        document: PDFDocument,
        ranges: List[PageRange],
        output_dir: Union[str, Path],
    ) -> List[Path]:
        """Write one output PDF per page range, named '<stem>_part1.pdf' etc."""
        if not ranges:
            raise ValueError("No page ranges provided to split")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        with document.path.open("rb") as handle:
            reader = PdfReader(handle)
            page_count = len(reader.pages)

            outputs = []
            for i, page_range in enumerate(ranges, 1):
                indices = page_range.resolve(page_count)
                writer = PdfWriter()
                for index in indices:
                    writer.add_page(reader.pages[index])

                output_path = output_dir / f"{document.path.stem}_part{i}.pdf"
                with output_path.open("wb") as out_handle:
                    writer.write(out_handle)
                outputs.append(output_path)
            return outputs

    def split_every_n_pages(
        self,
        document: PDFDocument,
        n: int,
        output_dir: Union[str, Path],
    ) -> List[Path]:
        """Split a document into consecutive chunks of at most n pages each."""
        if n < 1:
            raise ValueError("n must be 1 or greater")

        page_count = document.page_count
        ranges = [
            PageRange(indices=list(range(start, min(start + n, page_count))))
            for start in range(0, page_count, n)
        ]
        return self.split_by_ranges(document, ranges, output_dir)
