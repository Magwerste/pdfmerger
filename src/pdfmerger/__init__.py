from .document import PDFDocument
from .merger import MergeEntry, PDFMergerService
from .page_range import InvalidPageRangeError, PageRange
from .scanner import PDFFileScanner
from .splitter import PDFSplitterService

__all__ = [
    "PDFDocument",
    "MergeEntry",
    "PDFMergerService",
    "PageRange",
    "InvalidPageRangeError",
    "PDFFileScanner",
    "PDFSplitterService",
]

__version__ = "1.0.0"
