# CLAUDE.md

## Project Overview

This is an AI-powered portfolio application that tracks learning journey progress through a roadmap system with RAG (Retrieval-Augmented Generation) capabilities. The project consists of a Django REST backend with PostgreSQL + pgvector for semantic search, and a Next.js frontend.

## Architecture

### Backend (`/backend`)
- **Framework**: Django + Django REST Framework
- **Database**: PostgreSQL with pgvector extension
- **Vector Embeddings**: Cohere embed-english-v3.0 (1024 dimensions)
- **Python Version**: Python 3.x (managed via venv)

### Frontend (`/frontend`)
- **Framework**: Next.js 16.0.5 with React 19.2.0
- **Styling**: Tailwind CSS 4 (primary styling approach)
- **Language**: TypeScript 5
- **Component Architecture**: Modular, reusable components with clear separation of concerns

### Deployment
- **Infrastructure**: Fully Dockerized with docker-compose
- **Containerization**: ✅ Complete - All services containerized
- **Services** (6 containers):
  - PostgreSQL 16 + pgvector (port 5432)
  - Django Backend API (port 8000)
  - Next.js Frontend (port 3000)
  - Adminer DB Admin (port 8080)
  - Redis (port 6379) - Phase 3: Caching & task queue
  - Agent Service (port 8001) - Phase 3: LangChain agent
- **Design Principle**: Cloud-native and production-ready
  - Environment variables for all configuration
  - No hardcoded paths or localhost references
  - Horizontal scaling ready
  - Separated concerns with health checks
  - Microservices architecture with service-to-service communication

#### Cloud Deployment: Oracle Cloud Infrastructure (OCI)

**Instance Configuration:**
- **Region**: Frankfurt (eu-frankfurt-1)
- **Shape**: VM.Standard.A1.Flex (4 OCPUs, 24 GB RAM) - **FREE TIER**
- **Operating System**: Ubuntu 22.04 LTS
- **VCN**: aiportfolio-vcn (Virtual Cloud Network)
- **Subnet**: public subnet-aiportfolio-vcn (10.0.0.0/24)
- **Public IP**: See `.env.production` (local file, not committed)
- **Domain**: wwwportfolio.henrihaapala.com
- **Cost**: €0/month (Oracle Always Free tier)

**HTTPS/SSL Configuration:**
- **Reverse Proxy**: nginx (installed on instance, not in Docker)
- **SSL Certificates**: Let's Encrypt (free, auto-renewal)
- **Setup**: See [HTTPS_SETUP.md](HTTPS_SETUP.md) for detailed instructions
- **URLs**:
  - Frontend: https://wwwportfolio.henrihaapala.com
  - Backend API: https://wwwportfolio.henrihaapala.com/api/
  - Agent Service: https://wwwportfolio.henrihaapala.com/agent/
  - Adminer: https://wwwportfolio.henrihaapala.com/adminer/

**nginx Architecture** (Production):
```
Internet (HTTPS:443)
    ↓
nginx (SSL Termination + Reverse Proxy)
    ↓
Docker Containers (HTTP:3000, 8000, 8001, 8080)
    ↓
PostgreSQL (Internal network only)
```

**Local Development** (No nginx needed):
- Access services directly: http://localhost:3000, http://localhost:8000
- No SSL required for local development
- nginx only runs in production (Oracle Cloud instance)

**Benefits of Free Tier:**
- 💰 **€0/month** - Truly free forever (not a trial)
- 💪 **4 OCPUs + 24 GB RAM** - More than sufficient for portfolio app
- 🚀 **Always-on** - No need to stop/start instance
- 📈 **Scalable** - Can handle significant traffic
- 🎯 **Production-grade** - ARM architecture (Ampere Altra)

## Key Features

1. **Learning Roadmap System**
   - Hierarchical structure: RoadmapSection → RoadmapItem → LearningEntry
   - Track progress through ordered items
   - Public/private learning entries

2. **RAG (Retrieval-Augmented Generation)**
   - Document upload and processing (PDF support via pypdf)
   - Vector embeddings for semantic search
   - Knowledge chunking for efficient retrieval
   - Confidence scoring and hallucination reduction
   - Smart retrieval system

3. **MCP Server + Intelligent Agents** (Phase 3)
   - Model Context Protocol server exposing 5 portfolio management tools
   - LangChain-powered agent with natural language interface
   - Autonomous task orchestration and multi-tool chaining
   - GitHub webhook automation for learning entry creation
   - Scheduled tasks and smart reminders
   - Groq-powered reasoning and decision-making

4. **Content Management**
   - Site content with slug-based routing
   - Media attachments (images, videos, links, files)
   - Markdown content support

5. **Automated CI/CD Pipeline** (December 2025)
   - GitHub Actions automated testing and deployment
   - Push to main → Auto-test → Auto-deploy (10 minutes)
   - 5-job CI pipeline: backend tests, frontend tests, security scans, Docker builds, code quality
   - Zero-downtime deployment to Oracle Cloud production
   - Automatic database backups before each deployment
   - Health checks and automatic rollback on failure
   - See [CI_CD_SETUP.md](CI_CD_SETUP.md) for setup guide

## Database Schema

### Core Models

- **RoadmapSection**: Top-level categories for learning paths
- **RoadmapItem**: Individual topics within sections
- **LearningEntry**: Detailed notes/content for each item
- **Media**: Associated media files for learning entries
- **Embedding**: Vector embeddings for learning entries (legacy)
- **KnowledgeChunk**: Unified vector storage for all content types
  - Supports: learning_entry, roadmap_item, site_content, document
  - Contains title, content, section metadata, and 1024-dim vector
- **DocumentUpload**: RAG document ingestion trigger
- **SiteContent**: General site pages

### Vector Search
The application uses pgvector for semantic similarity search across learning content, enabling AI-powered content retrieval.

## Development Setup

### Docker (Recommended - Production Ready)
```bash
# Copy environment template
cp .env.example .env
# Edit .env with your API keys and secrets

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Running Tests (Pre-Commit Validation)
```bash
# Run full test suite before committing
npm run test:all

# Run specific test suites
npm run test:backend    # Django unit + integration tests
npm run test:frontend   # Jest + React Testing Library
npm run test:agent      # Agent service tests
npm run test:e2e        # Playwright end-to-end tests
npm run test:security   # Security scanning (SAST)

