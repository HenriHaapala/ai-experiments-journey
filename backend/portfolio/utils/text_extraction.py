from pypdf import PdfReader


def extract_text_from_upload(uploaded_file):
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        texts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            t = t.strip()
            if t:
                texts.append(t)
        return "\n\n".join(texts)

    # txt / md / markdown
    data = uploaded_file.read()
    if isinstance(data, bytes):
        data = data.decode("utf-8", errors="ignore")
    return data
