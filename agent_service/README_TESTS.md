# Agent Service Testing Guide

## Test Files Created

✅ **Test Infrastructure Complete:**
- `tests/conftest.py` - Pytest configuration and fixtures
- `tests/test_api.py` - FastAPI endpoint tests (10+ tests)
- `tests/test_mcp_tools.py` - MCP tool integration tests (15+ tests)
- `pytest.ini` - Pytest configuration with asyncio support

## Running Tests

### Option 1: Docker (Recommended for CI/CD)

**First, rebuild the agent service image:**
```bash
docker-compose build agent
docker-compose up -d agent
```

**Run all tests:**
```bash
docker-compose exec agent pytest tests/ -v
```

**Run specific test files:**
```bash
docker-compose exec agent pytest tests/test_api.py -v
docker-compose exec agent pytest tests/test_mcp_tools.py -v
```

**Run with coverage:**
```bash
docker-compose exec agent pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Option 2: Local Development

**Install dependencies:**
```bash
cd agent_service
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock httpx
```

**Run tests:**
```bash
pytest tests/ -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=. --cov-report=html
```

## Test Coverage

### API Tests (`test_api.py`)
- ✅ GET /health (health check)
- ✅ POST /api/chat (message validation)
- ✅ POST /api/chat (conversation flow with mocking)
- ✅ GET /api/tools (list available MCP tools)

### MCP Tool Tests (`test_mcp_tools.py`)
- ✅ get_roadmap() - Fetch roadmap structure
- ✅ get_learning_entries() - Fetch learning log with filters
- ✅ search_knowledge() - Semantic search with RAG
- ✅ add_learning_entry() - Create new entries
- ✅ get_progress_stats() - Portfolio statistics
- ✅ Error handling (timeouts, 500 errors, validation)

## Test Fixtures Available

Defined in `tests/conftest.py`:
- `test_client` - FastAPI TestClient
- `mock_backend_url` - Backend API URL for mocking
- `sample_chat_request` - Example chat message
- `sample_roadmap_data` - Mock roadmap JSON
- `sample_learning_entries` - Mock learning entries
- `sample_progress_stats` - Mock progress statistics
- `sample_search_results` - Mock RAG search results

## Mocking Strategy

Tests use `unittest.mock.patch` to mock:
- HTTP requests to backend API (`httpx.get`, `httpx.post`)
- Agent chat responses
- Redis connections (when needed)

This allows tests to run without:
- Running backend server
- API keys (GROQ_API_KEY, COHERE_API_KEY)
- Redis server

## CI/CD Integration

Tests can be added to GitHub Actions workflow:
```yaml
agent-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Install dependencies
      run: |
        cd agent_service
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-mock
    - name: Run tests
      run: |
        cd agent_service
        pytest tests/ -v --cov=. --cov-report=xml
```

## Test Execution Time

Current tests run in < 3 seconds (fast unit tests with mocking, no real API calls).

## Integration Testing Notes

For full integration tests (without mocking):
1. Start backend: `docker-compose up -d backend`
2. Start Redis: `docker-compose up -d redis`
3. Set environment variables:
   ```bash
   export BACKEND_URL=http://localhost:8000
   export REDIS_URL=redis://localhost:6379
   export GROQ_API_KEY=your_key_here
   ```
4. Run tests: `pytest tests/ --integration`

## Next Steps

1. ✅ Agent service tests created (25+ tests)
2. 🔲 Frontend tests (TODO)
3. 🔲 E2E tests with Playwright (TODO)
4. 🔲 Add integration tests to CI/CD pipeline