# Pre-commit hook (automatic)
# Runs linting, type checking, and fast tests
git commit -m "message"  # Automatically triggers pre-commit checks
```

**Services available at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/health/
- Database Admin (Adminer): http://localhost:8080
- PostgreSQL: localhost:5432

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed setup instructions.

### Local Development (Alternative)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Current Status: Phase 3 - Intelligent Agents & Automation (~80% Complete)

### Overview
Transform the MCP server from an internal tool into an intelligent, autonomous system with external access, LangChain-powered agents, and automated workflows.

### Architecture

```
External World (GitHub, Claude Desktop, etc.)
    ↓
[SSE HTTP Endpoint] ← Django Backend (port 8000)
    ↓
[MCP Server] (5 tools: get_roadmap, search_knowledge, etc.)
    ↓
[LangChain Agent Service] (separate Docker container)
    ├── Agent Brain (Groq API - llama-3.3-70b-versatile)
    ├── MCP Tool Integration
    ├── Conversation Memory
    └── Task Orchestration
    ↓
[Automation Workers]
    ├── GitHub Webhook Receiver
    ├── Scheduled Tasks (progress reports, trend monitoring)
    └── Background Jobs
    ↓
Django ORM → PostgreSQL + pgvector
```

### Phase 3 Components

#### 1. External Access via SSE Transport
**Goal**: Expose MCP server to external clients (Claude Desktop, custom agents)

**Implementation:**
- Add HTTP/SSE endpoint to Django backend (`/api/mcp/sse`)
- Server-Sent Events for streaming tool responses
- CORS configuration for web-based clients
- API key authentication for security
- Compatible with MCP client libraries

**Why SSE?**
- Simple HTTP-based protocol (firewall-friendly)
- Built-in reconnection handling
- Works with standard web infrastructure
- No WebSocket complexity needed

**Files to create:**
- `backend/mcp_server/transports.py` - SSE transport implementation
- `backend/mcp_server/urls.py` - Django URL routing
- `backend/mcp_server/middleware.py` - Authentication middleware

#### 2. LangChain Agent Integration (Separate Docker Service)
**Goal**: Intelligent agent that can use MCP tools autonomously

**Agent Capabilities:**
- **Natural Language Interface**: Ask questions in plain English
- **Multi-Tool Orchestration**: Chain multiple MCP tools together
- **Context-Aware**: Maintains conversation history and learning context
- **Reasoning**: Uses Groq's llama-3.3-70b-versatile for decision-making
- **Proactive Suggestions**: "You haven't logged learning for 3 days - want help?"

**Example Use Cases:**

1. **Intelligent Learning Logging**
   - User: "I spent today learning about transformer attention mechanisms"
   - Agent: Searches knowledge base → Finds "Neural Networks" roadmap item → Creates detailed learning entry with context from existing knowledge

2. **Progress Tracking & Planning**
   - User: "What should I learn next?"
   - Agent: Gets roadmap → Analyzes progress → Searches related knowledge → Recommends next topic with reasoning

3. **Knowledge Synthesis**
   - User: "Summarize everything I've learned about machine learning so far"
   - Agent: Searches all ML-related entries → Synthesizes into coherent summary → Identifies knowledge gaps

4. **Smart Query Answering**
   - User: "Have I learned about backpropagation yet?"
   - Agent: Semantic search → Finds related entries → Provides answer with references

5. **Roadmap Optimization**
   - User: "I'm interested in computer vision now"
   - Agent: Analyzes roadmap → Suggests reordering items → Explains prerequisite knowledge

**Implementation:**
- Separate Docker service (`aiportfolio-agent`)
- LangChain framework with custom MCP tool integration
- Groq API for LLM inference (free tier, fast)
- Redis for conversation memory/caching
- RESTful API for frontend integration

**Files to create:**
- `agent_service/Dockerfile` - Agent service container
- `agent_service/agent.py` - Main LangChain agent
- `agent_service/mcp_tools.py` - MCP tool wrappers for LangChain
- `agent_service/prompts.py` - System prompts and templates
- `agent_service/memory.py` - Conversation history management
- `agent_service/api.py` - FastAPI server for agent endpoints

#### 3. GitHub Webhook Automation
**Goal**: Automatically create learning entries from GitHub activity

**Automation Flow:**
1. Push code to GitHub repository
2. GitHub sends webhook to `/api/automation/github-webhook`
3. Parser analyzes commit messages, files changed, PR descriptions
4. Agent decides if it's learning-worthy
5. Creates learning entry with appropriate roadmap item linkage
6. Optionally: Generate embeddings from code comments/README changes

**Smart Features:**
- **Technology Detection**: Parse `requirements.txt`, `package.json` changes to detect new tools learned
- **Commit Message Analysis**: Extract learning insights from commit messages (e.g., "Learned how to implement OAuth2")
- **PR Description Mining**: Convert PR descriptions into structured learning entries
- **Auto-Tagging**: Automatically tag entries with technologies, concepts
- **Duplicate Prevention**: Check existing knowledge to avoid redundant entries

**Example Scenarios:**

1. **New Project Setup**
   - Commit: "Initial Django setup with PostgreSQL and pgvector"
   - → Creates entry: "Set up Django project with vector database support"
   - → Links to "Backend Development" roadmap item
   - → Tags: Django, PostgreSQL, pgvector

2. **Feature Implementation**
   - PR: "Implemented RAG semantic search with Cohere embeddings"
   - → Creates entry with PR description as content
   - → Links to "RAG & Vector Search" roadmap item
   - → Generates embedding for semantic search

3. **Bug Fix Learning**
   - Commit: "Fixed N+1 query issue using select_related"
   - → Creates entry: "Learned about Django ORM optimization"
   - → Tags: Django, Performance, Database

**Implementation:**
- Django endpoint: `/api/automation/github-webhook`
- Webhook signature verification (HMAC)
- Background task queue for processing (APScheduler)
- Integration with LangChain agent for intelligent parsing

**Files to create:**
- `backend/automation/github_webhook.py` - Webhook receiver
- `backend/automation/parsers.py` - Commit/PR parsing logic
- `backend/automation/tasks.py` - Background task definitions

#### 4. Additional Automation Ideas

**Scheduled Progress Reports:**
- Daily/weekly summary emails: "This week you learned about X, Y, Z"
- Progress visualization: "You're 60% through the Neural Networks section"
- Streak tracking: "7-day learning streak!"

**Trending Topics Monitor:**
- Scrape AI news sources (HackerNews, ArXiv, Papers with Code)
- Suggest new roadmap items based on trending technologies
- Alert when topics in your roadmap become trending

**Document Upload Automation:**
- Watch a designated folder for PDFs
- Automatically ingest and chunk documents
- Notify when new knowledge is indexed
- Suggest which roadmap items the document relates to

**Smart Reminders:**
- "You marked 'Reinforcement Learning' as active but haven't logged progress in 5 days"
- "Your last learning entry was about CNNs - ready to move to RNNs?"

**Learning Insights:**
- Analyze learning velocity: "You learn 3 new topics per week on average"
- Identify knowledge gaps: "You know about models but haven't studied deployment"
- Suggest optimal learning paths based on dependencies

#### 5. Updated Docker Architecture

**New Services:**
- `aiportfolio-agent` (port 8001) - LangChain agent service
- `aiportfolio-redis` (port 6379) - Caching and task queue

**Updated docker-compose.yml:**
```yaml
services:
  postgres: [existing]
  backend: [existing]
  frontend: [existing]
  adminer: [existing]

  redis:
    image: redis:7-alpine
    container_name: aiportfolio-redis
    restart: unless-stopped
    ports:
      - "6379:6379"

  agent:
    build: ./agent_service
    container_name: aiportfolio-agent
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - BACKEND_URL=http://backend:8000
      - REDIS_URL=redis://redis:6379
    depends_on:
      - backend
      - redis
