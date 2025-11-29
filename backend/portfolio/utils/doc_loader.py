import os
from django.conf import settings

SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown"}

def iter_documents():
    """
    Yield (relative_path, title, text) for each document under settings.DOCS_ROOT.
    """
    docs_root = getattr(settings, "DOCS_ROOT", None)
    if not docs_root or not os.path.isdir(docs_root):
        return

    for root, dirs, files in os.walk(docs_root):
        for fname in files:
            _, ext = os.path.splitext(fname)
            if ext.lower() not in SUPPORTED_EXTENSIONS:
                continue

            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, docs_root)

            with open(full_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Try to grab a title from the first line, or fallback to filename
            first_line = text.strip().splitlines()[0] if text.strip() else ""
            title = first_line.lstrip("# ").strip() or fname

            yield rel_path, title, text
