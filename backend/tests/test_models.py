"""
Unit tests for portfolio models
Tests database models and their relationships
"""
import pytest
from django.core.exceptions import ValidationError
from portfolio.models import (
    RoadmapSection, RoadmapItem, LearningEntry,
    Media, KnowledgeChunk, SiteContent
)


@pytest.mark.django_db
class TestRoadmapSection:
    """Test RoadmapSection model"""

    def test_create_roadmap_section(self):
        """Test creating a roadmap section"""
        section = RoadmapSection.objects.create(
            title="Backend Development",
            description="Learn backend technologies",
            order=1
        )
        assert section.title == "Backend Development"
        assert section.order == 1
        assert str(section) == "Backend Development"

    def test_roadmap_section_ordering(self):
        """Test sections are ordered correctly"""
        section1 = RoadmapSection.objects.create(title="Section 1", order=2)
        section2 = RoadmapSection.objects.create(title="Section 2", order=1)

        sections = list(RoadmapSection.objects.all())
        assert sections[0].title == "Section 2"  # Lower order first
        assert sections[1].title == "Section 1"


@pytest.mark.django_db
class TestRoadmapItem:
    """Test RoadmapItem model"""

    def test_create_roadmap_item(self, roadmap_section):
        """Test creating a roadmap item"""
        item = RoadmapItem.objects.create(
            section=roadmap_section,
            title="Django REST Framework",
            description="Learn DRF",
            order=1,
            is_active=True
        )
        assert item.title == "Django REST Framework"
        assert item.section == roadmap_section
        assert item.is_active is True
        assert str(item) == f"{roadmap_section.title} – Django REST Framework"

    def test_roadmap_item_relationship(self, roadmap_section):
        """Test roadmap item belongs to section"""
        item1 = RoadmapItem.objects.create(
            section=roadmap_section,
            title="Item 1",
            order=1
        )
        item2 = RoadmapItem.objects.create(
            section=roadmap_section,
            title="Item 2",
            order=2
        )

        items = roadmap_section.items.all()
        assert items.count() == 2
        assert item1 in items
        assert item2 in items

    def test_roadmap_item_cascade_delete(self, roadmap_section):
        """Test items are deleted when section is deleted"""
        RoadmapItem.objects.create(
            section=roadmap_section,
            title="Test Item",
            order=1
        )
        assert RoadmapItem.objects.count() == 1

        roadmap_section.delete()
        assert RoadmapItem.objects.count() == 0


@pytest.mark.django_db
class TestLearningEntry:
    """Test LearningEntry model"""

    def test_create_learning_entry(self, roadmap_item):
        """Test creating a learning entry"""
        entry = LearningEntry.objects.create(
            roadmap_item=roadmap_item,
            title="Completed Tutorial",
            content="# Notes\nLearned about REST APIs",
            is_public=True
        )
        assert entry.title == "Completed Tutorial"
        assert entry.roadmap_item == roadmap_item
        assert entry.is_public is True
        assert "REST APIs" in entry.content

    def test_learning_entry_without_roadmap_item(self):
        """Test creating entry without roadmap item (standalone)"""
        entry = LearningEntry.objects.create(
            title="General Learning Note",
            content="Random learning content",
            is_public=True
        )
        assert entry.roadmap_item is None
        assert str(entry) == "General Learning Note"

    def test_learning_entry_ordering(self, roadmap_item):
        """Test entries ordered by created_at (newest first)"""
        entry1 = LearningEntry.objects.create(
            roadmap_item=roadmap_item,
            title="Entry 1",
            content="First entry"
        )
        entry2 = LearningEntry.objects.create(
            roadmap_item=roadmap_item,
            title="Entry 2",
            content="Second entry"
        )

        entries = list(LearningEntry.objects.all())
        assert entries[0].title == "Entry 2"  # Newest first
        assert entries[1].title == "Entry 1"

    def test_learning_entry_set_null_on_item_delete(self, roadmap_item):
        """Test entry's roadmap_item set to null when item deleted"""
        entry = LearningEntry.objects.create(
            roadmap_item=roadmap_item,
            title="Test Entry",
            content="Content"
        )
        assert entry.roadmap_item is not None

        roadmap_item.delete()
        entry.refresh_from_db()
        assert entry.roadmap_item is None


