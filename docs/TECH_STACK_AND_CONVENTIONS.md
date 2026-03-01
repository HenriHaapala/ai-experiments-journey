# Tech Stack & Conventions

This document outlines the core technologies and the strict conventions that must be adhered to when developing this project. It is specifically designed to provide context for AI coding assistants.

---

## 🏗️ Core Tech Stack

### Frontend
- **Framework:** [Next.js](https://nextjs.org/) (App Router paradigm)
- **UI Library:** React 19
- **Styling:** Tailwind CSS (v4)
- **Linting/Formatting:** Biome (replaces Prettier/ESLint in some workflows, though ESLint is still present)
- **Language:** TypeScript (`strict` mode implied)

### Backend (Core Application)
- **Framework:** Django 5+
- **API Engine:** Django REST Framework (DRF)
- **Database:** PostgreSQL (with `pgvector` for embeddings)
- **Language:** Python 3.x
- **Testing:** `pytest` + `pytest-django`
- **Linting/Formatting:** `ruff` (used exclusively over flake8/black/isort)

### Agent Service (Microservice)
- **Framework:** FastAPI
- **AI Orchestration:** LangChain
- **Language:** Python 3.x

### Infrastructure & Deployment
- **Containerization:** Docker & Docker Compose (Used strictly across both **Local Development** and **Production**)
- **CI/CD:** GitHub Actions (Automated building, testing, and deployment)
- **Production Environment:** Oracle Cloud (Running via Docker containers)

---

## 🚨 Strict Project Rules & Conventions

> [!IMPORTANT]
> AI ASSISTANT DIRECTIVE: You must follow these rules without exception unless explicitly instructed otherwise by the human user.

### General Conventions
1. **Absolute Paths over Relative**: ALWAYS use absolute paths when referencing files in documentation or scripts to avoid ambiguity (e.g., `c:\ai-portfolio\frontend\app\page.tsx` or `/frontend/app/page.tsx`).
2. **Environment Variables**: Never hardcode secrets. Always assume they are passed via `.env` files. 
3. **Dockerized Environment**: Development and deployment are containerized. Ensure any new system dependencies, exposed ports, or environment variables are accurately updated in the `Dockerfile`s and `docker-compose.yml`.

### Python / Backend Rules
1. **Formatting**: Use `ruff` for all linting and formatting. Do not suggest or attempt to run `black`, `flake8`, or `isort`.
2. **Naming Convention**: Use `snake_case` for all variables, functions, and module names. Use `PascalCase` for classes.
3. **Typing**: Use comprehensive type hints (`typing` module) in all FastAPI agent code and standard Python utility scripts. Django models have their own typing inferences, but utility functions should still be typed.
4. **Dates**: Always use UTC timezone-aware datetimes.

### TypeScript / Frontend Rules
1. **Component Type**: Default to React Server Components (RSC) where possible in Next.js. Only use `"use client"` when necessary (e.g., for hooks like `useState`, `useEffect`, or browser event listeners).
2. **Naming Convention**: 
   - Use `PascalCase` for React components and their file names (e.g., `HeroSection.tsx`).
   - Use `camelCase` for variables and helper functions.
3. **Styling**: Rely heavily on Tailwind utility classes. Do not create separate `.css` modules unless absolutely necessary.
4. **Data Fetching**: Prefer Next.js native `fetch` with appropriate caching strategies inside Server Components over using heavy client-side fetching libraries unless real-time reactivity (via WebSockets/SSE) is required.
