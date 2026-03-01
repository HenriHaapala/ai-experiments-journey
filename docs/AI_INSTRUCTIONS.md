# AI Agent Instructions & Boundaries

This document contains strict behavioral instructions for any AI assistant (like Gemini or general coding agents) operating within this repository. 

> [!IMPORTANT]
> **AI ASSISTANT: You MUST read and adhere to these rules before taking any action.**

## 1. Process Management & Terminal Commands

*   **NEVER Force Kill Processes:** Do NOT use commands like `Stop-Process -Force` or `taskkill /F` unless the user explicitly asks you to "kill the dev server" or "force stop". 
    *   *Why:* AI agents sometimes try to forcefully clear ports when they get confused by background servers (like `npm run dev` or `docker-compose up`). This disrupts the user's workflow.
*   **Do Not Auto-Start Dev Servers:** Do NOT try to run `npm run dev`, `docker-compose up`, or `python manage.py runserver` on your own to "test" things unless explicitly told to. The user manages the development environments. 

## 2. Using Workflows (`.agents/workflows/`)

If you need to perform routine actions (deploying, migrating, adding endpoints), ALWAYS check the `.agents/workflows/` directory first. 

*   These `.md` files contain the *exact* permitted steps for this specific project.
*   If a workflow file contains a `// turbo` or `// turbo-all` annotation, you are authorized to run those specific bash commands automatically without interrupting the user for approval.

## 3. Tech Stack Awareness

Before modifying any code, remind yourself of the project's core technologies found in `docs/TECH_STACK_AND_CONVENTIONS.md`:
*   **Infrastructure:** Docker & Docker Compose (used locally and in production).
*   **Frontend:** Next.js (App Router, RSCs preferred), Tailwind CSS, Biome (for formatting/linting).
*   **Backend:** Django, PostgreSQL (with `pgvector`), `ruff` (for formatting/linting).
*   **Agent Service:** FastAPI.

## 4. Documentation as a Source of Truth

Never guess architectural decisions. Consult the `docs/` folder:
*   `ARCHITECTURE_MAP.md`: For service relationships and file maps.
*   `DATABASE_SCHEMA.md`: For understanding how `KnowledgeChunk` and RAG works.
*   `API_CONTRACTS.md`: For understanding how the Frontend, Backend, and FastAPI agent communicate.
