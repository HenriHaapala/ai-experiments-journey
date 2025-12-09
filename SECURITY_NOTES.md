# Security Notes

## 🔒 Sensitive Information Protection

This repository follows security best practices to protect sensitive information.

### Files Never Committed to Git

The following files contain sensitive data and are **gitignored**:

1. **`.env.production`** - Production server details (IP address, SSH key paths)
2. **`.env`** - Environment variables with API keys and secrets
3. **`*.key`, `*.pem`** - SSH private keys and certificates
4. **`*.sql`** - Database backups (may contain user data)

### Placeholder Usage in Documentation

Public documentation files use placeholders instead of real values:

| Placeholder | Description | Real Value Location |
|------------|-------------|---------------------|
| `${OCI_HOST}` | Oracle Cloud server IP | `.env.production` |
| `${OCI_SSH_KEY_PATH}` | SSH private key path | `.env.production` |
| `your_cohere_api_key_here` | Cohere API key | `.env` |
| `your_secure_password_here` | Database password | `.env` |

### Template Files (Safe to Commit)

These template files show structure without exposing secrets:

- ✅ `.env.example` - Environment variables template
- ✅ `.env.production.example` - Production server template
- ✅ All `.md` documentation files (use placeholders)

### How to Use `.env.production`

**If you're setting up this project:**

1. Copy the template:
   ```bash
   cp .env.production.example .env.production
   ```

2. Edit `.env.production` with your actual server details:
   ```bash
   nano .env.production
   # Fill in OCI_HOST, OCI_SSH_KEY_PATH, etc.
   ```

3. Source it when needed:
   ```bash
   source .env.production
   ssh -i $OCI_SSH_KEY_PATH $OCI_USER@$OCI_HOST
   ```

4. **NEVER commit it:**
   ```bash
   git status  # Should NOT show .env.production
   ```

### GitHub Secrets Configuration

Sensitive values for CI/CD are stored as **GitHub Secrets** (not in code):

1. Go to: **Repository → Settings → Secrets and variables → Actions**
2. Add these secrets:
   - `OCI_SSH_PRIVATE_KEY` - Full SSH private key content
   - `OCI_HOST` - Server IP address
   - `OCI_USER` - SSH username (ubuntu)
   - `COHERE_API_KEY` - Cohere API key
   - `GROQ_API_KEY` - Groq API key (optional)

### What's Safe to Share Publicly

✅ **Safe to commit/share:**
- Template files (`.env.example`, `.env.production.example`)
- Documentation with placeholders
- Docker configuration files
- Source code (backend, frontend)
- GitHub Actions workflow files (use secrets, not hardcoded values)

❌ **NEVER commit/share:**
- `.env`, `.env.production` (actual secrets)
- SSH private keys (`.key`, `.pem` files)
- Database backups (`.sql` files)
- API keys or passwords
- Server IP addresses in documentation (use placeholders)

### Security Checklist Before Committing

Before running `git commit`, verify:

```bash
# 1. Check for secrets in staged files
git diff --cached | grep -i "password\|secret\|key"

# 2. Verify .env files are not staged
git status | grep -E "\.env$|\.env\.production$"

# 3. Run Gitleaks to scan for secrets (if installed)
gitleaks detect --source . --verbose

# 4. Check gitignore is working
git check-ignore .env .env.production
```

### If You Accidentally Committed Secrets

**IMMEDIATELY:**

1. **Rotate all exposed credentials**:
   - Generate new SSH keys
   - Regenerate API keys (Cohere, Groq)
   - Change database passwords
   - Update GitHub Secrets

2. **Remove from git history**:
   ```bash
   # Using git-filter-repo (recommended)
   git filter-repo --invert-paths --path .env

   # Or use BFG Repo-Cleaner
   bfg --delete-files .env
   ```

3. **Force push** (⚠️ WARNING: rewrites history):
   ```bash
   git push origin main --force
   ```

4. **Notify team members** to re-clone the repository

### Additional Security Measures

**On Production Server:**

1. **Firewall rules** - Only allow ports 22, 80, 443
2. **SSH key-only auth** - Disable password authentication
3. **Fail2ban** - Auto-ban repeated failed login attempts
4. **Regular updates** - Keep system packages up to date
5. **Database backups** - Encrypted and stored securely

**For GitHub Actions:**

1. **Use secrets** - Never hardcode credentials in workflows
2. **Limit workflow permissions** - Read-only by default
3. **Branch protection** - Require PR reviews before merging to main
4. **Audit logs** - Review Actions logs for suspicious activity

### Reporting Security Issues

If you find a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Contact the repository owner privately
3. Provide details: what, where, impact, reproduction steps
4. Wait for response before public disclosure

---

## 🛡️ Best Practices Summary

✅ **DO:**
- Use `.env` files for all secrets (gitignored)
- Use placeholders in documentation (`${VARIABLE}`)
- Store production secrets in GitHub Secrets
- Rotate credentials regularly (every 3-6 months)
- Use strong, unique passwords for each service
- Enable 2FA on GitHub, Oracle Cloud, API providers

❌ **DON'T:**
- Commit `.env` files to git
- Hardcode IP addresses, passwords, or API keys
- Share SSH private keys via email or Slack
- Use the same password for multiple services
- Disable security features for convenience
- Ignore security warnings from dependency scanners

---

**Remember:** Security is not a one-time setup. Regularly review access logs, update dependencies, and audit your security practices.
