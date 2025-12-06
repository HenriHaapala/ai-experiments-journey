"""
MCP Tools Definition
Defines the 5 portfolio management tools exposed via MCP protocol
"""

TOOLS = [
    {
        "name": "get_roadmap",
        "description": "Get the AI Career Roadmap with all sections and items",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_learning_entries",
        "description": "Get learning log entries, optionally filtered by roadmap item",
        "inputSchema": {
            "type": "object",
            "properties": {
                "roadmap_item_id": {
                    "type": "integer",
                    "description": "Optional: filter by roadmap item ID"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of entries to return",
                    "default": 10
                }
            },
            "required": []
        }
    },
    {
        "name": "search_knowledge",
        "description": "Semantic search across all portfolio knowledge using RAG",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "add_learning_entry",
        "description": "Create a new learning log entry",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the learning entry"
                },
                "content": {
                    "type": "string",
                    "description": "Content/description of what was learned"
                },
                "roadmap_item_id": {
                    "type": "integer",
                    "description": "Optional: associate with a roadmap item"
                },
                "is_public": {
                    "type": "boolean",
                    "description": "Whether the entry is public",
                    "default": True
                }
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "get_progress_stats",
        "description": "Get portfolio progress statistics and metrics",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]
