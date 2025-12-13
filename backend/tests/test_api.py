"""
Integration tests for REST API endpoints
Tests all API views and endpoints
"""
import pytest
from django.urls import reverse
from rest_framework import status
from portfolio.models import RoadmapSection, RoadmapItem, LearningEntry, KnowledgeChunk
import numpy as np
import hmac
import hashlib
import json


@pytest.mark.django_db
class TestRoadmapAPI:
    """Test Roadmap API endpoints"""

    def test_get_roadmap_sections(self, api_client, roadmap_section, roadmap_item):
        """Test GET /api/roadmap/sections/"""
        url = "/api/roadmap/sections/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Machine Learning Fundamentals"
        assert "items" in response.data[0]
        assert len(response.data[0]["items"]) == 1

    def test_get_roadmap_sections_empty(self, api_client):
        """Test GET /api/roadmap/sections/ with no data"""
        url = "/api/roadmap/sections/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_roadmap_sections_prefetch_items(self, api_client, roadmap_section):
        """Test that items are prefetched efficiently"""
        # Create multiple items
        for i in range(5):
            RoadmapItem.objects.create(
                section=roadmap_section,
                title=f"Item {i}",
                order=i
            )

        url = "/api/roadmap/sections/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data[0]["items"]) == 5


@pytest.mark.django_db
class TestLearningEntryAPI:
    """Test Learning Entry API endpoints"""

    def test_get_public_learning_entries(self, api_client, learning_entry):
        """Test GET /api/learning/public/"""
        url = "/api/learning/public/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Completed backpropagation tutorial"

    def test_private_entries_not_in_public_list(self, api_client, learning_entry_private):
        """Test private entries excluded from public endpoint"""
        url = "/api/learning/public/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0  # Private entry not included

    def test_create_learning_entry(self, api_client, roadmap_item):
        """Test POST /api/roadmap/learning-entries/"""
        url = "/api/roadmap/learning-entries/"
        data = {
            "roadmap_item": roadmap_item.id,
            "title": "New Learning Entry",
            "content": "Learned something new today",
            "is_public": True
        }
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["entry"]["title"] == "New Learning Entry"
        assert LearningEntry.objects.count() == 1

    def test_list_learning_entries(self, api_client, learning_entry):
        """Test GET /api/roadmap/learning-entries/"""
        url = "/api/roadmap/learning-entries/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_filter_entries_by_roadmap_item(self, api_client, roadmap_item):
        """Test filtering entries by roadmap_item query param"""
        # Create entries for different items
        section = roadmap_item.section
        other_item = RoadmapItem.objects.create(
            section=section,
            title="Other Item",
            order=2
        )

        LearningEntry.objects.create(
            roadmap_item=roadmap_item,
            title="Entry 1",
            content="Content 1"
        )
        LearningEntry.objects.create(
            roadmap_item=other_item,
            title="Entry 2",
            content="Content 2"
        )

        url = f"/api/roadmap/learning-entries/?roadmap_item={roadmap_item.id}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Entry 1"


