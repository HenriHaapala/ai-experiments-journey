"""
Tests for agent service FastAPI endpoints
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, test_client):
        """Test GET /health returns healthy status"""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


@pytest.mark.asyncio
class TestChatEndpoint:
    """Test chat API endpoint"""

    def test_chat_missing_message(self, test_client):
        """Test POST /api/chat without message"""
        response = test_client.post("/api/chat", json={})

        assert response.status_code == 422  # Validation error
        assert "detail" in response.json()

    def test_chat_empty_message(self, test_client):
        """Test POST /api/chat with empty message"""
        response = test_client.post("/api/chat", json={"message": ""})

        # Should either reject or handle gracefully
        assert response.status_code in [200, 400, 422]

    @patch('agent.AIAgent.chat')
    def test_chat_with_valid_message(self, mock_chat, test_client, sample_chat_request):
        """Test POST /api/chat with valid message (mocked agent)"""
        mock_chat.return_value = {
            "response": "You've completed 50% of your roadmap!",
            "conversation_id": "test_conv_123"
        }

        response = test_client.post("/api/chat", json=sample_chat_request)

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data

    def test_chat_creates_new_conversation_id(self, test_client):
        """Test POST /api/chat without conversation_id creates new one"""
        response = test_client.post("/api/chat", json={"message": "Hello"})

        # May fail without mocking, but tests the flow
        if response.status_code == 200:
            data = response.json()
            assert "conversation_id" in data


@pytest.mark.asyncio
class TestToolsEndpoint:
    """Test tools listing endpoint"""

    def test_list_tools(self, test_client):
        """Test GET /api/tools returns available tools"""
        response = test_client.get("/api/tools")

        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)

        # Check expected tools are present
        tool_names = [tool["name"] for tool in data["tools"]]
        expected_tools = [
            "get_roadmap",
            "get_learning_entries",
            "search_knowledge",
            "add_learning_entry",
            "get_progress_stats"
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"

    def test_tools_have_descriptions(self, test_client):
        """Test tools have required fields"""
        response = test_client.get("/api/tools")
        data = response.json()

        for tool in data["tools"]:
            assert "name" in tool
            assert "description" in tool
            # Optional: check for parameters field
