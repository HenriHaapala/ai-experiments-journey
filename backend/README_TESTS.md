# Backend Testing Guide

## Test Files Created

✅ **Test Infrastructure Complete:**
- `tests/conftest.py` - Pytest configuration and fixtures
- `tests/test_models.py` - Database model tests (16 tests)
- `tests/test_api.py` - REST API endpoint tests (20+ tests)
- `pytest.ini` - Pytest configuration

## Running Tests

### Option 1: Docker (Recommended for CI/CD)

**First, rebuild the Docker image to include test dependencies:**
```bash
docker-compose build backend
docker-compose up -d backend
```

**Run all tests:**
```bash
docker-compose exec backend python -m pytest tests/ -v
```

**Run specific test files:**
```bash
docker-compose exec backend python -m pytest tests/test_models.py -v
docker-compose exec backend python -m pytest tests/test_api.py -v
```

**Run with coverage:**
```bash
docker-compose exec backend python -m pytest tests/ --cov=portfolio --cov-report=html --cov-report=term
```

### Option 2: Local Development (Virtual Environment)

**Activate virtual environment and install dependencies:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run tests:**
```bash
pytest tests/ -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=portfolio --cov-report=html
```

## Test Coverage

### Model Tests (`test_models.py`)
- ✅ RoadmapSection creation and ordering
- ✅ RoadmapItem relationships and cascade delete
- ✅ LearningEntry with/without roadmap items
- ✅ Media attachments with all media types
- ✅ KnowledgeChunk vector storage (RAG)
- ✅ SiteContent unique slugs

### API Tests (`test_api.py`)
- ✅ GET /api/roadmap/sections/ (with prefetch)
- ✅ GET /api/learning/public/ (public entries only)
- ✅ POST /api/roadmap/learning-entries/ (create entry)
- ✅ GET /api/roadmap/learning-entries/ (list, filter, limit)
- ✅ GET /api/roadmap/progress/ (statistics)
- ✅ POST /api/rag/search/ (input validation)
- ✅ POST /api/ai/chat/ (input validation)
- ✅ GET /api/health/ (health check)

## Test Fixtures Available

Defined in `tests/conftest.py`:
- `api_client` - Django REST framework test client
- `roadmap_section` - Sample roadmap section
- `roadmap_item` - Sample roadmap item
- `learning_entry` - Public learning entry
- `learning_entry_private` - Private learning entry
- `media_attachment` - Sample media file
- `knowledge_chunk` - Sample RAG chunk with vector
- `site_content` - Sample site page
- `authenticated_user` - Test user

## CI/CD Integration

Tests are automatically run by the pre-push hook (see `lefthook.yml`):
```yaml
pre-push:
  commands:
    test-backend:
      run: cd backend && pytest --maxfail=1 --disable-warnings -q
```

## Notes for Integration Tests

Some tests require API keys to run fully:
- `test_rag_search_with_query` - Requires COHERE_API_KEY
- `test_ai_chat_with_question` - Requires COHERE_API_KEY + GROQ_API_KEY

For CI/CD, these should be mocked or use test API keys.

## Next Steps

1. ✅ Backend tests created (36+ tests)
2. 🔲 Agent service tests (TODO)
3. 🔲 Frontend tests (TODO)
4. 🔲 E2E tests with Playwright (TODO)

## Test Execution Time

Current tests run in < 5 seconds (fast unit tests, no external API calls).