```

### Implementation Status

**✅ Step 1: SSE Transport Layer** (COMPLETE - Dec 8, 2025)
- ✅ Created `backend/mcp_server/transports.py` with SSE implementation
- ✅ Added Django URLs for `/api/mcp/sse` endpoint
- ✅ Implemented API key authentication middleware
- ✅ Tested with curl/HTTP clients - all 5 tools working

**✅ Step 2: Agent Service Setup** (COMPLETE - Dec 6, 2025)
- ✅ Created `agent_service/` directory structure
- ✅ Wrote Dockerfile for agent service
- ✅ Set up FastAPI server for agent API
- ✅ Added LangChain dependencies

**✅ Step 3: MCP Tool Integration in Agent** (COMPLETE - Dec 6, 2025)
- ✅ Created LangChain tool wrappers for 5 MCP tools
- ✅ Implemented agent with Groq LLM (llama-3.3-70b-versatile)
- ✅ Added conversation memory with Redis
- ✅ Tested agent with example queries (see `agent_service/TEST_RESULTS.md`)

**✅ Step 4: Pre-commit Hooks & CI/CD** (COMPLETE - Dec 7-8, 2025)
- ✅ Installed Lefthook 1.13.6, Biome 1.9.4, Gitleaks 8.30.0
- ✅ Created `lefthook.yml` configuration
- ✅ Verified all tools working (see `PRECOMMIT_VERIFICATION.md`)
- ✅ Created GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`)

**❌ Step 5: GitHub Webhook Automation** (NOT STARTED)
- [ ] Create webhook receiver endpoint
- [ ] Implement commit/PR parsing logic
- [ ] Integrate with agent for intelligent entry creation
- [ ] Test with real GitHub webhooks

**❌ Step 6: Additional Automations** (NOT STARTED)
- [ ] Scheduled progress reports
- [ ] Trending topics monitor
- [ ] Document upload automation
- [ ] Smart reminders

**📋 See [REMAINING_PHASE3_TASKS.md](REMAINING_PHASE3_TASKS.md) for detailed implementation guide**

### Success Criteria

- ✅ External clients can connect to MCP server via SSE
- ✅ Agent can answer natural language queries using MCP tools
- ❌ GitHub commits automatically create learning entries (NOT YET)
- ✅ Agent maintains conversation context across queries
- ✅ All services run in Docker with proper networking
- ✅ Complete documentation with example use cases

### Technology Stack (Phase 3 Additions)

- **LangChain**: Agent orchestration framework
- **Groq API**: LLM inference (llama-3.3-70b-versatile) - FREE tier
- **FastAPI**: Agent service HTTP API
- **Redis**: Caching and conversation memory
- **APScheduler**: Background task scheduling
- **MCP SDK**: Model Context Protocol client/server

### Why This Matters

**For Portfolio Demonstration:**
- Shows advanced AI agent development skills
- Demonstrates understanding of MCP protocol
- Production-ready microservices architecture
- Real-world automation and workflow engineering

**For Personal Use:**
- Automatic learning journal from GitHub activity
- Intelligent learning path recommendations
- Semantic search across all knowledge
- Progress tracking and motivation

---

## Recent Development

### Phase 3 Progress: 80% Complete (Dec 6-8, 2025)

**December 9, 2025:**
- ✅ **Automated CI/CD Pipeline** - Full GitHub Actions deployment to Oracle Cloud
- ✅ **Production Deployment** - Live at https://wwwportfolio.henrihaapala.com
- ✅ **Zero-Touch Deployment** - Push to main → Auto-test → Auto-deploy (10 min)
- 📋 See [CI_CD_SETUP.md](CI_CD_SETUP.md) for complete setup guide

**December 8, 2025:**
- ✅ **MCP SSE Transport** - HTTP/SSE access to MCP server via `POST /api/mcp/sse/`
- ✅ **API Key Authentication** - Secure external access with middleware
- ✅ **GitHub Actions CI/CD** - 5-job pipeline (tests, security, Docker builds)
- ✅ **Vector Search Fix** - Corrected pgvector CosineDistance implementation

**December 7, 2025:**
- ✅ **Pre-commit Hooks** - Lefthook with Gitleaks, Biome, Ruff, Semgrep
- ✅ **Security Tools** - All installed and verified (see `PRECOMMIT_VERIFICATION.md`)
- ✅ **Performance** - <3 second pre-commit checks vs 10-30s traditional

**December 6, 2025:**
- ✅ **LangChain Agent** - Full implementation in `agent_service/`
- ✅ **Groq Integration** - llama-3.3-70b-versatile for reasoning
- ✅ **Redis Memory** - Conversation history tracking
- ✅ **Docker Service** - Running on port 8001 (healthy)

**📋 Remaining Tasks:** See [REMAINING_PHASE3_TASKS.md](REMAINING_PHASE3_TASKS.md) for GitHub webhooks and additional automations

