# Testing Implementation TODO

## Current Status (December 10, 2025)

✅ **Pre-commit infrastructure ready**:
- Lefthook 1.10.3 installed
- Gitleaks, Biome, Ruff configured
- Pre-commit hooks: secrets detection, linting, formatting

❌ **Missing: Actual tests**:
- `backend/portfolio/tests.py` is empty
- `backend/test_mcp_tools.py` is a manual test script (not pytest)
- No frontend tests
- Pre-push hook expects `pytest` but no real tests exist

---

## What We Need (Simple Version)

### 1. Backend Tests (pytest)
**Install dependencies:**
```bash
cd backend
pip install pytest pytest-django pytest-cov
```

**Create tests:**
- `backend/tests/test_models.py` - Test database models
- `backend/tests/test_api.py` - Test API endpoints
- `backend/tests/conftest.py` - Test fixtures

**Run tests:**
```bash
cd backend
pytest -v
```

### 2. Frontend Tests (Jest)
**Install dependencies:**
```bash
cd frontend
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

**Create tests:**
- `frontend/__tests__/Navigation.test.tsx` - Test navigation component
- `frontend/jest.config.js` - Jest configuration

**Run tests:**
```bash
cd frontend
npm test
```

### 3. Update Lefthook Pre-Push
**File:** `lefthook.yml`

Currently has:
```yaml
pre-push:
  commands:
    test-backend:
      run: cd backend && pytest --maxfail=1 --disable-warnings -q
```

This will work once we add real pytest tests!

---

## Priority After Agent Routing Fix

**Step 1: Backend Tests** (Highest priority)
- Write 5-10 basic tests for models and API
- Ensures database operations work
- Catches breaking changes before deployment

**Step 2: Frontend Tests** (Medium priority)
- Test critical components (Navigation, RoadmapCard)
- Ensures UI doesn't break

**Step 3: Agent Tests** (Lower priority)
- Test agent service endpoints
- Test MCP tool integration

---

## Quick Start Commands

### Install test dependencies:
```bash
# Backend
cd backend && pip install pytest pytest-django pytest-cov

# Frontend
cd frontend && npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

### Run existing pre-commit hooks:
```bash
git commit -m "test"  # Runs secrets detection + linting automatically
```

### Run pre-push hooks (will fail until tests exist):
```bash
git push  # Will try to run pytest (not yet available)
```

---

## Expected Timeline

**After fixing agent routing:**
1. **Day 1**: Install pytest, write 5 backend tests
2. **Day 2**: Install Jest, write 3 frontend tests
3. **Day 3**: Test pre-push hooks, verify CI/CD integration

**Total:** 3-4 hours of work

---

**Created:** December 10, 2025
**Next Action:** Fix agent routing first, then implement tests
