# Security Testing Setup Guide

This document describes the security testing infrastructure for the AI Portfolio project, including all tools, configurations, and usage instructions.

## Overview

The project uses a comprehensive security testing stack to prevent vulnerabilities before they reach production:

- **Gitleaks**: Detects secrets, API keys, passwords in code
- **Semgrep**: Multi-language SAST (Static Application Security Testing)
- **Bandit**: Python-specific security linter for Django
- **Safety**: Python dependency vulnerability scanner
- **Biome**: Modern frontend linting and formatting (Rust-based, 100x faster than ESLint)

## Quick Start

### Install Dependencies

```bash
# Install frontend dependencies (including Biome and security tools)
cd frontend
npm install

# Install backend dependencies (including Bandit, Safety, pytest)
cd ../backend
pip install -r requirements.txt

# Install agent service dependencies
cd ../agent_service
pip install -r requirements.txt

# Or install everything at once from root
npm run install:all
```

### Install External Tools

Some security tools need to be installed globally:

```bash
# Install Gitleaks (secrets detection)
# macOS
brew install gitleaks

# Windows (Chocolatey)
choco install gitleaks

# Linux
# Download from https://github.com/gitleaks/gitleaks/releases

# Install Semgrep (SAST)
# macOS/Linux
brew install semgrep

# Windows
pip install semgrep

# Or use Docker
docker pull semgrep/semgrep
```

## Running Security Scans

### All Security Scans (Recommended)

```bash
# Run all security scans from project root
npm run security:all
```

This runs:
1. Gitleaks (secrets detection)
2. Bandit (Python security)
3. Safety (Python dependency vulnerabilities)
4. npm audit (JavaScript dependency vulnerabilities)
5. Semgrep (multi-language SAST)

### Individual Scans

#### 1. Secrets Detection (Gitleaks)

Scans for API keys, passwords, tokens, and other secrets:

```bash
npm run security:secrets

# Output: gitleaks-report.json
```

**What it catches:**
- Hardcoded API keys (Cohere, Groq, OpenAI, etc.)
- Database credentials
- Django secret keys
- Generic API keys and tokens
- Private keys and certificates

#### 2. Python Security (Bandit)

Scans Python code for security issues:

```bash
npm run security:backend
# Or directly in backend directory
cd backend
bandit -r . -f json -o bandit-report.json
```

**What it catches:**
- SQL injection vulnerabilities
- Command injection (shell=True)
- Use of eval() or exec()
- Insecure deserialization (pickle)
- Hardcoded passwords
- Weak cryptography
- And more...

#### 3. Python Dependencies (Safety)

Checks Python dependencies for known CVEs:

```bash
cd backend
safety check --json --output safety-report.json
```

**What it catches:**
- Known vulnerabilities in packages listed in requirements.txt
- Outdated packages with security fixes available
- CVE identifiers and severity ratings

#### 4. JavaScript Dependencies (npm audit)

Checks Node.js dependencies for vulnerabilities:

```bash
npm run security:frontend
# Or
cd frontend
npm audit --audit-level=moderate
```

**What it catches:**
- Known vulnerabilities in npm packages
- Dependency tree vulnerabilities
- Suggested fixes and updates

#### 5. Multi-Language SAST (Semgrep)

Static analysis for Python and JavaScript/TypeScript:

```bash
npm run security:sast

# Output: semgrep-report.json
```

**What it catches:**

*Python/Django:*
- SQL injection
- XSS vulnerabilities
- CSRF protection issues
- Command injection
- Insecure deserialization
- Hardcoded secrets
- DEBUG=True in production
- Weak random number generation

*JavaScript/TypeScript:*
- XSS (innerHTML, dangerouslySetInnerHTML)
- eval() usage
- Insecure HTTP requests
- Hardcoded API keys
- SQL injection in raw queries
- Weak crypto (Math.random())

## Configuration Files

### `.gitleaks.toml`

Gitleaks configuration with custom rules for:
- Cohere API keys
- Groq API keys
- Django secret keys
- PostgreSQL passwords
- Generic API key patterns

**Allowlisted files:**
- `.env.example` (template files)
- Documentation files (`.md`)
- Lock files

### `.semgrep.yml`

Semgrep rules covering:
- OWASP Top 10 vulnerabilities
- Python/Django best practices
- React/Next.js security
- Custom security patterns

**Excluded paths:**
- `*/migrations/*`
- `*/node_modules/*`
- `*/venv/*`
- Test files (`*.test.js`, `*.spec.ts`)

### `.bandit`

Bandit configuration:
- Excludes: venv, migrations, tests
- Severity: MEDIUM and above
- Confidence: MEDIUM and above

### `biome.json`

Biome configuration for frontend:
- Linting rules (including security)
- Formatting (100x faster than Prettier)
- Import organization
- TypeScript/React best practices

## Pre-Commit Integration (Coming Soon)

The next phase will add automatic pre-commit hooks using **Lefthook**:

