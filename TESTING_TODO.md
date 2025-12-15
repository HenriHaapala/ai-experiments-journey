# Testing Implementation TODO (Updated Dec 15, 2025)

## Current Status
- ✅ Backend pytest suite in `backend/tests/` (models, API, automation tasks)
- ✅ Frontend Jest suite in `frontend/__tests__/components/` (Navigation, Card)
- ✅ Agent service pytest suite in `agent_service/tests/` (FastAPI + MCP tools)
- ✅ Lefthook pre-push runs backend pytest; CI workflow exists
- ❌ Playwright E2E suite not created (`e2e/tests/` missing)
- ❌ Frontend page/hook/API client tests missing
- ❌ Frontend + agent_service test jobs not yet wired into GitHub Actions

## What to Add Next

### 1) End-to-End Tests (Playwright)
- Create `e2e/tests/` with coverage for homepage health, chat flow, roadmap, learning log.
- Add npm scripts: `test:e2e`, `test:e2e:ui`.
- Consider MSW or seeded data for stable runs.

### 2) Frontend Coverage Expansion
- Add page-level tests (Homepage, Roadmap, Learning).
- Add hook/API client utility tests with mocked fetch.
- Keep existing component tests as fast guardrail.

### 3) CI Integration
- Update `.github/workflows/ci.yml` to run frontend and agent_service tests alongside backend.
- Keep backend pytest in pre-push hook; optionally add `npm test` smoke locally.

## Quick Commands
```bash
# E2E scaffold
cd frontend
npm install @playwright/test
npx playwright install
npm run test:e2e

# Frontend unit/integration
npm test

# Agent service (optional local run)
cd agent_service && pytest -v
```
