from rest_framework import serializers
from .models import RoadmapSection, RoadmapItem, LearningEntry, Media


class RoadmapItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadmapItem
        fields = ["id", "title", "description", "order", "is_active", "status"]


class RoadmapSectionSerializer(serializers.ModelSerializer):
    items = RoadmapItemSerializer(many=True, read_only=True)

    class Meta:
        model = RoadmapSection
        fields = ["id", "title", "description", "order", "items"]


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ["id", "media_type", "url", "caption"]


class LearningEntrySerializer(serializers.ModelSerializer):
    roadmap_item_title = serializers.CharField(
        source="roadmap_item.title", read_only=True
    )
    section_title = serializers.CharField(
        source="roadmap_item.section.title", read_only=True
    )
    media = MediaSerializer(many=True, read_only=True)

    class Meta:
        model = LearningEntry
        fields = [
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "is_public",
            "roadmap_item",
            "roadmap_item_title",
            "section_title",
            "media",
        ]