```yaml
# lefthook.yml (planned)
pre-commit:
  parallel: true
  commands:
    secrets:
      run: gitleaks protect --staged --verbose

    biome:
      glob: "*.{js,ts,tsx,json}"
      run: npx biome check --write {staged_files}

    python-format:
      glob: "*.py"
      run: black {staged_files}

    python-lint:
      glob: "*.py"
      run: ruff check --fix {staged_files}
```

This will automatically run security checks on every commit.

## CI/CD Integration (Coming Soon)

GitHub Actions workflow will run all security scans on:
- Every push to main/develop
- Every pull request
- Nightly scheduled scans

## Interpreting Results

### Gitleaks Report (`gitleaks-report.json`)

```json
{
  "DetectorName": "cohere-api-key",
  "Match": "co-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "File": "backend/settings.py",
  "Line": "45"
}
```

**Action:** Move secrets to `.env` file, never commit them.

### Bandit Report (`bandit-report.json`)

```json
{
  "issue_severity": "HIGH",
  "issue_confidence": "HIGH",
  "issue_text": "Possible SQL injection vector through string-based query construction",
  "test_id": "B608",
  "line_number": 123
}
```

**Action:** Use Django ORM or parameterized queries.

### Semgrep Report (`semgrep-report.json`)

```json
{
  "check_id": "django-raw-sql-injection",
  "path": "backend/portfolio/views.py",
  "start": {"line": 45},
  "extra": {
    "severity": "ERROR",
    "metadata": {
      "owasp": "A03:2021 - Injection"
    }
  }
}
```

**Action:** Refactor to use safe query methods.

## Best Practices

### 1. Never Commit Secrets

- Always use environment variables (`.env` files)
- Use `.env.example` as templates (safe to commit)
- Run `npm run security:secrets` before commits

### 2. Regular Scans

```bash
# Before every commit
npm run security:all

# Weekly (or integrate into CI/CD)
npm run security:backend
npm run security:frontend
```

### 3. Fix Issues Immediately

- **HIGH severity**: Fix before committing
- **MEDIUM severity**: Fix before merging to main
- **LOW severity**: Document and plan to fix

### 4. Update Dependencies Regularly

```bash
# Check for outdated packages
cd frontend && npm outdated
cd backend && pip list --outdated

# Update with caution (test after updating)
npm update
pip install --upgrade <package>
```

### 5. Review Security Reports

Security scan reports are in `.gitignore` (not committed):
- `gitleaks-report.json`
- `bandit-report.json`
- `safety-report.json`
- `semgrep-report.json`

Review these locally and in CI/CD pipelines.

## Common Issues and Solutions

### Issue: Gitleaks False Positive

**Solution:** Add to `.gitleaks.toml` allowlist:

```toml
[allowlist]
regexes = [
    '''YOUR_FALSE_POSITIVE_PATTERN''',
]
```

### Issue: Bandit Reports Test Files

**Solution:** Already configured to skip tests. If needed, adjust `.bandit`:

```ini
exclude_dirs = [
    "/tests",
    "*/test_*.py",
]
```

### Issue: Semgrep Too Noisy

**Solution:** Adjust severity in `.semgrep.yml`:

```yaml
# Change from "ERROR" to "WARNING" for less critical rules
severity: WARNING
```

### Issue: npm audit Reports Unfixable Issues

**Solution:**

```bash
# Generate audit report
npm audit --json > audit-report.json

# If vulnerability is in dev dependencies and acceptable
npm audit --production

# Use --audit-level to adjust threshold
npm audit --audit-level=high
```

## Tool Comparison

| Tool | Language | Speed | Accuracy | False Positives |
|------|----------|-------|----------|-----------------|
| Gitleaks | All | ⚡⚡⚡ Very Fast | High | Low |
| Semgrep | Python, JS/TS | ⚡⚡ Fast | Very High | Low |
| Bandit | Python | ⚡⚡ Fast | High | Medium |
| Safety | Python (deps) | ⚡⚡⚡ Very Fast | Very High | Very Low |
| npm audit | JS/TS (deps) | ⚡⚡⚡ Very Fast | Very High | Low |
| Biome | JS/TS | ⚡⚡⚡ Extremely Fast | High | Low |

## Resources

- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [Semgrep Rules](https://semgrep.dev/explore)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)
- [Biome Documentation](https://biomejs.dev/)
- [OWASP Top 10](https://owasp.org/Top10/)

## Next Steps

After setting up security scanning:

1. **Run initial scan**: `npm run security:all`
2. **Fix critical issues**: Address HIGH severity findings
3. **Set up pre-commit hooks**: Implement Lefthook (Phase 2)
4. **Add CI/CD integration**: GitHub Actions workflow (Phase 2)
5. **Regular audits**: Schedule weekly/monthly scans

---

**For questions or issues, see the main [CLAUDE.md](CLAUDE.md) documentation.**
