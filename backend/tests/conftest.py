"""
Pytest configuration and fixtures for backend tests
"""
import pytest
from django.contrib.auth.models import User
from portfolio.models import (
    RoadmapSection, RoadmapItem, LearningEntry,
    Media, KnowledgeChunk, SiteContent
)


@pytest.fixture
def api_client():
    """Returns a Django REST framework API test client"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def roadmap_section(db):
    """Creates a test roadmap section"""
    return RoadmapSection.objects.create(
        title="Machine Learning Fundamentals",
        description="Core ML concepts and algorithms",
        order=1
    )


@pytest.fixture
def roadmap_item(db, roadmap_section):
    """Creates a test roadmap item"""
    return RoadmapItem.objects.create(
        section=roadmap_section,
        title="Neural Networks Basics",
        description="Introduction to neural networks",
        order=1,
        is_active=True
    )


@pytest.fixture
def learning_entry(db, roadmap_item):
    """Creates a test learning entry"""
    return LearningEntry.objects.create(
        roadmap_item=roadmap_item,
        title="Completed backpropagation tutorial",
        content="Learned about gradient descent and backpropagation algorithms",
        is_public=True
    )


@pytest.fixture
def learning_entry_private(db, roadmap_item):
    """Creates a private learning entry"""
    return LearningEntry.objects.create(
        roadmap_item=roadmap_item,
        title="Private research notes",
        content="My private notes on advanced techniques",
        is_public=False
    )


@pytest.fixture
def media_attachment(db, learning_entry):
    """Creates a test media attachment"""
    return Media.objects.create(
        learning_entry=learning_entry,
        media_type=Media.MediaType.IMAGE,
        url="https://example.com/image.png",
        caption="Example image"
    )


@pytest.fixture
def knowledge_chunk(db):
    """Creates a test knowledge chunk with fake embedding"""
    import numpy as np

    return KnowledgeChunk.objects.create(
        source_type=KnowledgeChunk.SourceType.LEARNING_ENTRY,
        source_id=1,
        title="Test Knowledge Chunk",
        content="This is test content about neural networks",
        section_title="Machine Learning",
        item_title="Neural Networks",
        tags="ml,ai,deep-learning",
        vector=np.random.rand(1024).tolist()  # Random 1024-dim vector
    )


@pytest.fixture
def site_content(db):
    """Creates a test site content page"""
    return SiteContent.objects.create(
        slug="about",
        title="About Henri",
        body="This is Henri's portfolio website",
        is_published=True
    )


@pytest.fixture
def authenticated_user(db):
    """Creates a test user"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