### Phase 2 Complete: MCP Server (Dec 6, 2025)
- **MCP Server Built** - Model Context Protocol server exposing 5 portfolio management tools
- **Tool Integration** - get_roadmap, get_learning_entries, search_knowledge, add_learning_entry, get_progress_stats
- **Django Integration** - MCP handlers using Django ORM for database access
- **RAG-Powered Search** - Semantic search across 41 knowledge chunks with Cohere embeddings
- **Documentation** - Complete API documentation in [backend/mcp_server/README.md](backend/mcp_server/README.md)

### Phase 1 Complete: Full Stack Dockerization (Dec 5, 2025)
- **Dockerization Complete** - Full stack containerized with docker-compose (6 services)
- **Database Migration** - Successfully migrated to Docker postgres with pgvector
- **Frontend Build Fix** - Next.js environment variables properly baked at build time
- **Production Ready** - All services running with health checks and proper dependencies

### Earlier Milestones
- **Tailwind CSS Refactoring** - Converted all styles to Tailwind utilities
- Hallucination reduction and confidence scoring implementation
- Smart retrieve functionality for better RAG performance
- Document upload system for RAG knowledge base

## Project Structure

```
ai-portfolio/
├── backend/
│   ├── Dockerfile           # Backend Docker configuration
│   ├── .dockerignore        # Docker build exclusions
│   ├── mcp_server/          # MCP Server (Phase 2)
│   │   ├── server.py        # MCP protocol server
│   │   ├── tools.py         # Tool definitions
│   │   ├── handlers.py      # Tool implementations
│   │   ├── transports.py    # SSE transport (Phase 3)
│   │   ├── urls.py          # Django URL routing (Phase 3)
│   │   ├── middleware.py    # Authentication (Phase 3)
│   │   └── README.md        # MCP server documentation
│   ├── automation/          # Automation workflows (Phase 3 - NOT YET CREATED)
│   │   ├── github_webhook.py # GitHub integration (TODO)
│   │   ├── parsers.py       # Commit/PR parsing (TODO)
│   │   └── tasks.py         # Background tasks (TODO)
│   ├── portfolio/
│   │   ├── models.py        # Django models (roadmap, embeddings, RAG)
│   │   └── ...
│   ├── venv/                # Python virtual environment (local dev)
│   └── requirements.txt     # Python dependencies
├── agent_service/           # LangChain Agent (Phase 3)
│   ├── Dockerfile           # Agent service container
│   ├── agent.py             # Main LangChain agent
│   ├── mcp_tools.py         # MCP tool wrappers
│   ├── prompts.py           # System prompts
│   ├── memory.py            # Conversation history
│   ├── api.py               # FastAPI server
│   └── requirements.txt     # Agent dependencies
├── frontend/
│   ├── Dockerfile           # Frontend Docker configuration
│   ├── .dockerignore        # Docker build exclusions
│   ├── app/                 # Next.js app directory
│   ├── node_modules/        # Node dependencies
│   └── package.json         # Node dependencies config
├── docker-compose.yml       # Multi-service orchestration (6 services)
├── .env.example             # Environment template (safe to commit)
├── .env                     # Actual secrets (gitignored)
├── DOCKER_SETUP.md          # Docker setup guide
├── DATABASE_MIGRATION.md    # Database migration guide
└── CLAUDE.md                # This file - Project documentation
```

## Working with this Project

### Common Tasks

1. **Adding New Learning Content**
   - Create entries through Django admin or API
   - Embeddings are automatically generated for RAG

2. **Querying Knowledge Base**
   - Use KnowledgeChunk model for semantic search
   - Supports multiple source types with unified vector storage

3. **Uploading Documents**
   - Use DocumentUpload model to trigger RAG ingestion
   - PDF documents are processed and chunked automatically

### Key Files to Know

- [backend/portfolio/models.py](backend/portfolio/models.py) - Core data models
- [frontend/package.json](frontend/package.json) - Frontend dependencies
- [backend/requirements.txt](backend/requirements.txt) - Backend dependencies

## Technology Stack

**Backend:**
- Django & Django REST Framework
- PostgreSQL with pgvector
- Cohere embeddings API
- pypdf for document processing

**Frontend:**
- Next.js 16 (App Router)
- React 19
- TypeScript 5
- Tailwind CSS 4

**Agent Service:**
- LangChain with Groq LLM
- FastAPI
- Redis for caching & memory
- Python 3.11

## Testing & CI/CD Strategy

### Overview
Production-grade testing infrastructure with automated quality gates and continuous integration. Demonstrates industry best practices for modern web applications.

### Testing Pyramid

```
         /\
        /E2E\          <- End-to-End Tests (Playwright)
       /------\
      /Integration\    <- API Integration Tests
     /------------\
    /  Unit Tests  \   <- Component/Function Tests
   /----------------\
```

### Test Suites

#### 1. Backend Tests (pytest + Django Test Framework)
**Location**: `backend/tests/`

**Coverage**:
- **Unit Tests**: Models, serializers, utilities (>80% coverage target)
- **Integration Tests**: API endpoints, database operations
- **RAG Tests**: Vector search, embedding generation, document processing
- **MCP Tests**: Tool execution, handler logic

**Tools**:
- `pytest` - Test framework with fixtures and parametrization
- `pytest-django` - Django integration
- `pytest-cov` - Code coverage reporting
- `factory_boy` - Test data factories
- `faker` - Realistic fake data generation

**Example**:
```bash
# Run all backend tests with coverage
cd backend
pytest --cov=portfolio --cov-report=html --cov-report=term

# Run specific test modules
pytest tests/test_models.py -v
pytest tests/test_rag.py -k "test_semantic_search" -v

# Run only unit tests (fast)
pytest -m unit

# Run integration tests (slower)
pytest -m integration
```

**Key Test Files**:
- `tests/test_models.py` - Django model validation
- `tests/test_api.py` - REST API endpoints
- `tests/test_rag.py` - RAG system functionality
- `tests/test_mcp_tools.py` - MCP tool handlers
- `tests/factories.py` - Test data factories

#### 2. Frontend Tests (Jest + React Testing Library + Vitest)
**Location**: `frontend/__tests__/`

**Coverage**:
- **Component Tests**: UI component rendering and interactions
- **Hook Tests**: Custom React hooks
- **Utility Tests**: Helper functions
- **Integration Tests**: API client, data fetching

