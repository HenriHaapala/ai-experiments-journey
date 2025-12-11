"""
Pytest configuration and fixtures for agent service tests
"""
import pytest
import os
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Returns a FastAPI test client"""
    from api import app
    return TestClient(app)


@pytest.fixture
def mock_backend_url():
    """Returns mock backend URL for testing"""
    return os.getenv("BACKEND_URL", "http://localhost:8000")


@pytest.fixture
def mock_redis_url():
    """Returns mock Redis URL for testing"""
    return os.getenv("REDIS_URL", "redis://localhost:6379")


@pytest.fixture
def sample_chat_request():
    """Returns a sample chat request"""
    return {
        "message": "What is my learning progress?",
        "conversation_id": "test_conv_123"
    }


@pytest.fixture
def sample_roadmap_data():
    """Returns sample roadmap data"""
    return [
        {
            "id": 1,
            "title": "Machine Learning Fundamentals",
            "description": "Core ML concepts",
            "order": 1,
            "items": [
                {
                    "id": 1,
                    "title": "Neural Networks Basics",
                    "description": "Introduction to neural networks",
                    "order": 1,
                    "is_active": True
                }
            ]
        }
    ]


@pytest.fixture
def sample_learning_entries():
    """Returns sample learning entries"""
    return [
        {
            "id": 1,
            "title": "Completed backpropagation tutorial",
            "content": "Learned about gradient descent",
            "roadmap_item": {
                "id": 1,
                "title": "Neural Networks Basics"
            },
            "created_at": "2025-12-01T10:00:00Z",
            "is_public": True
        }
    ]


@pytest.fixture
def sample_progress_stats():
    """Returns sample progress statistics"""
    return {
        "success": True,
        "stats": {
            "roadmap": {
                "total_sections": 5,
                "total_items": 24,
                "active_items": 18,
                "items_with_entries": 12,
                "completion_percentage": 50.0
            },
            "learning": {
                "total_entries": 45,
                "public_entries": 42,
                "private_entries": 3
            },
            "knowledge_base": {
                "total_chunks": 41,
                "by_source": {
                    "learning_entry": 38,
                    "roadmap_item": 2,
                    "site_content": 1,
                    "document": 0
                }
            }
        }
    }


@pytest.fixture
def sample_search_results():
    """Returns sample knowledge search results"""
    return {
        "success": True,
        "query": "neural networks",
        "top_k": 3,
        "results": [
            {
                "id": 1,
                "source_type": "learning_entry",
                "title": "Neural Networks Basics",
                "content": "Neural networks are composed of layers",
                "section_title": "Machine Learning",
                "item_title": "Neural Networks",
                "similarity": 0.85
            }
        ]
    }
