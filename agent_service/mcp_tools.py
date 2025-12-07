"""
MCP (Model Context Protocol) Tools Integration
Wraps MCP server tools for LangChain agent usage
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List

import httpx
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# Enable mock mode for testing
USE_MOCK = os.getenv("USE_MOCK_BACKEND", "false").lower() == "true"

if USE_MOCK:
    from mock_backend import get_mock_data
    logger.info("Using MOCK backend for testing")


class MCPToolExecutor:
    """
    Executes MCP tools by calling the backend Django API
    """

    def __init__(self, backend_url: str = BACKEND_URL):
        """
        Initialize MCP tool executor

        Args:
            backend_url: URL of the Django backend service
        """
        self.backend_url = backend_url
        self.client = httpx.Client(timeout=30.0)
        logger.info(f"MCPToolExecutor initialized with backend: {backend_url}")

    def _call_backend(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Call Django backend API (or mock for testing)

        Args:
            endpoint: API endpoint path
            method: HTTP method
            data: Request data for POST requests

        Returns:
            Response data as dictionary
        """
        # Use mock data if enabled
        if USE_MOCK:
            logger.info(f"Mock call: {method} {endpoint}")
            return get_mock_data(endpoint, method, data)

        url = f"{self.backend_url}{endpoint}"

        try:
            if method == "GET":
                response = self.client.get(url)
            elif method == "POST":
                response = self.client.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling {url}: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error calling {url}: {e}")
            return {"success": False, "error": str(e)}

    def get_roadmap(self) -> str:
        """Get the complete AI Career Roadmap"""
        result = self._call_backend("/api/roadmap/sections/")
        return json.dumps(result, indent=2)

    def get_learning_entries(self, roadmap_item_id: Optional[int] = None, limit: int = 10) -> str:
        """
        Get learning log entries

        Args:
            roadmap_item_id: Optional filter by roadmap item ID
            limit: Maximum number of entries to return
        """
        endpoint = f"/api/roadmap/learning-entries/?limit={limit}"
        if roadmap_item_id:
            endpoint += f"&roadmap_item={roadmap_item_id}"

        result = self._call_backend(endpoint)
        return json.dumps(result, indent=2)

    def search_knowledge(self, query: str, top_k: int = 5) -> str:
        """
        Semantic search across all portfolio knowledge

        Args:
            query: Search query
            top_k: Number of results to return
        """
        result = self._call_backend(
            "/api/rag/search/",
            method="POST",
            data={"query": query, "top_k": top_k}
        )
        return json.dumps(result, indent=2)

    def add_learning_entry(
        self,
        title: str,
        content: str,
        roadmap_item_id: Optional[int] = None,
        is_public: bool = True
    ) -> str:
        """
        Create a new learning log entry

        Args:
            title: Title of the learning entry
            content: Content/description of what was learned
            roadmap_item_id: Optional roadmap item to link to
            is_public: Whether the entry is public
        """
        data = {
            "title": title,
            "content": content,
            "is_public": is_public
        }
        if roadmap_item_id:
            data["roadmap_item"] = roadmap_item_id

        result = self._call_backend(
            "/api/roadmap/learning-entries/",
            method="POST",
            data=data
        )
        return json.dumps(result, indent=2)

    def get_progress_stats(self) -> str:
        """Get portfolio progress statistics and metrics"""
        result = self._call_backend("/api/roadmap/progress/")
        return json.dumps(result, indent=2)


# Pydantic models for tool inputs
class SearchKnowledgeInput(BaseModel):
    query: str = Field(..., description="Search query for semantic knowledge search")
    top_k: int = Field(5, description="Number of results to return (default: 5)")


class AddLearningEntryInput(BaseModel):
    title: str = Field(..., description="Title of the learning entry")
    content: str = Field(..., description="Detailed content of what was learned")
    roadmap_item_id: Optional[int] = Field(None, description="Optional roadmap item ID to link to")
    is_public: bool = Field(True, description="Whether the entry is public (default: True)")


class GetLearningEntriesInput(BaseModel):
    roadmap_item_id: Optional[int] = Field(None, description="Optional roadmap item ID to filter by")
    limit: int = Field(10, description="Maximum number of entries to return (default: 10)")


def create_langchain_tools(executor: Optional[MCPToolExecutor] = None) -> List[StructuredTool]:
    """
    Create LangChain StructuredTool instances from MCP tools

    Args:
        executor: MCPToolExecutor instance (creates new one if not provided)

    Returns:
        List of LangChain StructuredTool instances
    """
    if executor is None:
        executor = MCPToolExecutor()

    tools = [
        StructuredTool.from_function(
            func=executor.get_roadmap,
            name="get_roadmap",
            description=(
                "Get the complete AI Career Roadmap with all sections and items. "
                "Use this to understand the learning structure and plan what to learn next. "
                "Returns a hierarchical structure with sections containing multiple roadmap items."
            )
        ),
        StructuredTool.from_function(
            func=executor.get_learning_entries,
            name="get_learning_entries",
            description=(
                "Get learning log entries, optionally filtered by roadmap item. "
                "Use this to see what has been learned previously. "
                "Returns a list of learning entries with titles, content, and timestamps."
            ),
            args_schema=GetLearningEntriesInput
        ),
        StructuredTool.from_function(
            func=executor.search_knowledge,
            name="search_knowledge",
            description=(
                "Perform semantic search across all portfolio knowledge using RAG. "
                "Use this to find information about specific topics or concepts. "
                "Returns relevant knowledge chunks ranked by similarity."
            ),
            args_schema=SearchKnowledgeInput
        ),
        StructuredTool.from_function(
            func=executor.add_learning_entry,
            name="add_learning_entry",
            description=(
                "Create a new learning log entry. "
                "Use this when the user shares something they learned. "
                "Requires a title and content, optionally link to a roadmap item."
            ),
            args_schema=AddLearningEntryInput
        ),
        StructuredTool.from_function(
            func=executor.get_progress_stats,
            name="get_progress_stats",
            description=(
                "Get portfolio progress statistics and metrics. "
                "Use this to understand overall learning progress, completion rates, "
                "and knowledge base statistics. Returns comprehensive progress data."
            )
        ),
    ]

    logger.info(f"Created {len(tools)} LangChain tools from MCP server")
    return tools