**Tools**:
- `Jest` - Test runner and assertion library
- `React Testing Library` - Component testing with user-centric queries
- `Vitest` - Fast unit test runner (alternative to Jest)
- `@testing-library/jest-dom` - Custom matchers for DOM assertions
- `msw` (Mock Service Worker) - API mocking

**Example**:
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch

# Run specific test file
npm test -- Navigation.test.tsx
```

**Key Test Files**:
- `__tests__/components/Navigation.test.tsx`
- `__tests__/components/RoadmapCard.test.tsx`
- `__tests__/hooks/useApi.test.ts`
- `__tests__/utils/formatters.test.ts`

#### 3. Agent Service Tests (pytest + pytest-asyncio)
**Location**: `agent_service/tests/`

**Coverage**:
- **Unit Tests**: Tool wrappers, memory management, prompts
- **Integration Tests**: LangChain agent execution, tool orchestration
- **Mock Tests**: Testing with mock backend (no external dependencies)
- **LLM Tests**: Groq API integration (with rate limiting)

**Tools**:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking capabilities
- `httpx` - HTTP client for testing

**Example**:
```bash
cd agent_service

# Run all agent tests
pytest -v

# Run with mock backend (no external API calls)
GROQ_API_KEY=mock pytest -v

# Test specific functionality
pytest tests/test_mcp_tools.py -v
pytest tests/test_memory.py -v
```

**Key Test Files**:
- `tests/test_agent.py` - LangChain agent behavior
- `tests/test_mcp_tools.py` - MCP tool integration
- `tests/test_memory.py` - Redis conversation memory
- `tests/test_api.py` - FastAPI endpoints

#### 4. End-to-End Tests (Playwright)
**Location**: `e2e/tests/`

**Coverage**:
- **User Workflows**: Complete user journeys across frontend and backend
- **Cross-browser**: Chrome, Firefox, Safari (WebKit)
- **Mobile Testing**: Responsive design validation
- **Visual Regression**: Screenshot comparison

**Tools**:
- `Playwright` - Modern E2E testing framework
- `@playwright/test` - Test runner with built-in assertions
- Parallel execution, video recording, trace viewer

**Example Scenarios**:
```typescript
// e2e/tests/learning-journey.spec.ts
test('User creates learning entry and sees it in roadmap', async ({ page }) => {
  // 1. Navigate to roadmap
  await page.goto('http://localhost:3000/roadmap');

  // 2. Create new learning entry
  await page.click('text=Add Learning Entry');
  await page.fill('#title', 'Completed React 19 course');
  await page.fill('#content', 'Learned about concurrent features');
  await page.click('button:has-text("Save")');

  // 3. Verify entry appears
  await expect(page.locator('text=Completed React 19 course')).toBeVisible();

  // 4. Verify RAG indexing (semantic search)
  await page.goto('http://localhost:3000/search');
  await page.fill('#search-input', 'concurrent features');
  await expect(page.locator('text=React 19')).toBeVisible();
});

test('Agent answers questions about progress', async ({ page }) => {
  await page.goto('http://localhost:3000/chat');
  await page.fill('#message', 'What is my learning progress?');
  await page.click('button:has-text("Send")');
  await expect(page.locator('.agent-response')).toContainText('%');
});
```

**Run E2E Tests**:
```bash
# Install browsers (first time only)
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run with UI mode (visual debugging)
npm run test:e2e:ui

# Generate test report
npx playwright show-report
```

#### 5. Security & Quality Scans

**SAST (Static Application Security Testing)**:
- `bandit` - Python security linter (backend)
- `eslint-plugin-security` - JavaScript security (frontend)
- `safety` - Python dependency vulnerability scanner
- `npm audit` - Node.js dependency scanner

**Code Quality**:
- `pylint`, `flake8`, `black` - Python linting and formatting
- `ESLint` + `Prettier` - JavaScript/TypeScript linting and formatting
- `mypy` - Python type checking
- `tsc --noEmit` - TypeScript type checking

**Example**:
```bash
# Security scans
npm run security:backend   # bandit + safety
npm run security:frontend  # npm audit + ESLint security
npm run security:all       # Full security audit

# Code quality checks
npm run lint:backend       # Python linting
npm run lint:frontend      # ESLint + Prettier
npm run type:check         # TypeScript + mypy
```

### Pre-Commit Hooks (Modern Options)

Multiple approaches available - choose based on team preference:

#### Option 1: **Biome** (2025 Recommended - Fastest)
Modern all-in-one toolchain that replaces ESLint + Prettier with 100x faster performance:

```bash
# Install Biome (Rust-based, very fast)
npm install --save-dev @biomejs/biome

# biome.json configuration
{
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  },
  "organizeImports": {
    "enabled": true
  }
}

# Pre-commit: .git/hooks/pre-commit
#!/bin/sh
npx @biomejs/biome check --apply --staged .
```

**Benefits**:
- ⚡ 100x faster than ESLint + Prettier (Rust-based)
- 🔧 Single tool for linting, formatting, import sorting
- 📦 Zero config to get started
- 🎯 Built specifically for modern JavaScript/TypeScript

#### Option 2: **Lefthook** (GitHub's Choice - Lightweight)
Used by GitHub, GitLab, and many modern projects. Faster than Husky, no npm dependencies:

```bash
# Install Lefthook (Go-based, cross-platform)
npm install --save-dev lefthook

# lefthook.yml configuration
pre-commit:
  parallel: true
  commands:
    biome:
      glob: "*.{js,ts,tsx,json}"
      run: npx @biomejs/biome check --apply --no-errors-on-unmatched --files-ignore-unknown=true {staged_files}

    python-format:
      glob: "*.py"
      run: black {staged_files}

    python-lint:
      glob: "*.py"
      run: ruff check --fix {staged_files}

    type-check:
      run: npm run type:check

    test-fast:
      run: npm run test:fast

pre-push:
  commands:
    test-all:
      run: npm run test
