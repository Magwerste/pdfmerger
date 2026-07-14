from __future__ import annotations

from pathlib import Path
from typing import List, Union

from .document import PDFDocument


class PDFFileScanner:
    """Finds PDF files within a directory."""

    def __init__(self, directory: Union[str, Path] = ".") -> None:
        self.directory = Path(directory)

    def scan(self) -> List[PDFDocument]:
        pdf_paths = sorted(self.directory.glob("*.pdf"))
        return [PDFDocument(path) for path in pdf_paths]
