from pathlib import Path

from pypdf import PdfReader, PdfWriter

from pdfmerger.document import PDFDocument
from pdfmerger.page_range import PageRange
from pdfmerger.splitter import PDFSplitterService

import pytest


def _make_pdf(path: Path, page_count: int) -> None:
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=72, height=72)
    with path.open("wb") as handle:
        writer.write(handle)


def _page_counts(paths):
    counts = []
    for path in paths:
        with path.open("rb") as handle:
            counts.append(len(PdfReader(handle).pages))
    return counts


def test_split_by_ranges_writes_one_file_per_range(tmp_path):
    _make_pdf(tmp_path / "a.pdf", 6)
    document = PDFDocument(tmp_path / "a.pdf")
    ranges = [PageRange.parse("1-2"), PageRange.parse("3-6")]

    outputs = PDFSplitterService().split_by_ranges(document, ranges, tmp_path / "out")

    assert [output.name for output in outputs] == ["a_part1.pdf", "a_part2.pdf"]
    assert _page_counts(outputs) == [2, 4]


def test_split_by_ranges_creates_output_dir(tmp_path):
    _make_pdf(tmp_path / "a.pdf", 2)
    document = PDFDocument(tmp_path / "a.pdf")

    outputs = PDFSplitterService().split_by_ranges(
        document, [PageRange.all_pages()], tmp_path / "nested" / "out"
    )

    assert outputs[0].exists()


def test_split_by_ranges_with_no_ranges_raises(tmp_path):
    _make_pdf(tmp_path / "a.pdf", 2)
    document = PDFDocument(tmp_path / "a.pdf")

    with pytest.raises(ValueError):
        PDFSplitterService().split_by_ranges(document, [], tmp_path / "out")


def test_split_every_n_pages_splits_into_even_chunks(tmp_path):
    _make_pdf(tmp_path / "a.pdf", 5)
    document = PDFDocument(tmp_path / "a.pdf")

    outputs = PDFSplitterService().split_every_n_pages(document, 2, tmp_path / "out")

    assert len(outputs) == 3
    assert _page_counts(outputs) == [2, 2, 1]


def test_split_every_n_pages_rejects_non_positive_n(tmp_path):
    _make_pdf(tmp_path / "a.pdf", 2)
    document = PDFDocument(tmp_path / "a.pdf")

    with pytest.raises(ValueError):
        PDFSplitterService().split_every_n_pages(document, 0, tmp_path / "out")