```

**Benefits**:
- 🚀 5-10x faster than Husky (Go-based)
- 🔄 Parallel execution built-in
- 🌍 Cross-platform (no shell scripts)
- 🎯 Used by GitHub, GitLab, Shopify

#### Option 3: **pre-commit** (Python Standard)
Python ecosystem standard for multi-language projects:

```bash
# Install pre-commit (Python-based)
pip install pre-commit

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/biomejs/biome
    rev: v1.9.4
    hooks:
      - id: biome-check
        additional_dependencies: ["@biomejs/biome"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

# Install hooks
pre-commit install
```

**Benefits**:
- 🐍 Python ecosystem standard
- 🔧 Extensive plugin ecosystem
- 📦 Language-agnostic
- ✅ Auto-updates dependencies

#### Option 4: **Husky + lint-staged** (Traditional - Still Valid)
Still widely used, especially in JavaScript-heavy projects:

```bash
# Install Husky + lint-staged
npm install --save-dev husky lint-staged

# .husky/pre-commit
npx lint-staged

# package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["biome check --apply"],
    "*.py": ["ruff check --fix", "black"],
    "*.{json,md,yml}": ["prettier --write"]
  }
}
```

**Benefits**:
- 📚 Most documented
- 🌐 Largest ecosystem
- ⚛️ React/Next.js standard

---

### Recommended Stack for This Project

**For 2025 Best Practices**:
```bash
# Frontend: Biome (replaces ESLint + Prettier)
npm install --save-dev @biomejs/biome

# Backend: Ruff (replaces flake8, black, isort - 10-100x faster)
pip install ruff

# Git Hooks: Lefthook (modern, fast, cross-platform)
npm install --save-dev lefthook

# Result: Fastest possible pre-commit checks (<1 second)
```

**Why this stack**:
- ⚡ **Biome**: Rust-based, 100x faster than ESLint
- ⚡ **Ruff**: Rust-based, 10-100x faster than flake8/black
- ⚡ **Lefthook**: Go-based, 5-10x faster than Husky
- 🎯 All tools from 2023-2025, built for modern development
- 🚀 Pre-commit checks complete in <1 second instead of 10+ seconds

### Continuous Integration (GitHub Actions)

**Workflow**: `.github/workflows/ci.yml`

Triggers on:
- Push to `main` branch
- Pull requests
- Manual workflow dispatch

**CI Pipeline**:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # Job 1: Backend Tests
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-django
      - name: Run tests with coverage
        run: |
          cd backend
          pytest --cov=portfolio --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  # Job 2: Frontend Tests
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json

  # Job 3: Agent Service Tests
  agent-tests:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd agent_service
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: |
          cd agent_service
          pytest --cov=. --cov-report=xml
        env:
          USE_MOCK_BACKEND: true
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}

  # Job 4: E2E Tests
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Docker Compose
        run: docker-compose up -d
      - name: Wait for services
        run: |
          timeout 60 sh -c 'until curl -f http://localhost:3000; do sleep 2; done'
          timeout 60 sh -c 'until curl -f http://localhost:8000/api/health/; do sleep 2; done'
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npm run test:e2e
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/

  # Job 5: Security Scans
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit (Python SAST)
        run: |
          pip install bandit
          bandit -r backend/ agent_service/ -f json -o bandit-report.json
      - name: Run Safety (Python dependencies)
        run: |
          pip install safety
          safety check --file backend/requirements.txt --json
      - name: Run npm audit
        run: |
          cd frontend
          npm audit --audit-level=moderate

  # Job 6: Build & Deploy (only on main)
  build-deploy:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests, agent-tests, e2e-tests, security]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: docker-compose build
      - name: Push to registry (optional)
        run: echo "Deploy to production"
```

### Test Coverage Goals

| Component | Target | Current | Status |
|-----------|--------|---------|--------|
| Backend (Django) | 80% | TBD | 🔴 Not Started |
| Frontend (React) | 70% | TBD | 🔴 Not Started |
| Agent Service | 75% | TBD | 🔴 Not Started |
| E2E Coverage | 5 critical paths | TBD | 🔴 Not Started |

**Note**: Testing infrastructure implementation is planned after Phase 3 completion. Modern tooling stack documented above (Biome, Ruff, Lefthook) will be implemented when setting up automated testing.

### Testing Best Practices

1. **Write Tests First** (TDD when appropriate)
   - Write failing test
   - Implement minimum code to pass
   - Refactor while keeping tests green

2. **Test Naming Convention**:
   ```python
   # Backend (pytest)
   def test_<function>_<scenario>_<expected_result>():
       """Test that <function> <scenario> returns <expected_result>"""
       pass

   # Frontend (Jest)
   describe('ComponentName', () => {
     it('should render correctly when <condition>', () => {
       // Test implementation
     });
   });
   ```

3. **AAA Pattern** (Arrange, Act, Assert):
   ```python
   def test_roadmap_item_completion():
       # Arrange: Set up test data
       item = RoadmapItemFactory(is_active=True)

       # Act: Execute the behavior
       result = item.mark_completed()

       # Assert: Verify the outcome
       assert result.is_active is False
       assert result.completed_at is not None
   ```

4. **Mock External Dependencies**:
   - API calls (Cohere, Groq)
   - Database in unit tests (use factories)
   - Time-dependent functions

5. **Continuous Coverage Improvement**:
   - Track coverage trends
   - Fail CI if coverage drops > 5%
   - Focus on critical business logic

### Performance Testing (Future)

**Load Testing** (Locust / k6):
- API endpoint response times
- Concurrent user handling
- Database query performance
- Vector search scalability

