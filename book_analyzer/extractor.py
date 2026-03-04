"""
network.extractor
=================
Reads and extracts plain text from .txt, .epub, and .pdf files.
"""

import os
import re
import zipfile


class TextExtractor:
    """Reads and extracts plain text from .txt, .epub, and .pdf files."""

    EPUB_SKIP_PATTERNS = ["toc", "cover", "nav", "logo", "cip"]

    @staticmethod
    def from_txt(path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    @classmethod
    def from_epub(cls, path: str) -> str:
        try:
            z = zipfile.ZipFile(path)
        except zipfile.BadZipFile:
            raise ValueError(f"Cannot open {path} as EPUB/ZIP.")

        html_files = sorted([
            f for f in z.namelist()
            if f.lower().endswith((".html", ".xhtml", ".htm"))
            and not any(skip in f.lower() for skip in cls.EPUB_SKIP_PATTERNS)
        ])

        if not html_files:
            raise ValueError("No readable HTML files found inside EPUB.")

        all_text = []
        for name in html_files:
            raw = z.read(name).decode("utf-8", errors="replace")
            clean = re.sub(r"<[^>]+>", " ", raw)
            clean = re.sub(r"&nbsp;|&#160;", " ", clean)
            clean = re.sub(r"&amp;", "&", clean)
            clean = re.sub(r"&lt;", "<", clean)
            clean = re.sub(r"&gt;", ">", clean)
            clean = re.sub(r"\s+", " ", clean).strip()
            if len(clean) > 100:
                all_text.append(clean)

        return "\n\n".join(all_text)

    @staticmethod
    def from_pdf(path: str) -> str:
        try:
            from pdfminer.high_level import extract_text as pdf_extract
            text = pdf_extract(path)
            if not text or len(text.strip()) < 200:
                raise ValueError(
                    "PDF text extraction returned little content "
                    "(possibly scanned image PDF)."
                )
            return text
        except ImportError:
            raise ImportError(
                "pdfminer.six is required for PDF support. "
                "Install with: pip install pdfminer.six"
            )

    def extract(self, path: str) -> str:
        """Dispatch to the correct extractor based on file extension."""
        ext = os.path.splitext(path)[1].lower()
        print(f"  Reading {ext.upper()} file…")
        handlers = {
            ".txt":  self.from_txt,
            ".epub": self.from_epub,
            ".pdf":  self.from_pdf,
        }
        if ext not in handlers:
            raise ValueError(f"Unsupported file type '{ext}'. Use .txt, .epub, or .pdf")
        return handlers[ext](path)
