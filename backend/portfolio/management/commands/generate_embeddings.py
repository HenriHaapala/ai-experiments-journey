import os
from typing import List

from django.core.management.base import BaseCommand
from django.db import transaction

import cohere
from dotenv import load_dotenv

from portfolio.models import LearningEntry, Embedding

# Load .env explicitly so COHERE_API_KEY is available
load_dotenv()

def get_cohere_client() -> cohere.Client:
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise RuntimeError("COHERE_API_KEY is not set in environment or .env file")
    return cohere.Client(api_key)


def get_embedding_for_text(
    client: cohere.Client,
    text: str,
    model: str,
) -> List[float]:
    """
    Call Cohere embeddings API and return the embedding vector.
    """
    # Optionally trim very long text
    if len(text) > 8000:
        text = text[:8000]

    response = client.embed(
        texts=[text],
        model=model,
        input_type="search_document",  # good default for RAG docs
    )

    # response.embeddings is a list of vectors; we sent one text, so take [0]
    return response.embeddings[0]


class Command(BaseCommand):
    help = "Generate embeddings for LearningEntry records using Cohere and store them in the Embedding table."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate embeddings even if they already exist.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        model_name = os.getenv("COHERE_EMBED_MODEL", "embed-english-v3.0")

        client = get_cohere_client()

        qs = LearningEntry.objects.filter(is_public=True)
        if not force:
            qs = qs.filter(embedding__isnull=True)

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No learning entries need embeddings."))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Generating embeddings for {total} LearningEntry object(s) with Cohere model '{model_name}'..."
            )
        )

        for i, entry in enumerate(qs.iterator(), start=1):
            text = f"{entry.title}\n\n{entry.content}"

            try:
                vector = get_embedding_for_text(client, text, model_name)
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"[{i}/{total}] Failed to get embedding for entry {entry.id}: {e}"
                    )
                )
                continue

            with transaction.atomic():
                Embedding.objects.update_or_create(
                    learning_entry=entry,
                    defaults={
                        "vector": vector,
                        "model": model_name,
                    },
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"[{i}/{total}] Embedded entry {entry.id} ({entry.title})"
                )
            )

        self.stdout.write(self.style.SUCCESS("Done generating embeddings with Cohere."))
