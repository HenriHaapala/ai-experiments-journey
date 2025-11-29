from django.contrib import admin
from .models import RoadmapSection, RoadmapItem, LearningEntry, Media, Embedding, SiteContent


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