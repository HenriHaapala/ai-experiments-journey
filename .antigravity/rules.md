*   **NEVER Force Kill Processes:** Do NOT use commands like `Stop-Process -Force` or `taskkill /F` unless the user explicitly asks you to "kill the dev server" or "force stop".
*   **Do Not Auto-Start Dev Servers:** Do NOT try to run `npm run dev`, `docker-compose up`, or `python manage.py runserver` on your own to "test" things unless explicitly told to.
*   **Use Workflows:** ALWAYS check the `.agents/workflows/` directory before performing routine actions (deploying, migrating, adding endpoints). Use `// turbo` bash blocks if available.
*   **Tech Stack:** Docker, Next.js (App Router), Tailwind CSS, Django, PostgreSQL (`pgvector`), FastAPI.
*   **React / Next.js:** Default to React Server Components (RSC). Only use `"use client"` when absolutely necessary (hooks, events). Use `PascalCase` for components, `camelCase` for variables.
*   **Styling:** Rely heavily on **Tailwind v4** utility classes. Do not create `.css` modules unless requested.
*   **Python / Backend:** Use `ruff` exclusively for formatting/linting (NO `black`, `flake8`, or `isort`). Use `snake_case` for functions/variables, `PascalCase` for classes. Always use UTC datetimes.

**📚 Documentation Pointers (Read these using your file viewer tools when needed):**
*   **Architecture & Flow:** Read `docs/ARCHITECTURE_MAP.md` before creating new services or modifying cross-container communication.
*   **Database & RAG:** Read `docs/DATABASE_SCHEMA.md` before making Django migrations or modifying how `KnowledgeChunk` vectors are handled.
*   **Frontend/Backend APIs:** Read `docs/API_CONTRACTS.md` before writing new `fetch` requests in Next.js or new `views.py` paths in Django.
*   **Frontend & Styles:** Read `docs/TECH_STACK_AND_CONVENTIONS.md` (specifically the TypeScript / Frontend Rules section) before adding new React components, making UI layout changes, or deciding whether to use Client vs Server Components.
*   **Strict Rules:** Read `docs/TECH_STACK_AND_CONVENTIONS.md` to understand formatting rules (e.g., must use `ruff`, not `flake8`).
