# AI Documentation TODOs

This document tracks missing or incomplete documentation that would significantly improve the performance and accuracy of AI coding assistants (like Gemini) when working on this repository.

## 1. High-Level Context
* [x] **`docs/TECH_STACK_AND_CONVENTIONS.md`**: Define the exact technologies, versions, and strict project rules. 
  * *Why it helps:* Prevents the AI from guessing syntax conventions (e.g., `snake_case` vs `camelCase`), architectural preferences (e.g., React Server Components vs UI components), or adding unapproved libraries.
* [x] **`docs/PROJECT_GOALS.md`** (or expand the README): Outline the primary use cases, target audience, and main features of the portfolio.
  * *Why it helps:* Guides the AI when making product-level design assumptions or suggesting UX improvements.

## 2. System Deep Dives
* [x] **`docs/DATABASE_SCHEMA.md`** (or `DATA_MODELS.md`): Document the core entity relationships and any non-obvious database constraints.
  * *Why it helps:* While the AI can read model files, understanding the *intent* behind the relationships prevents costly query-level mistakes or bad migrations.
* [x] **`docs/API_CONTRACTS.md`**: Clearly define the expected request/response payloads between the frontend and backend.
  * *Why it helps:* Serves as a single source of truth for integrations, helping the AI perfectly align frontend `fetch` calls with backend endpoints.

## 3. Workflows & Automation
* [x] **`.agents/workflows/` directory**: Create step-by-step markdown files for repetitive tasks that the AI can automatically execute. Examples to create:
  * [x] `deploy_process.md`
  * [x] `add_new_api_endpoint.md`
  * [x] `database_migration_steps.md`
  * *Why it helps:* Allows you to give the AI a single command (e.g., "run the deployment workflow") and know it will follow your exact, required steps.

## 4. Improvements to Existing Docs
* [x] **`docs/ARCHITECTURE_MAP.md`**: 
  * Add direct markdown links to crucial files (e.g., `[Auth Context](../src/contexts/AuthContext.tsx)`).
  * Use GitHub-style alerts (`> [!IMPORTANT]`) to highlight strict architectural boundaries.
  * *Why it helps:* Allows the AI to jump straight to the relevant files and prevents it from breaking architectural patterns.
