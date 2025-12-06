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
- **Services**:
  - PostgreSQL 16 + pgvector (port 5432)
  - Django Backend API (port 8000)
  - Next.js Frontend (port 3000)
  - Adminer DB Admin (port 8080)
- **Design Principle**: Cloud-native and production-ready
  - Environment variables for all configuration
  - No hardcoded paths or localhost references
  - Horizontal scaling ready
  - Separated concerns with health checks

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

3. **Content Management**
   - Site content with slug-based routing
   - Media attachments (images, videos, links, files)
   - Markdown content support

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

## Recent Development

### Phase 2 Complete: MCP Server (Dec 6, 2025)
- **MCP Server Built** - Model Context Protocol server exposing 5 portfolio management tools
- **Tool Integration** - get_roadmap, get_learning_entries, search_knowledge, add_learning_entry, get_progress_stats
- **Django Integration** - MCP handlers using Django ORM for database access
- **RAG-Powered Search** - Semantic search across 41 knowledge chunks with Cohere embeddings
- **Documentation** - Complete API documentation in [backend/mcp_server/README.md](backend/mcp_server/README.md)

### Phase 1 Complete: Full Stack Dockerization (Dec 5, 2025)
- **Dockerization Complete** - Full stack containerized with docker-compose (4 services)
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
│   │   └── README.md        # MCP server documentation
│   ├── portfolio/
│   │   ├── models.py        # Django models (roadmap, embeddings, RAG)
│   │   └── ...
│   ├── venv/                # Python virtual environment (local dev)
│   └── requirements.txt     # Python dependencies (includes mcp>=0.9.0)
├── frontend/
│   ├── Dockerfile           # Frontend Docker configuration
│   ├── .dockerignore        # Docker build exclusions
│   ├── app/                 # Next.js app directory
│   ├── node_modules/        # Node dependencies
│   └── package.json         # Node dependencies config
├── docker-compose.yml       # Multi-service orchestration
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
