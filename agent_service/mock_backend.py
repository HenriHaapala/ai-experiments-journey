"""
Mock backend for testing agent service without real Django backend
"""
import json
from typing import Dict, Any, Optional


class MockBackend:
    """
    Mock backend that returns sample data for testing
    """

    @staticmethod
    def get_roadmap() -> Dict[str, Any]:
        """Mock roadmap data"""
        return {
            "success": True,
            "roadmap": [
                {
                    "id": 1,
                    "title": "Machine Learning Fundamentals",
                    "description": "Core concepts and algorithms",
                    "order": 1,
                    "items": [
                        {
                            "id": 1,
                            "title": "Neural Networks Basics",
                            "description": "Understanding perceptrons and backpropagation",
                            "order": 1,
                            "is_active": True
                        },
                        {
                            "id": 2,
                            "title": "Deep Learning",
                            "description": "CNNs, RNNs, and Transformers",
                            "order": 2,
                            "is_active": True
                        }
                    ]
                },
                {
                    "id": 2,
                    "title": "AI Engineering",
                    "description": "Production ML systems",
                    "order": 2,
                    "items": [
                        {
                            "id": 3,
                            "title": "Model Deployment",
                            "description": "Serving models in production",
                            "order": 1,
                            "is_active": False
                        }
                    ]
                }
            ],
            "total_sections": 2,
            "total_items": 3
        }

    @staticmethod
    def get_learning_entries(roadmap_item_id: Optional[int] = None, limit: int = 10) -> Dict[str, Any]:
        """Mock learning entries"""
        entries = [
            {
                "id": 1,
                "title": "Completed Neural Networks course",
                "content": "Learned about feedforward networks, backpropagation, and gradient descent",
                "roadmap_item": "Neural Networks Basics",
                "is_public": True,
                "created_at": "2025-12-01T10:00:00Z"
            },
            {
                "id": 2,
                "title": "Built a CNN for image classification",
                "content": "Implemented ResNet-18 for CIFAR-10 dataset, achieved 92% accuracy",
                "roadmap_item": "Deep Learning",
                "is_public": True,
                "created_at": "2025-12-03T15:30:00Z"
            }
        ]

        # Filter by roadmap_item_id if provided
        if roadmap_item_id:
            entries = [e for e in entries if roadmap_item_id in [1, 2]][:limit]

        return {
            "success": True,
            "entries": entries[:limit],
            "count": len(entries[:limit])
        }

    @staticmethod
    def search_knowledge(query: str, top_k: int = 5) -> Dict[str, Any]:
        """Mock knowledge search"""
        all_results = [
            {
                "id": 1,
                "title": "Neural Networks Basics",
                "content": "Neural networks are computing systems inspired by biological neural networks...",
                "source_type": "roadmap_item",
                "section_title": "Machine Learning Fundamentals",
                "similarity": 0.92
            },
            {
                "id": 2,
                "title": "Backpropagation Algorithm",
                "content": "Backpropagation is a method for calculating gradients in neural networks...",
                "source_type": "learning_entry",
                "section_title": "Machine Learning Fundamentals",
                "similarity": 0.88
            },
            {
                "id": 3,
                "title": "Deep Learning Architectures",
                "content": "CNNs for vision, RNNs for sequences, Transformers for attention...",
                "source_type": "learning_entry",
                "section_title": "Machine Learning Fundamentals",
                "similarity": 0.75
            }
        ]

        return {
            "success": True,
            "results": all_results[:top_k],
            "query": query,
            "count": min(len(all_results), top_k)
        }

    @staticmethod
    def add_learning_entry(title: str, content: str, roadmap_item_id: Optional[int] = None,
                           is_public: bool = True) -> Dict[str, Any]:
        """Mock create learning entry"""
        return {
            "success": True,
            "entry": {
                "id": 999,
                "title": title,
                "content": content,
                "roadmap_item_id": roadmap_item_id,
                "is_public": is_public,
                "created_at": "2025-12-06T20:00:00Z"
            }
        }

    @staticmethod
    def get_progress_stats() -> Dict[str, Any]:
        """Mock progress statistics"""
        return {
            "success": True,
            "stats": {
                "roadmap": {
                    "total_sections": 2,
                    "total_items": 3,
                    "active_items": 2,
                    "items_with_entries": 2,
                    "completion_percentage": 66.7
                },
                "learning": {
                    "total_entries": 2,
                    "public_entries": 2,
                    "private_entries": 0
                },
                "knowledge_base": {
                    "total_chunks": 15,
                    "by_source": {
                        "learning_entry": 2,
                        "roadmap_item": 3,
                        "site_content": 0,
                        "document": 10
                    }
                }
            }
        }


def get_mock_data(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Get mock data for an endpoint

    Args:
        endpoint: API endpoint path
        method: HTTP method
        data: Request data

    Returns:
        Mock response data
    """
    mock = MockBackend()

    # Route to appropriate mock method
    if "/api/roadmap/sections/" in endpoint:
        return mock.get_roadmap()
    elif "/api/roadmap/learning-entries/" in endpoint:
        # Parse query parameters from endpoint
        roadmap_item_id = None
        limit = 10
        if "?" in endpoint:
            params = endpoint.split("?")[1]
            for param in params.split("&"):
                if "=" in param:
                    key, value = param.split("=")
                    if key == "roadmap_item":
                        roadmap_item_id = int(value)
                    elif key == "limit":
                        limit = int(value)
        return mock.get_learning_entries(roadmap_item_id, limit)
    elif "/api/rag/search/" in endpoint:
        query = data.get("query", "") if data else ""
        top_k = data.get("top_k", 5) if data else 5
        return mock.search_knowledge(query, top_k)
    elif "/api/roadmap/progress/" in endpoint:
        return mock.get_progress_stats()
    else:
        return {"success": False, "error": f"Mock endpoint not found: {endpoint}"}
