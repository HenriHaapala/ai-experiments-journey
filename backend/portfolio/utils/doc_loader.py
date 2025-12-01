import os
from django.conf import settings
from pathlib import Path
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf"}   # ← PDF added


def load_pdf_file(path: Path) -> str:
    """
    Extract text from a PDF file for RAG ingestion.
    Returns a single big string, which will go through
    the existing chunking pipeline.
    """
    reader = PdfReader(str(path))
    texts = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        page_text = page_text.strip()
        if page_text:
            texts.append(page_text)

    return "\n\n".join(texts)


def iter_documents():
    """
    Yield (relative_path, title, text) for each document under settings.DOCS_ROOT.
    Supports: .txt, .md, .markdown, .pdf
    """
    docs_root = getattr(settings, "DOCS_ROOT", None)
    if not docs_root or not os.path.isdir(docs_root):
        return

    for root, dirs, files in os.walk(docs_root):
        for fname in files:
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, docs_root)
            ext = Path(fname).suffix.lower()

            # Skip anything not in our supported list
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            # ------------------------------
            # TEXT / MARKDOWN DOCUMENTS
            # ------------------------------
            if ext in {".txt", ".md", ".markdown"}:
                with open(full_path, "r", encoding="utf-8") as f:
                    text = f.read()

                # Title = first line or filename
                first_line = text.strip().splitlines()[0] if text.strip() else ""
                title = first_line.lstrip("# ").strip() or fname

                yield rel_path, title, text

            # ------------------------------
            # PDF DOCUMENTS
            # ------------------------------
            elif ext == ".pdf":
                text = load_pdf_file(Path(full_path))

                if not text.strip():
                    continue  # skip empty PDFs

                # Title: try to use first text line, else filename
                first_line = text.splitlines()[0].strip() if text.strip() else ""
                title = first_line or fname

                yield rel_path, title, text

