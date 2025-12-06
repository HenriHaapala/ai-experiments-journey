# MCP Server - Portfolio Management Tools

This MCP (Model Context Protocol) server exposes 5 tools for managing and querying the AI portfolio.

## Available Tools

### 1. get_roadmap
Get the complete AI Career Roadmap with all sections and items.

**Input:** None
**Output:**
```json
{
  "success": true,
  "roadmap": [
    {
      "id": 1,
      "title": "Section Title",
      "description": "Section description",
      "order": 1,
      "items": [
        {
          "id": 1,
          "title": "Item Title",
          "description": "Item description",
          "order": 1,
          "is_active": true
        }
      ]
    }
  ],
  "total_sections": 10,
  "total_items": 26
}
```

### 2. get_learning_entries
Get learning log entries, optionally filtered by roadmap item.

**Input:**
- `roadmap_item_id` (optional): Filter by roadmap item ID
- `limit` (optional, default=10): Max number of entries to return

**Output:**
```json
{
  "success": true,
  "entries": [
    {
      "id": 1,
      "title": "Entry Title",
      "content": "What I learned...",
      "roadmap_item": "Roadmap Item Title",
      "is_public": true,
      "created_at": "2025-12-06T12:00:00Z"
    }
  ],
  "count": 2
}
```

### 3. search_knowledge
Semantic search across all portfolio knowledge using RAG.

**Input:**
- `query` (required): Search query
- `top_k` (optional, default=5): Number of results

**Output:**
```json
{
  "success": true,
  "results": [
    {
      "id": 1,
      "title": "Knowledge Chunk Title",
      "content": "Content snippet...",
      "source_type": "learning_entry",
      "section_title": "Section",
      "similarity": 0.85
    }
  ],
  "query": "your search query",
  "count": 5
}
```

### 4. add_learning_entry
Create a new learning log entry.

**Input:**
- `title` (required): Title of the learning entry
- `content` (required): Content/description of what was learned
- `roadmap_item_id` (optional): Associate with a roadmap item
- `is_public` (optional, default=true): Whether the entry is public

**Output:**
```json
{
  "success": true,
  "entry": {
    "id": 3,
    "title": "New Entry",
    "content": "What I learned...",
    "created_at": "2025-12-06T12:00:00Z"
  }
}
```

### 5. get_progress_stats
Get portfolio progress statistics and metrics.

**Input:** None
**Output:**
```json
{
  "success": true,
  "stats": {
    "roadmap": {
      "total_sections": 10,
      "total_items": 26,
      "active_items": 26,
      "items_with_entries": 0,
      "completion_percentage": 0.0
    },
    "learning": {
      "total_entries": 2,
      "public_entries": 2,
      "private_entries": 0
    },
    "knowledge_base": {
      "total_chunks": 41,
      "by_source": {
        "learning_entry": 2,
        "roadmap_item": 26,
        "site_content": 0,
        "document": 13
      }
    }
  }
}
```

## Usage

### Direct Python Usage
```python
from mcp_server.handlers import (
    handle_get_roadmap,
    handle_get_learning_entries,
    handle_search_knowledge,
    handle_add_learning_entry,
    handle_get_progress_stats
)

# Get roadmap
result = handle_get_roadmap({})

# Search knowledge
result = handle_search_knowledge({"query": "What is RAG?", "top_k": 5})

# Add learning entry
result = handle_add_learning_entry({
    "title": "Learned about embeddings",
    "content": "Vector embeddings represent text as numbers..."
})

# Get stats
result = handle_get_progress_stats({})
```

### MCP Server Mode
```bash
python -m mcp_server.server
```

This starts the MCP server in stdio mode for agent integration.

## Architecture

- **server.py** - MCP protocol server implementation
- **tools.py** - Tool definitions (schemas)
- **handlers.py** - Tool implementations using Django ORM
- **__init__.py** - Package initialization

## Dependencies

- `mcp>=0.9.0` - Model Context Protocol SDK
- Django ORM for database access
- Cohere for embeddings (search_knowledge tool)
