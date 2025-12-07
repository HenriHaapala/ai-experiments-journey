# Testing & Pre-Commit Hooks Setup

## Pre-Commit Hooks (Lefthook)

This project uses [Lefthook](https://github.com/evilmartians/lefthook) for Git hooks (5-10x faster than Husky).

### What Runs on Every Commit

The following checks run automatically **before each commit**:

1. **Secrets Detection** (Gitleaks) - Priority 1
   - Scans staged files for API keys, passwords, tokens
   - Blocks commit if secrets are found

2. **Frontend Linting** (Biome) - Priority 2
   - Checks TypeScript/JavaScript/JSON files
   - Auto-fixes formatting issues
   - 100x faster than ESLint + Prettier

3. **Python Formatting** (Ruff) - Priority 2
   - Formats Python code (replaces Black)
   - 10-100x faster than Black

4. **Python Linting** (Ruff) - Priority 3
   - Checks Python code quality
   - Auto-fixes common issues
   - Replaces flake8, isort, pyupgrade

### Installation

Hooks are installed automatically when you run `npm install`:

```bash
npm install
# This runs "lefthook install" automatically via the "prepare" script
```

### Manual Commands

```bash
# Install hooks
npm run hooks:install

# Uninstall hooks
npm run hooks:uninstall

# Run pre-commit checks manually
npm run hooks:run

# Run specific hook
lefthook run pre-commit

# Skip hooks for one commit (use sparingly!)
git commit --no-verify -m "message"
```

### What Runs Before Push

Before pushing to remote:
- Backend tests (`pytest`)
- Full security scan (Gitleaks)

### Configuration Files

- [`lefthook.yml`](lefthook.yml) - Hook configuration
- [`ruff.toml`](ruff.toml) - Python linting/formatting rules
- [`biome.json`](biome.json) - Frontend linting/formatting rules
- [`.gitleaks.toml`](.gitleaks.toml) - Secrets detection rules
- [`.semgrep.yml`](.semgrep.yml) - SAST security rules

### Troubleshooting

#### Hooks not running
```bash
# Reinstall hooks
npm run hooks:install
```

#### Need to skip hooks temporarily
```bash
# Skip ALL hooks (use with caution!)
git commit --no-verify -m "Emergency hotfix"

# Skip specific hook
LEFTHOOK_EXCLUDE=biome-check git commit -m "Skip Biome"
```

#### Hooks too slow
```bash
# Disable type checking (optional rules in lefthook.yml)
# They are commented out by default
```

## Testing Infrastructure

### Backend Tests (pytest)

```bash
# Run all tests with coverage
npm run test:backend

# Run specific test file
cd backend
pytest tests/test_models.py -v

# Run tests matching pattern
pytest -k "test_roadmap" -v

# Fast tests only (skip integration)
pytest -m "not integration"
```

### Frontend Tests (Jest + React Testing Library)

```bash
# Run all tests
npm run test:frontend

# Watch mode
cd frontend
npm run test:watch

# Coverage report
npm run test:coverage
```

### Agent Service Tests

```bash
# Run agent tests
npm run test:agent

# With mock backend
cd agent_service
GROQ_API_KEY=mock pytest -v
```

### Run All Tests

```bash
npm run test:all
```

## Code Quality Tools

### Ruff (Python)

Ruff replaces **7 tools** in one:
- flake8 (linting)
- black (formatting)
- isort (import sorting)
- pyupgrade (modernize code)
- pydocstyle (docstring style)
- autoflake (remove unused imports)
- And more...

**Speed**: 10-100x faster than alternatives (Rust-based)

```bash
# Format code
cd backend
ruff format .

# Check and fix issues
ruff check --fix .

# Check only (no fixes)
ruff check .
```

### Biome (Frontend)

Biome replaces **2 tools**:
- ESLint (linting)
- Prettier (formatting)

**Speed**: 100x faster than ESLint + Prettier (Rust-based)

```bash
# Format code
cd frontend
biome format --write .

# Lint and fix
biome check --write .

# Check only
biome check .
```

## Security Scanning

See [SECURITY_SETUP.md](SECURITY_SETUP.md) for full security documentation.

Quick commands:
```bash
# Run all security scans
npm run security:all

# Individual scans
npm run security:secrets   # Gitleaks
npm run security:backend   # Bandit + Safety
npm run security:frontend  # npm audit
npm run security:sast      # Semgrep
```

## CI/CD Integration (Coming Soon)

GitHub Actions workflow will:
- Run all tests
- Run all security scans
- Check code quality
- Generate coverage reports
- Block merge if checks fail

## Best Practices

1. **Commit Often**: Pre-commit hooks are fast (<3 seconds typically)
2. **Let Tools Fix**: Most issues are auto-fixed by Ruff and Biome
3. **Review Fixes**: Check what was auto-fixed before committing
4. **Don't Skip Hooks**: Only use `--no-verify` in emergencies
5. **Run Tests Locally**: Before pushing, run `npm run test:all`

## Tool Comparison

| Tool | What It Replaces | Speed | Language |
|------|------------------|-------|----------|
| Ruff | flake8, black, isort, pyupgrade | 10-100x faster | Python |
| Biome | ESLint, Prettier | 100x faster | JS/TS |
| Lefthook | Husky, pre-commit | 5-10x faster | Git hooks |
| Gitleaks | TruffleHog, detect-secrets | Very fast | Secrets |
| Semgrep | Multiple SAST tools | Fast | Multi-lang |

All modern tools are **Rust-based** for maximum performance.

---

For more details:
- [SECURITY_SETUP.md](SECURITY_SETUP.md) - Security tools documentation
- [CLAUDE.md](CLAUDE.md) - Full project documentation
