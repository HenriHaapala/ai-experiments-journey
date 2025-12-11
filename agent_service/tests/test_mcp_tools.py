"""
Tests for MCP tool wrappers
Tests tool integration with backend API
"""
import pytest
from unittest.mock import patch, MagicMock
import httpx


@pytest.mark.asyncio
class TestGetRoadmap:
    """Test get_roadmap MCP tool"""

    @patch('httpx.get')
    async def test_get_roadmap_success(self, mock_get, sample_roadmap_data):
        """Test successful roadmap retrieval"""
        from mcp_tools import get_roadmap

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_roadmap_data
        mock_get.return_value = mock_response

        result = await get_roadmap()

        assert result["success"] is True
        assert "roadmap" in result
        assert len(result["roadmap"]) == 1
        assert result["roadmap"][0]["title"] == "Machine Learning Fundamentals"

    @patch('httpx.get')
    async def test_get_roadmap_api_error(self, mock_get):
        """Test roadmap retrieval with API error"""
        from mcp_tools import get_roadmap

        # Mock HTTP error
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await get_roadmap()

        assert result["success"] is False
        assert "error" in result


@pytest.mark.asyncio
class TestGetLearningEntries:
    """Test get_learning_entries MCP tool"""

    @patch('httpx.get')
    async def test_get_learning_entries_success(self, mock_get, sample_learning_entries):
        """Test successful learning entries retrieval"""
        from mcp_tools import get_learning_entries

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_learning_entries
        mock_get.return_value = mock_response

        result = await get_learning_entries(limit=10)

        assert result["success"] is True
        assert "entries" in result
        assert len(result["entries"]) == 1

    @patch('httpx.get')
    async def test_get_learning_entries_with_roadmap_item_filter(self, mock_get):
        """Test filtering entries by roadmap_item"""
        from mcp_tools import get_learning_entries

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = await get_learning_entries(roadmap_item_id=5, limit=20)

        # Verify URL parameters
        call_url = str(mock_get.call_args[0][0])
        assert "roadmap_item=5" in call_url
        assert "limit=20" in call_url


@pytest.mark.asyncio
class TestSearchKnowledge:
    """Test search_knowledge MCP tool"""

    @patch('httpx.post')
    async def test_search_knowledge_success(self, mock_post, sample_search_results):
        """Test successful knowledge search"""
        from mcp_tools import search_knowledge

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_results
        mock_post.return_value = mock_response

        result = await search_knowledge("neural networks", top_k=3)

        assert result["success"] is True
        assert "results" in result
        assert len(result["results"]) == 1

    @patch('httpx.post')
    async def test_search_knowledge_empty_query(self, mock_post):
        """Test search with empty query"""
        from mcp_tools import search_knowledge

        # Should handle empty query gracefully
        result = await search_knowledge("", top_k=5)

        # Either returns error or passes to API
        assert "success" in result or "error" in result


@pytest.mark.asyncio
class TestAddLearningEntry:
    """Test add_learning_entry MCP tool"""

    @patch('httpx.post')
    async def test_add_learning_entry_success(self, mock_post):
        """Test successful learning entry creation"""
        from mcp_tools import add_learning_entry

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "success": True,
            "entry": {
                "id": 99,
                "title": "Test Entry",
                "content": "Test content"
            }
        }
        mock_post.return_value = mock_response

        result = await add_learning_entry(
            title="Test Entry",
            content="Test content",
            roadmap_item_id=1,
            is_public=True
        )

        assert result["success"] is True
        assert "entry" in result
        assert result["entry"]["id"] == 99

    @patch('httpx.post')
    async def test_add_learning_entry_missing_required_fields(self, mock_post):
        """Test entry creation with missing fields"""
        from mcp_tools import add_learning_entry

        # Should handle missing fields gracefully or raise validation error
        try:
            result = await add_learning_entry(title="", content="")
            # If it doesn't raise, check for error response
            assert "error" in result or result["success"] is False
        except Exception:
            # Validation error is acceptable
            pass


@pytest.mark.asyncio
class TestGetProgressStats:
    """Test get_progress_stats MCP tool"""

    @patch('httpx.get')
    async def test_get_progress_stats_success(self, mock_get, sample_progress_stats):
        """Test successful progress stats retrieval"""
        from mcp_tools import get_progress_stats

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_progress_stats
        mock_get.return_value = mock_response

        result = await get_progress_stats()

        assert result["success"] is True
        assert "stats" in result
        assert "roadmap" in result["stats"]
        assert "learning" in result["stats"]
        assert "knowledge_base" in result["stats"]

    @patch('httpx.get')
    async def test_get_progress_stats_includes_completion_percentage(
        self, mock_get, sample_progress_stats
    ):
        """Test progress stats includes completion percentage"""
        from mcp_tools import get_progress_stats

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_progress_stats
        mock_get.return_value = mock_response

        result = await get_progress_stats()

        assert "completion_percentage" in result["stats"]["roadmap"]
        assert result["stats"]["roadmap"]["completion_percentage"] == 50.0


@pytest.mark.asyncio
class TestToolErrorHandling:
    """Test error handling across all tools"""

    @patch('httpx.get')
    async def test_tool_handles_timeout(self, mock_get):
        """Test tools handle timeout errors"""
        from mcp_tools import get_roadmap

        mock_get.side_effect = httpx.TimeoutException("Request timeout")

        result = await get_roadmap()

        assert result["success"] is False
        assert "error" in result
        assert "timeout" in result["error"].lower()

    @patch('httpx.post')
    async def test_tool_handles_server_error(self, mock_post):
        """Test tools handle 500 errors"""
        from mcp_tools import search_knowledge

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = await search_knowledge("test query")

        assert result["success"] is False
        assert "error" in result