@pytest.mark.django_db
class TestMedia:
    """Test Media model"""

    def test_create_media_attachment(self, learning_entry):
        """Test creating media attachment"""
        media = Media.objects.create(
            learning_entry=learning_entry,
            media_type=Media.MediaType.IMAGE,
            url="https://example.com/image.jpg",
            caption="Test image"
        )
        assert media.media_type == Media.MediaType.IMAGE
        assert media.learning_entry == learning_entry
        assert "image.jpg" in str(media)

    def test_media_types(self, learning_entry):
        """Test all media types"""
        types = [
            Media.MediaType.IMAGE,
            Media.MediaType.VIDEO,
            Media.MediaType.LINK,
            Media.MediaType.FILE
        ]

        for media_type in types:
            Media.objects.create(
                learning_entry=learning_entry,
                media_type=media_type,
                url=f"https://example.com/{media_type}.file"
            )

        assert Media.objects.count() == 4

    def test_media_cascade_delete(self, learning_entry):
        """Test media deleted when learning entry deleted"""
        Media.objects.create(
            learning_entry=learning_entry,
            media_type=Media.MediaType.IMAGE,
            url="https://example.com/test.jpg"
        )
        assert Media.objects.count() == 1

        learning_entry.delete()
        assert Media.objects.count() == 0


@pytest.mark.django_db
class TestKnowledgeChunk:
    """Test KnowledgeChunk model for RAG"""

    def test_create_knowledge_chunk(self):
        """Test creating knowledge chunk with vector"""
        import numpy as np

        chunk = KnowledgeChunk.objects.create(
            source_type=KnowledgeChunk.SourceType.LEARNING_ENTRY,
            source_id=123,
            title="Neural Networks",
            content="Neural networks are composed of layers",
            section_title="ML Fundamentals",
            item_title="Deep Learning",
            tags="ai,ml,neural-networks",
            vector=np.random.rand(1024).tolist()
        )

        assert chunk.source_type == KnowledgeChunk.SourceType.LEARNING_ENTRY
        assert chunk.source_id == 123
        assert len(chunk.vector) == 1024
        assert str(chunk) == "[learning_entry] Neural Networks"

    def test_knowledge_chunk_source_types(self):
        """Test all supported source types"""
        import numpy as np
        source_types = [
            KnowledgeChunk.SourceType.LEARNING_ENTRY,
            KnowledgeChunk.SourceType.ROADMAP_ITEM,
            KnowledgeChunk.SourceType.SITE_CONTENT,
            KnowledgeChunk.SourceType.DOCUMENT
        ]

        for source_type in source_types:
            KnowledgeChunk.objects.create(
                source_type=source_type,
                title=f"Test {source_type}",
                content="Test content",
                vector=np.random.rand(1024).tolist()
            )

        assert KnowledgeChunk.objects.count() == 4


@pytest.mark.django_db
class TestSiteContent:
    """Test SiteContent model"""

    def test_create_site_content(self):
        """Test creating site content page"""
        content = SiteContent.objects.create(
            slug="about",
            title="About Me",
            body="# About\nThis is my portfolio",
            is_published=True
        )
        assert content.slug == "about"
        assert content.is_published is True
        assert str(content) == "About Me"

    def test_site_content_unique_slug(self):
        """Test slug must be unique"""
        SiteContent.objects.create(
            slug="test",
            title="Test 1",
            body="Body 1"
        )

        with pytest.raises(Exception):  # IntegrityError
            SiteContent.objects.create(
                slug="test",
                title="Test 2",
                body="Body 2"
            )
