from django.contrib import admin
from django.db import transaction

from .models import (
    RoadmapSection,
    RoadmapItem,
    LearningEntry,
    Media,
    Embedding,
    SiteContent,
    DocumentUpload,
    KnowledgeChunk,
)
from .forms import DocumentUploadForm
from .utils.text_extraction import extract_text_from_upload

# import your REAL existing RAG functions:
from .management.commands.build_knowledge_index import chunk_text, embed_text
import cohere
import os
co = cohere.Client(os.getenv("COHERE_API_KEY"))
model_name = os.getenv("COHERE_EMBED_MODEL", "embed-english-v3.0")

class RoadmapItemInline(admin.TabularInline):
    model = RoadmapItem
    extra = 0


@admin.register(RoadmapSection)
class RoadmapSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    ordering = ("order", "id")
    inlines = [RoadmapItemInline]


@admin.register(RoadmapItem)
class RoadmapItemAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "order", "is_active")
    list_filter = ("section", "is_active")
    ordering = ("section", "order")


@admin.register(LearningEntry)
class LearningEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "roadmap_item", "created_at", "is_public")
    list_filter = ("is_public", "roadmap_item__section")
    search_fields = ("title", "content")


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("media_type", "learning_entry", "url")
    list_filter = ("media_type",)

@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ("learning_entry", "model", "created_at")
    search_fields = ("learning_entry__title", "model")

@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "body", "slug")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(DocumentUpload)
class DocumentUploadAdmin(admin.ModelAdmin):
    form = DocumentUploadForm
    list_display = ("title", "source_type", "original_filename", "created_at")
    readonly_fields = ("original_filename",)

    def save_model(self, request, obj, form, change):
        uploaded_file = form.cleaned_data["file"]
        filename = uploaded_file.name

        # Extract text
        text = extract_text_from_upload(uploaded_file)
        if not text.strip():
            raise ValueError("No extractable text found in uploaded document.")

        # Metadata
        if not obj.title:
            obj.title = filename
        obj.original_filename = filename

        with transaction.atomic():
            # Save DocumentUpload row
            super().save_model(request, obj, form, change)

            # 1) Chunk text (your real function)
            chunks = chunk_text(text)

            # 2) Embed + Create KnowledgeChunk rows
            kc_list = []
            for idx, chunk_body in enumerate(chunks, start=1):
                # use your real embed_text() EXACTLY as in indexer
                emb = embed_text(co, chunk_body, model_name)
                if emb is None:
                    continue  # skip failed embeddings, same as your indexer

                kc_list.append(
                    KnowledgeChunk(
                        source_type=KnowledgeChunk.SourceType.DOCUMENT,
                        source_id=obj.id,
                        title=obj.title,
                        content=chunk_body,
                        section_title="",
                        item_title="",
                        tags="uploaded_doc",
                        vector=emb,
                    )
                )

            KnowledgeChunk.objects.bulk_create(kc_list)