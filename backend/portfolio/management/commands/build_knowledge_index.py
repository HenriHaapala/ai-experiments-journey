import os

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from dotenv import load_dotenv
import cohere

from portfolio.models import (
    RoadmapItem,
    LearningEntry,
    KnowledgeChunk,
    SiteContent,
)

from portfolio.utils.doc_loader import iter_documents

load_dotenv()

def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> list[str]:
    """
    Naive character-based chunking with overlap.
    Keeps chunks under max_chars and overlaps them by `overlap` characters
    so important info near boundaries isn't lost.
    """
    text = (text or "").strip()
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    length = len(text)

    # Make sure overlap is smaller than max_chars
    overlap = min(overlap, max_chars // 2)

    while start < length:
        end = min(length, start + max_chars)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == length:
            break
        start = end - overlap  # slide window with overlap

    return chunks

def embed_text(client: cohere.Client, text: str, model_name: str) -> list[float] | None:
    """
    Embed a single text with Cohere.
    Returns the vector, or None if it fails (after logging).
    """
    text = text.strip()
    if not text:
        return None

    # Avoid ridiculously long payloads
    if len(text) > 8000:
        text = text[:8000]

    try:
        resp = client.embed(
            texts=[text],
            model=model_name,
            input_type="search_document",
        )
        return resp.embeddings[0]
    except Exception as e:
        # We log and return None so that a single bad call doesn't kill the whole command
        print(f"[embed_text] Failed to embed text (len={len(text)}): {e}")
        return None


class Command(BaseCommand):
    help = (
        "Rebuild the unified knowledge index from roadmap items, learning entries, "
        "and site content."
    )

    def handle(self, *args, **options):
        api_key = os.getenv("COHERE_API_KEY")
        model_name = os.getenv("COHERE_EMBED_MODEL", "embed-english-v3.0")

        if not api_key:
            raise RuntimeError("COHERE_API_KEY is not set")

        client = cohere.Client(api_key)

        self.stdout.write(self.style.WARNING("Clearing existing knowledge index..."))
        KnowledgeChunk.objects.all().delete()

            # 1) Index roadmap items
        self.stdout.write(self.style.SUCCESS("Indexing roadmap items."))
        for item in RoadmapItem.objects.select_related("section").all():
            section = item.section
            base_content = (item.description or "").strip()
            if not base_content:
                base_content = item.title

            chunks = chunk_text(base_content)
            if not chunks:
                continue

            for idx, chunk_body in enumerate(chunks, start=1):
                text_to_embed = f"{item.title}\n\n{chunk_body}"
                emb = embed_text(client, text_to_embed, model_name)
                if emb is None:
                    self.stderr.write(
                        self.style.ERROR(
                            f"  Skipping roadmap item {item.id} chunk {idx} ('{item.title}') due to embedding failure."
                        )
                    )
                    continue

                KnowledgeChunk.objects.create(
                    source_type=KnowledgeChunk.SourceType.ROADMAP_ITEM,
                    source_id=item.id,
                    title=item.title,  # same title for all chunks
                    content=chunk_body,
                    section_title=section.title if section else "",
                    item_title=item.title,
                    tags="roadmap",
                    vector=emb,
                )


              # 2) Index learning entries
        self.stdout.write(self.style.SUCCESS("Indexing learning entries."))
        for entry in LearningEntry.objects.select_related(
            "roadmap_item", "roadmap_item__section"
        ).filter(is_public=True):
            base_content = entry.content or ""
            chunks = chunk_text(base_content)
            if not chunks:
                continue

            section_title = ""
            item_title = ""
            if entry.roadmap_item:
                item_title = entry.roadmap_item.title
                if entry.roadmap_item.section:
                    section_title = entry.roadmap_item.section.title

            for idx, chunk_body in enumerate(chunks, start=1):
                text_to_embed = f"{entry.title}\n\n{chunk_body}"
                emb = embed_text(client, text_to_embed, model_name)
                if emb is None:
                    self.stderr.write(
                        self.style.ERROR(
                            f"  Skipping learning entry {entry.id} chunk {idx} ('{entry.title}') due to embedding failure."
                        )
                    )
                    continue

                KnowledgeChunk.objects.create(
                    source_type=KnowledgeChunk.SourceType.LEARNING_ENTRY,
                    source_id=entry.id,
                    title=entry.title,
                    content=chunk_body,
                    section_title=section_title,
                    item_title=item_title,
                    tags="learning_entry",
                    vector=emb,
                )

                # 3) Index site content
        self.stdout.write(self.style.SUCCESS("Indexing site content."))
        for sc in SiteContent.objects.all():
            body = getattr(sc, "body", None)
            if body is None:
                body = getattr(sc, "content", "")

            chunks = chunk_text(body)
            if not chunks:
                continue

            raw_tags = getattr(sc, "tags", "")
            tags = f"site_content,{raw_tags}" if raw_tags else "site_content"

            for idx, chunk_body in enumerate(chunks, start=1):
                text_to_embed = f"{sc.title}\n\n{chunk_body}"
                emb = embed_text(client, text_to_embed, model_name)
                if emb is None:
                    self.stderr.write(
                        self.style.ERROR(
                            f"  Skipping site content {sc.id} chunk {idx} ('{sc.title}') due to embedding failure."
                        )
                    )
                    continue

                KnowledgeChunk.objects.create(
                    source_type=KnowledgeChunk.SourceType.SITE_CONTENT,
                    source_id=sc.id,
                    title=sc.title,
                    content=chunk_body,
                    section_title="",
                    item_title="",
                    tags=tags,
                    vector=emb,
                )


                # 4) Index docs from DOCS_ROOT (txt / md)
        self.stdout.write(self.style.SUCCESS("Indexing docs from DOCS_ROOT."))
        docs = list(iter_documents())
        if not docs:
            self.stdout.write(self.style.WARNING("No docs found."))
        else:
            for (rel_path, title, text) in docs:
                chunks = chunk_text(text)
                if not chunks:
                    continue

                for idx, chunk_body in enumerate(chunks, start=1):
                    emb = embed_text(client, chunk_body, model_name)
                    if emb is None:
                        self.stderr.write(
                            self.style.ERROR(
                                f"  Skipping doc '{rel_path}' chunk {idx} due to embedding failure."
                            )
                        )
                        continue

                    KnowledgeChunk.objects.create(
                        source_type=KnowledgeChunk.SourceType.DOCUMENT,
                        source_id=rel_path,
                        title=title,
                        content=chunk_body,
                        section_title="",
                        item_title="",
                        tags="doc",
                        vector=emb,
                    )