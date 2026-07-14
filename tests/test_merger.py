from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from pdfmerger.document import PDFDocument
from pdfmerger.merger import MergeEntry, PDFMergerService
from pdfmerger.page_range import PageRange
from pdfmerger.scanner import PDFFileScanner


def _make_pdf(path: Path, page_count: int) -> None:
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=72, height=72)
    with path.open("wb") as handle:
        writer.write(handle)


def test_scanner_finds_pdfs_and_ignores_other_files(tmp_path):
    _make_pdf(tmp_path / "a.pdf", 1)
    _make_pdf(tmp_path / "b.pdf", 1)
    (tmp_path / "notes.txt").write_text("not a pdf")

    documents = PDFFileScanner(tmp_path).scan()

    assert [document.name for document in documents] == ["a.pdf", "b.pdf"]


def test_document_rejects_non_pdf_extension(tmp_path):
    text_file = tmp_path / "notes.txt"
    text_file.write_text("hello")

    with pytest.raises(ValueError):
        PDFDocument(text_file)


def test_document_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        PDFDocument(tmp_path / "missing.pdf")


def test_document_reports_page_count(tmp_path):
    path = tmp_path / "a.pdf"
    _make_pdf(path, 4)

    assert PDFDocument(path).page_count == 4


def test_merge_combines_selected_pages_in_order(tmp_path):
    _make_pdf(tmp_path / "a.pdf", 3)
    _make_pdf(tmp_path / "b.pdf", 2)

    documents = PDFFileScanner(tmp_path).scan()
    entries = [
        MergeEntry(documents[0], PageRange.parse("1,3")),
        MergeEntry(documents[1], PageRange.all_pages()),
    ]

    output = PDFMergerService().merge(entries, tmp_path / "combined.pdf")

    with output.open("rb") as handle:
        assert len(PdfReader(handle).pages) == 4


def test_merge_appends_pdf_suffix_when_missing(tmp_path):
    _make_pdf(tmp_path / "a.pdf", 1)
    documents = PDFFileScanner(tmp_path).scan()
    entries = [MergeEntry(documents[0], PageRange.all_pages())]

    output = PDFMergerService().merge(entries, tmp_path / "result")

    assert output.name == "result.pdf"
    assert output.exists()


def test_merge_with_no_entries_raises(tmp_path):
    with pytest.raises(ValueError):
        PDFMergerService().merge([], tmp_path / "combined.pdf")
