from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .document import PDFDocument
from .merger import MergeEntry, PDFMergerService
from .page_range import InvalidPageRangeError, PageRange
from .scanner import PDFFileScanner
from .splitter import PDFSplitterService


class ConsoleUI:
    """Interactive, prompt-driven interface for merging PDFs."""

    def __init__(self, directory: Path) -> None:
        self.scanner = PDFFileScanner(directory)
        self.merger = PDFMergerService()

    def run(self) -> int:
        documents = self.scanner.scan()
        if not documents:
            print("No PDF files found in the current directory.")
            return 1

        selected = self._select_documents(documents)
        if not selected:
            print("No files selected for merging.")
            return 1

        entries = [
            MergeEntry(document, self._prompt_page_range(document))
            for document in selected
        ]
        output_path = self._prompt_output_path()

        try:
            result = self.merger.merge(entries, output_path)
        except InvalidPageRangeError as exc:
            print(f"Error: {exc}")
            return 1

        print(f"PDFs merged successfully into {result}")
        return 0

    def _select_documents(self, documents: List[PDFDocument]) -> List[PDFDocument]:
        print("Available PDF files:")
        for i, document in enumerate(documents, 1):
            print(f"{i}. {document.name}")

        raw = input(
            "Enter the numbers of the files you want to merge, in order (comma-separated): "
        )
        try:
            indices = [int(value.strip()) - 1 for value in raw.split(",") if value.strip()]
        except ValueError:
            print("Invalid input; expected comma-separated numbers.")
            return []
        return [documents[i] for i in indices if 0 <= i < len(documents)]

    def _prompt_page_range(self, document: PDFDocument) -> PageRange:
        while True:
            raw = input(
                f"Enter page range for {document.name} "
                "(e.g. '1-5', '1,3,5-7', or 'all'): "
            )
            try:
                return PageRange.parse(raw)
            except InvalidPageRangeError as exc:
                print(f"Invalid input: {exc}. Please try again.")

    def _prompt_output_path(self) -> str:
        raw = input("Enter the name for the merged PDF (default: 'combined.pdf'): ")
        return raw.strip() or "combined.pdf"


def _parse_entry_argument(raw: str, directory: Path) -> MergeEntry:
    """Parse a 'file.pdf' or 'file.pdf:range' command-line argument."""
    name, _, range_text = raw.partition(":")
    document = PDFDocument(directory / name)
    page_range = PageRange.parse(range_text) if range_text else PageRange.all_pages()
    return MergeEntry(document, page_range)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdfmerger",
        description="Merge PDF files, optionally selecting specific pages from each.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help=(
            "PDF files to merge, in order, formatted as 'file.pdf' or "
            "'file.pdf:1-3,5'. If omitted, an interactive prompt is shown."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="combined.pdf",
        help="Name of the merged output file (default: combined.pdf).",
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=".",
        help="Directory to resolve input and output files against (default: current directory).",
    )
    return parser


def build_split_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdfmerger split",
        description="Split a PDF file into multiple output files.",
    )
    parser.add_argument("file", help="PDF file to split.")
    parser.add_argument(
        "-r",
        "--range",
        dest="ranges",
        action="append",
        metavar="RANGE",
        help=(
            "A page range for one output file, e.g. '1-3' or '1,3,5-7'. "
            "Repeat this flag once per output file. Cannot be combined with --every."
        ),
    )
    parser.add_argument(
        "--every",
        type=int,
        metavar="N",
        help="Split into consecutive chunks of N pages each. Cannot be combined with --range.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Directory to write the split files into (default: current directory).",
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=".",
        help="Directory to resolve the input file against (default: current directory).",
    )
    return parser


def _run_split(argv: List[str]) -> int:
    parser = build_split_arg_parser()
    args = parser.parse_args(argv)

    if bool(args.ranges) == bool(args.every):
        print("Error: specify exactly one of --range or --every", file=sys.stderr)
        return 1

    try:
        document = PDFDocument(Path(args.directory) / args.file)
        splitter = PDFSplitterService()
        if args.every:
            outputs = splitter.split_every_n_pages(document, args.every, args.output_dir)
        else:
            ranges = [PageRange.parse(text) for text in args.ranges]
            outputs = splitter.split_by_ranges(document, ranges, args.output_dir)
    except (InvalidPageRangeError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for output in outputs:
        print(f"Wrote {output}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)

    if argv and argv[0] == "split":
        return _run_split(argv[1:])

    parser = build_arg_parser()
    args = parser.parse_args(argv)
    directory = Path(args.directory)

    if not args.files:
        return ConsoleUI(directory).run()

    try:
        entries = [_parse_entry_argument(raw, directory) for raw in args.files]
        result = PDFMergerService().merge(entries, directory / args.output)
    except (InvalidPageRangeError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"PDFs merged successfully into {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