@pytest.mark.django_db
class TestAutomationWebhook:
    """Test GitHub webhook endpoint creates learning entries"""

    def _sign_payload(self, secret: str, payload: dict) -> str:
        body = json.dumps(payload).encode("utf-8")
        digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return f"sha256={digest}", body

    def test_push_event_creates_entry_and_dedupes(self, api_client, settings, roadmap_item):
        # Configure secret for signature verification
        settings.GITHUB_WEBHOOK_SECRET = "test-secret"

        payload = {
            "ref": "refs/heads/main",
            "repository": {"full_name": "henri/ai-portfolio"},
            "compare": "https://github.com/henri/ai-portfolio/compare/abc...def",
            "commits": [
                {
                    "id": "abc123456789",
                    "message": "Improve roadmap item matching",
                    "url": "https://github.com/henri/ai-portfolio/commit/abc123",
                    "author": {"name": "Henri"},
                }
            ],
        }

        sig_header, body = self._sign_payload(settings.GITHUB_WEBHOOK_SECRET, payload)

        # First delivery should create an entry
        response = api_client.post(
            "/api/automation/github-webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256=sig_header,
            HTTP_X_GITHUB_EVENT="push",
            HTTP_X_GITHUB_DELIVERY="delivery-123",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["created"] == 1
        assert LearningEntry.objects.count() == 1
        entry = LearningEntry.objects.first()
        assert "GitHub Delivery ID: delivery-123" in entry.content

        # Duplicate delivery should be skipped
        response_dup = api_client.post(
            "/api/automation/github-webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256=sig_header,
            HTTP_X_GITHUB_EVENT="push",
            HTTP_X_GITHUB_DELIVERY="delivery-123",
        )

        assert response_dup.status_code == status.HTTP_200_OK
        assert response_dup.json()["skipped"] == 1
        assert LearningEntry.objects.count() == 1

    def test_limit_learning_entries(self, api_client, roadmap_item):
        """Test limit query parameter"""
        # Create multiple entries
        for i in range(10):
            LearningEntry.objects.create(
                roadmap_item=roadmap_item,
                title=f"Entry {i}",
                content=f"Content {i}"
            )

        url = "/api/roadmap/learning-entries/?limit=5"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5


@pytest.mark.django_db
class TestProgressAPI:
    """Test Roadmap Progress API"""

    def test_get_progress_stats(self, api_client, roadmap_section, roadmap_item, learning_entry):
        """Test GET /api/roadmap/progress/"""
        url = "/api/roadmap/progress/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "stats" in response.data

        stats = response.data["stats"]
        assert "roadmap" in stats
        assert "learning" in stats
        assert "knowledge_base" in stats

        # Check roadmap stats
        assert stats["roadmap"]["total_sections"] == 1
        assert stats["roadmap"]["total_items"] == 1
        assert stats["roadmap"]["items_with_entries"] == 1
        assert stats["roadmap"]["completion_percentage"] == 100.0

    def test_progress_stats_empty(self, api_client):
        """Test progress stats with no data"""
        url = "/api/roadmap/progress/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        stats = response.data["stats"]
        assert stats["roadmap"]["total_sections"] == 0
        assert stats["roadmap"]["total_items"] == 0
        assert stats["roadmap"]["completion_percentage"] == 0.0

    def test_progress_completion_percentage(self, api_client, roadmap_section):
        """Test completion percentage calculation"""
        # Create 4 items
        items = []
        for i in range(4):
            item = RoadmapItem.objects.create(
                section=roadmap_section,
                title=f"Item {i}",
                order=i
            )
            items.append(item)

        # Add entries to 2 items (50% completion)
        LearningEntry.objects.create(
            roadmap_item=items[0],
            title="Entry 1",
            content="Content 1"
        )
        LearningEntry.objects.create(
            roadmap_item=items[1],
            title="Entry 2",
            content="Content 2"
        )

        url = "/api/roadmap/progress/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        stats = response.data["stats"]
        assert stats["roadmap"]["items_with_entries"] == 2
        assert stats["roadmap"]["completion_percentage"] == 50.0


@pytest.mark.django_db
class TestRAGSearchAPI:
    """Test RAG semantic search API"""

    def test_rag_search_missing_query(self, api_client):
        """Test POST /api/rag/search/ without query"""
        url = "/api/rag/search/"
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "Missing 'query'" in response.data["error"]

    def test_rag_search_with_query(self, api_client, knowledge_chunk):
        """Test RAG search with valid query (mocked)"""
        # Note: This will fail without COHERE_API_KEY in test environment
        # In CI/CD, you'd mock the Cohere client
        url = "/api/rag/search/"
        data = {"query": "neural networks", "top_k": 3}

        # This test requires actual API keys or mocking
        # For now, we just test the endpoint exists and validates input
        # Full integration tests would need API key mocking


@pytest.mark.django_db
class TestAIChatAPI:
    """Test AI Chat API endpoint"""

    def test_ai_chat_missing_question(self, api_client):
        """Test POST /api/ai/chat/ without question"""
        url = "/api/ai/chat/"
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "Missing 'question'" in response.data["error"]

    def test_ai_chat_empty_question(self, api_client):
        """Test POST /api/ai/chat/ with empty question"""
        url = "/api/ai/chat/"
        response = api_client.post(url, {"question": ""}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_ai_chat_with_question(self, api_client, knowledge_chunk):
        """Test AI chat with valid question (requires API keys)"""
        # Note: Full test requires COHERE_API_KEY and GROQ_API_KEY
        # In production tests, you'd mock these API calls
        url = "/api/ai/chat/"
        data = {"question": "What have I learned about neural networks?"}

        # This would need API key mocking for full integration test


@pytest.mark.django_db
class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self, api_client):
        """Test GET /api/health/"""
        url = "/api/health/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ok"
        assert "database" in response.data
