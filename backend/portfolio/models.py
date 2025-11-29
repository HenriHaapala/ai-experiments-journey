from django.db import models
from pgvector.django import VectorField

class RoadmapSection(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title


class RoadmapItem(models.Model):
    section = models.ForeignKey(
        RoadmapSection,
        on_delete=models.CASCADE,
        related_name="items",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["section", "order", "id"]

    def __str__(self) -> str:
        return f"{self.section.title} – {self.title}"


class LearningEntry(models.Model):
    roadmap_item = models.ForeignKey(
        RoadmapItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="learning_entries",
    )
    title = models.CharField(max_length=255)
    content = models.TextField()  # markdown / notes / description of what you did
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        if self.roadmap_item:
            return f"{self.roadmap_item.title}: {self.title}"
        return self.title


class Media(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        LINK = "link", "Link"
        FILE = "file", "File"

    learning_entry = models.ForeignKey(
        LearningEntry,
        on_delete=models.CASCADE,
        related_name="media",
    )
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    url = models.URLField(max_length=500)
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"{self.media_type}: {self.url[:50]}"

class Embedding(models.Model):
    learning_entry = models.OneToOneField(
        LearningEntry,
        on_delete=models.CASCADE,
        related_name="embedding",
    )
    # Cohere embed-english-v3.0 → 1024 dims
    vector = VectorField(dimensions=1024)
    model = models.CharField(max_length=100, default="embed-english-v3.0")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Embedding"
        verbose_name_plural = "Embeddings"

    def __str__(self) -> str:
        return f"Embedding for entry {self.learning_entry_id}"
    
class SiteContent(models.Model):
    slug = models.SlugField(unique=True, null=True, blank=True)
    title = models.CharField(max_length=200)
    body = models.TextField()

    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return self.title

class KnowledgeChunk(models.Model):
    class SourceType(models.TextChoices):
        LEARNING_ENTRY = "learning_entry", "Learning Entry"
        ROADMAP_ITEM = "roadmap_item", "Roadmap Item"
        SITE_CONTENT = "site_content", "Site Content"
        DOCUMENT = "document", "Document"  # for future docs

    source_type = models.CharField(
        max_length=50,
        choices=SourceType.choices,
    )
    # ID in the original table (LearningEntry, RoadmapItem, etc.)
    source_id = models.IntegerField(null=True, blank=True)

    title = models.CharField(max_length=255)
    content = models.TextField()

    section_title = models.CharField(max_length=255, blank=True)
    item_title = models.CharField(max_length=255, blank=True)
    tags = models.CharField(max_length=255, blank=True)

    # Cohere embed-english-v3.0 → 1024 dimensions
    vector = VectorField(dimensions=1024)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"[{self.source_type}] {self.title}"