**Example** (k6):
```javascript
// k6/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp up to 50 users
    { duration: '3m', target: 50 },   // Stay at 50 users
    { duration: '1m', target: 100 },  // Ramp up to 100 users
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests < 500ms
  },
};

export default function () {
  let res = http.get('http://localhost:8000/api/roadmap/sections/');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

### Benefits for Employers

This testing infrastructure demonstrates:

✅ **Production-Ready Skills**: Industry-standard testing practices
✅ **Quality Focus**: Automated quality gates prevent regressions
✅ **CI/CD Expertise**: Complete automation pipeline
✅ **Scalability Mindset**: Performance and load testing
✅ **Security Awareness**: SAST and dependency scanning
✅ **Maintainability**: High test coverage = confident refactoring
✅ **Professional Workflow**: Pre-commit hooks, code reviews, standards

## Git Branch Structure

- **main**: Primary development branch
- Clean working directory (as of last status)

## Project Timeline

### December 6, 2025 - Phase 2: MCP Server
**Goal:** Build Model Context Protocol server for portfolio management
- Created `backend/mcp_server/` with 4 files (server.py, tools.py, handlers.py, README.md)
- Installed MCP SDK v1.23.1
- Implemented 5 tools: get_roadmap, get_learning_entries, search_knowledge, add_learning_entry, get_progress_stats
- Fixed Django settings path (`core.settings` not `backend.settings`)
- Fixed RoadmapItem fields (uses `is_active` not `completed`)
- All tools tested and working with live database
- **Result:** MCP server successfully exposing portfolio data and operations

### December 5, 2025 - Phase 1: Dockerization
**Goal:** Containerize entire stack for production deployment
- Created Dockerfiles for backend and frontend
- Built docker-compose.yml with 4 services (postgres, backend, frontend, adminer)
- Migrated existing database to Docker postgres (611KB backup)
- Fixed Next.js environment variables (build-time vs runtime)
- Removed volume mounts from frontend to use built image
- Created `.env.example` template (security fix from `.env.docker`)
- Updated `.gitignore` to prevent secret commits
- **Result:** Full stack running in Docker, production-ready

### Earlier Development
- **RAG System:** Implemented retrieval-augmented generation with pgvector
- **Frontend:** Built Next.js 16 portfolio with Tailwind CSS 4
- **Backend:** Django 5.2.8 REST API with PostgreSQL
- **Knowledge Base:** Document upload system with semantic search
- **UI Refactor:** Converted all styles to Tailwind utilities

## Notes for AI Assistants

- Vector embeddings use 1024 dimensions (Cohere embed-english-v3.0)
- KnowledgeChunk is the unified model for all vector search operations
- The project emphasizes hallucination reduction and confidence scoring in RAG
- Document processing happens via the admin interface (DocumentUpload)
- All learning content supports markdown formatting

### AI Assistant Operating Rules

**CRITICAL: Administrator Privileges**
- **NEVER** attempt to run commands that require administrator/elevated privileges
- **NEVER** use `sudo`, `choco install`, or similar commands that need admin rights
- If a command requires admin privileges: **STOP** and ask the user to run it manually
- Provide clear instructions for the user to execute, then wait for confirmation
- Examples of commands that need admin:
  - `choco install <package>` (Windows)
  - `sudo apt install <package>` (Linux)
  - System-wide tool installations
  - Modifying system PATH or environment variables

**When Admin Rights Are Needed:**
1. Stop immediately
2. Explain what needs to be done and why
3. Provide the exact command for the user to run
4. Wait for user confirmation that it's complete
5. Only then proceed with next steps

**Example:**
```
❌ BAD: Running `choco install gitleaks` directly
✅ GOOD: "Gitleaks installation requires admin privileges. Please run this
         command in an elevated PowerShell window:

         choco install gitleaks -y

         Let me know when it's complete, and I'll help you verify the installation."
```
- MCP server tools documented in [backend/mcp_server/README.md](backend/mcp_server/README.md)

## AI Assistant Guidelines

### Security (CRITICAL - HIGHEST PRIORITY)

**Never commit or expose sensitive information:**
- API keys, passwords, secrets, tokens
- Database credentials or connection strings
- Private keys, certificates
- Environment variables containing sensitive data
- Always use `.env` files (never committed) for secrets
- Verify `.gitignore` includes sensitive files before any commits

**Security vulnerabilities to prevent:**
- SQL injection (use Django ORM properly, never raw SQL with user input)
- XSS attacks (sanitize user input, use React's built-in escaping)
- CSRF attacks (ensure Django CSRF protection is active)
- Command injection (never use `eval()`, avoid shell commands with user input)
- Path traversal (validate file paths, use Django storage APIs)
- Authentication/authorization bypasses (always check permissions)
- Insecure dependencies (keep packages updated)
- Rate limiting on API endpoints
- Proper CORS configuration

**Before any code changes involving security:**
- Review for OWASP Top 10 vulnerabilities
- Validate and sanitize all user inputs
- Use parameterized queries
- Implement proper authentication and authorization
- Secure file upload handling

### Code Quality

**Readability:**
- Clear, descriptive variable and function names
- Consistent formatting (PEP 8 for Python, ESLint for TypeScript)
- Meaningful comments for complex logic only
- Self-documenting code preferred over excessive comments
- Type hints in Python, proper TypeScript types

**Best Practices:**
- DRY (Don't Repeat Yourself) - extract reusable functions
- Single Responsibility Principle
- Proper error handling and logging
- Unit tests for critical functionality
- Meaningful commit messages
- Django migrations for all model changes
- Proper React component composition
- Use Django's built-in features (permissions, validators, etc.)

### Performance

**Backend optimization:**
- Database query optimization (select_related, prefetch_related)
- Proper indexing on frequently queried fields
- Pagination for large datasets
- Caching where appropriate (Django cache framework)
- Async views for I/O-bound operations
- Efficient vector similarity queries

**Frontend optimization:**
- Next.js server components where possible
- Lazy loading for heavy components
- Image optimization (next/image)
- Minimize bundle size
- Proper React memoization (useMemo, useCallback)
- Code splitting for route-based optimization
- Optimize asset delivery (fonts, images, scripts)

### Future Production Optimizations

**Redis Caching Strategy** (Planned Enhancement):
- **Purpose**: Demonstrate production-grade optimization knowledge and improve performance
- **API Response Caching**: Cache frequently accessed endpoints (roadmap data, stats)
- **Session Caching**: Store user sessions in Redis for faster authentication
- **Query Result Caching**: Cache expensive database queries (semantic search results)
- **Embedding Cache**: Store frequently used embeddings to reduce API calls to Cohere
- **Cache Invalidation**: Implement smart invalidation on data updates
- **Implementation**: Django cache backend with Redis, django-redis package
- **Benefits**: Reduced database load, faster response times, lower API costs, scalability

**Other Optimizations**:
- **CDN Integration**: CloudFront or similar for static asset delivery
- **Database Connection Pooling**: PgBouncer for PostgreSQL connection management
- **Load Balancing**: Multiple backend instances behind nginx
- **Background Task Queue**: Celery + Redis for async document processing
- **Monitoring**: Prometheus + Grafana for performance metrics
- **Rate Limiting**: Redis-backed rate limiting for API endpoints

### Communication Protocol

**Always keep prompts concise:**
- Break complex tasks into smaller steps
- After each significant step, ask: "Ready to proceed to the next part?"
- Wait for confirmation before continuing
- Provide clear, brief summaries of what was done

**Decision-making threshold:**
- If less than 95% certain about the approach: **ASK FIRST**
- Questions to ask when uncertain:
  - "Should I use approach A or B?"
  - "This could affect X, Y, Z - how should I proceed?"
  - "I found multiple ways to do this - which do you prefer?"
- Never guess on important architectural decisions
- Better to ask than to implement incorrectly

**When asking questions:**
- Present options clearly
- Explain trade-offs
- Recommend an approach if appropriate
- Keep explanations brief

### Example Workflow

```
✅ GOOD:
"I'll add input validation to the API endpoint. This will:
- Validate email format
- Sanitize text fields
- Check file size limits

