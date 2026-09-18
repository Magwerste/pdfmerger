# PDF Merger

A small command-line tool for merging PDF files, with support for selecting
specific pages from each source file.

## Features

- Merge any number of PDF files into one, in a chosen order.
- Select specific pages or ranges from each file (e.g. `1-3,7`) instead of
  always merging entire documents.
- Two ways to use it: an interactive prompt-driven mode, or a scriptable
  command-line mode for use in shell scripts and automation.
- Clear error messages for invalid page ranges, missing files, or malformed
  input.

## Installation

Requires Python 3.9 or later.

```bash
pip install -e .
```

This installs the package in editable mode along with its `pypdf` dependency,
and exposes both the `pdfmerger` console script and the `python -m pdfmerger`
module entry point described below.

## Usage

### Interactive mode

Run the tool with no arguments from a directory containing PDF files:

```bash
python -m pdfmerger
```

It will list the PDF files it finds, let you pick which ones to merge and in
what order, prompt for a page range for each one (or `all`), and ask for an
output filename.

### Command-line mode

Pass files directly for a non-interactive merge, optionally with a page range
after a colon:

```bash
python -m pdfmerger report.pdf:1-3 appendix.pdf -o final.pdf
```

This merges pages 1-3 of `report.pdf` followed by every page of
`appendix.pdf`, writing the result to `final.pdf`.

Options:

| Flag | Description |
| --- | --- |
| `-o`, `--output` | Output filename (default: `combined.pdf`) |
| `-d`, `--directory` | Directory to resolve input/output files against (default: current directory) |

### Splitting a PDF

Use the `split` subcommand to break one PDF into several files, either by
explicit page ranges or into fixed-size chunks:

```bash
python -m pdfmerger split report.pdf -r 1-3 -r 4-6 -r 7-10 -o parts/
python -m pdfmerger split report.pdf --every 5 -o parts/
```

The first example writes `parts/report_part1.pdf` (pages 1-3),
`parts/report_part2.pdf` (pages 4-6), and `parts/report_part3.pdf`
(pages 7-10). The second splits the document into consecutive 5-page
chunks. `--range`/`-r` and `--every` are mutually exclusive.

Options:

| Flag | Description |
| --- | --- |
| `-r`, `--range` | A page range for one output file (repeatable) |
| `--every` | Split into consecutive chunks of N pages each |
| `-o`, `--output-dir` | Directory to write the split files into (default: current directory) |
| `-d`, `--directory` | Directory to resolve the input file against (default: current directory) |

## Project structure

The tool is organized as a small set of single-responsibility classes rather
than one monolithic script, laid out under `src/pdfmerger/`:

- `PageRange` (`page_range.py`) parses and validates page range strings such
  as `1,3,5-7` into concrete page indices.
- `PDFDocument` (`document.py`) represents a single PDF file on disk and
  exposes its page count.
- `PDFFileScanner` (`scanner.py`) discovers PDF files in a directory.
- `PDFMergerService` (`merger.py`) performs the actual merge given a list of
  documents and the pages to take from each.
- `PDFSplitterService` (`splitter.py`) splits a document into multiple
  output files, either by explicit page ranges or into fixed-size chunks.
- `ConsoleUI` and `main` (`cli.py`) wire the above classes together into the
  interactive and command-line interfaces.

Separating parsing, file discovery, and merging from the user interface
keeps each piece independently testable and easy to reason about.

## Running tests

```bash
pip install -r requirements.txt pytest
pytest
```

## Background

This project started as a first-year university exercise for learning
Python. It has since been rewritten with a proper object-oriented design,
a scriptable CLI, and test coverage.

## Acknowledgments

All PDF reading and writing is done via [pypdf](https://github.com/py-pdf/pypdf),
maintained by Martin Thoma and the py-pdf community. This project is just a
thin, task-specific CLI on top of their work.
