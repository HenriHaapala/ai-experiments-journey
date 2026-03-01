# API Contracts & Internal Communication

This document outlines the REST API endpoints exposed by the Django backend and the internal communication paths between the Next.js frontend, the Django backend, and the FastAPI LangChain agent.

---

## 🌐 Public Endpoints (Django REST Framework)
These endpoints are exposed by the Django Backend (typically on port `8000`) and are consumed directly by the Next.js frontend.

### 1. Roadmap & Learning
*   `GET /api/roadmap/sections/`
    *   **Returns:** A list of all top-level roadmap sections, pre-fetching their associated items.
*   `GET /api/roadmap/progress/`
    *   **Returns:** High-level statistics used for the frontend progress bars (total items, completion percentage, knowledge base chunk counts).
*   `GET /api/roadmap/learning-entries/`
    *   **Params:** `?roadmap_item=<id>`, `?limit=<int>`
    *   **Returns:** A list of learning entries, optionally filtered by a specific roadmap item.
*   `POST /api/roadmap/learning-entries/`
    *   **Body:** Learning entry data (title, content, roadmap_item_id).
    *   **Returns:** The created entry.
*   `GET /api/learning/public/`
    *   **Returns:** All learning entries marked as `is_public=True`.

### 2. AI Chat Interaction
*   `POST /api/ai/chat/`
    *   **Description:** The primary endpoint for user interaction with the AI.
    *   **Body:** `{ "question": "user input string" }`
    *   **Flow:**
        1.  **Security Check:** Immediately proxies the `question` to the FastAPI agent (`http://agent:8001/api/validate`) for guardrail checks. If unsafe, returns a 200 OK with a blocked message.
        2.  **Vector Search:** If safe, embeds the question using Cohere and searches `pgvector` for related `KnowledgeChunk` records. Includes an SQL keyword fallback if the vector search returns low confidence.
        3.  **Generation:** Sends the retrieved context and question to Groq (Llama-3) to generate an answer.
    *   **Returns:** 
        ```json
        {
            "answer": "string",
            "question": "string",
            "confidence": float,
            "retrieval_debug": object,
            "follow_up_questions": [ "string", "string", "string" ]
        }
        ```

### 3. Utility & RAG
*   `POST /api/rag/search/`
    *   **Body:** `{ "query": "search term", "top_k": 5 }`
    *   **Returns:** The raw `pgvector` chunks matching the query. Used internally or for debugging.
*   `POST /api/security/audit/`
    *   **Returns:** Endpoint to log security events (like jailbreaks detected by the agent).

---

## 🤖 Internal Agent API (FastAPI)
These endpoints are exposed by the FastAPI agent (typically on port `8001`). They are **not** exposed directly to the public web; they are only called internally by the Django backend or via internal Docker networking.

### 1. Guardrails & Validation
*   `POST /api/validate` *(Internal)*
    *   **Called By:** Django `AIChatView`
    *   **Body:** `{ "text": "user input" }`
    *   **Returns:** `{ "is_safe": boolean, "reason": "string" }`
    *   **Purpose:** Runs NeMo guardrails or predefined regex/heuristics to block prompt injection before any heavy LLM processing occurs.

### 2. Tools & Execution (MCP)
*   *Note: Detailed MCP connections are defined in `agent_service/mcp_tools.py` and `backend/mcp_server/urls.py`.* The LangChain agent can execute remote procedure calls back into the Django backend to fetch live data (like reading a specific database item) during its reasoning loop.