Ready to proceed?"

❌ BAD:
"I'll add a bunch of features and change the architecture and
refactor everything and also add these 10 other things..."
```

### Uncertainty Examples

**95%+ certain - Proceed:**
- Adding a new Django model field
- Styling changes with Tailwind
- Bug fixes with clear solutions

**Less than 95% certain - ASK:**
- Architecture changes
- New external dependencies
- Database schema restructuring
- API contract changes
- Security-related implementations
- Performance optimization strategies

### Git Commit Protocol

**CRITICAL: Always ask before committing**
- **NEVER** commit code without explicit user approval
- After completing work, summarize changes and ask: "Ready to commit these changes?"
- Wait for user confirmation before running git commands
- Provide clear commit message describing what was changed and why
- User may want to review, test, or modify before committing

### Frontend Development Standards

**Component Architecture:**
- **Size**: Keep components reasonably sized (150-300 lines max)
- **Reusability**: Extract reusable logic into shared components when it makes sense
- **Single Responsibility**: Each component should have one clear purpose
- **Composition**: Build complex UIs by composing smaller, focused components
- **File Structure**: Group related components in feature-based directories

**Styling with Tailwind CSS:**
- Use Tailwind utilities as the primary styling approach (per Next.js recommendations)
- Global styles for Tailwind base (in `app/globals.css`)
- Custom design tokens defined in `@theme inline` directive in globals.css
- Complex gradients and patterns in `@layer utilities` for reusability
- Use CSS Modules only for truly custom scoped styles (rare cases)
- Follow Next.js official styling recommendations: Tailwind first, CSS Modules when needed
- Organize styles: global → Tailwind utilities → component-specific

**Custom Utilities Available:**
- `.bg-page-outer`, `.bg-page-inner` - Page gradient backgrounds
- `.bg-card` - Card gradient background
- `.text-gradient-red` - Gradient text effect with webkit support
- `.shadow-red-glow` - Red glow box shadow
- `.divider-red` - Red gradient divider line
- `.bg-radial-red` - Radial gradient with red center

**Tailwind Color Tokens:**
- `text-primary-red` → #CC0000
- `text-light-red` → #FF3333
- `text-dark-red` → #8B0000
- `text-text-light` → #E8E8E8
- `text-text-gray` → #808080
- `bg-bg-nav` → rgb(25 15 15 / 0.9)

**Common Tailwind Patterns:**
- Flex layouts: `flex items-center justify-between gap-4`
- Grid layouts: `grid grid-cols-2 gap-16`
- Transitions: `transition-all duration-200`
- Hover effects: `hover:-translate-y-0.5 hover:border-primary-red/50`
- Focus states: `focus:outline-none focus:ring-2 focus:ring-primary-red`

**Naming Conventions:**
- **Components**: PascalCase (`UserProfile.tsx`, `ChatMessage.tsx`)
- **Files**: Match component name (`UserProfile.tsx` contains `UserProfile`)
- **Props**: Descriptive, avoid abbreviations (`userName` not `uName`)
- **Functions**: camelCase, verb-based (`handleSubmit`, `fetchUserData`)
- **Constants**: UPPER_SNAKE_CASE (`API_BASE_URL`, `MAX_RETRY_COUNT`)
- **Types/Interfaces**: PascalCase with descriptive names (`UserProfile`, `ChatMessage`)
- **CSS Modules** (rare): ComponentName.module.css (`ChatMessage.module.css`)

**Accessibility (a11y):**
- Semantic HTML elements (`<button>`, `<nav>`, `<main>`, etc.)
- ARIA labels where needed (`aria-label`, `aria-describedby`)
- Keyboard navigation support (tab order, focus states)
- Color contrast ratios meet WCAG AA standards (4.5:1 for text)
- Alt text for images
- Form labels properly associated with inputs
- Focus indicators visible and clear

**Responsive Design:**
- Mobile-first approach (base styles for mobile, scale up)
- Use CSS Grid and Flexbox for layouts
- Breakpoints: mobile (default), tablet (768px), desktop (1024px), wide (1440px)
- Test on multiple screen sizes
- Touch-friendly targets (min 44x44px for interactive elements)
- Responsive typography (use rem/em, not fixed px)

**Performance Best Practices:**
- **Lazy Loading**: Use `React.lazy()` and `Suspense` for route-based code splitting
- **Image Optimization**: Always use Next.js `<Image>` component with proper sizes
- **Memoization**: Use `useMemo` for expensive calculations, `useCallback` for callbacks passed to children
- **Avoid Premature Optimization**: Profile first, optimize bottlenecks
- **Bundle Analysis**: Monitor bundle size, split large dependencies
- **Server Components**: Prefer Next.js server components for non-interactive UI

**Code Quality:**
- **TypeScript**: Strict typing, avoid `any`, use proper interfaces/types
- **Error Handling**: Graceful error states, user-friendly messages
- **Loading States**: Show feedback during async operations
- **Validation**: Client-side validation for UX, server-side for security
- **Comments**: Explain "why" not "what", document complex logic only
- **Linting**: Follow ESLint rules, fix warnings before committing

**Maintainability:**
- **Clear Architecture**: Separate concerns (components, hooks, utils, types)
- **Consistent Patterns**: Follow established patterns in the codebase
- **Documentation**: README for complex features, JSDoc for public APIs
- **Testing**: Unit tests for utilities, integration tests for critical flows
- **Version Control**: Atomic commits, descriptive messages, feature branches

**Example Component Structure:**
```
frontend/
├── app/
│   ├── globals.css              # Tailwind config and custom utilities
│   ├── page.tsx                 # Landing page
│   ├── roadmap/
│   │   └── page.tsx
│   └── learning/
│       └── page.tsx
├── components/                   # Shared components
│   ├── layout/
│   │   ├── Navigation.tsx       # Shared navigation
│   │   ├── Footer.tsx           # Shared footer
│   │   └── PageWrapper.tsx      # Page container
│   └── ui/
│       └── Card.tsx             # Reusable card component
├── hooks/                        # Custom hooks
├── utils/                        # Utility functions
└── types/                        # TypeScript types
```
