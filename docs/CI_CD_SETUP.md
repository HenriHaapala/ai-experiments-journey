# CI/CD Pipeline Setup Guide

> **📝 Note on Server Details:**
> This documentation uses `${OCI_HOST}` as a placeholder for security.
> **Actual server details** are in `.env.production` (local file, never committed to git).
> See [`.env.production.example`](.env.production.example) for the template.

## Overview

This project has a complete CI/CD pipeline that automatically tests and deploys your application to Oracle Cloud when you push to the `main` branch.

**Pipeline Flow:**
```
GitHub Push (main)
    ↓
CI Pipeline (.github/workflows/ci.yml)
    ├── Backend Tests (Django + PostgreSQL)
    ├── Frontend Tests (Next.js + Jest)
    ├── Security Scanning (Bandit, Safety, npm audit)
    ├── Docker Build Verification
    └── Code Quality (Ruff, Black, ESLint)
    ↓
CD Pipeline (.github/workflows/deploy.yml)
    ├── Verify CI Passed
    ├── SSH to Oracle Cloud
    ├── Pull Latest Code
    ├── Rebuild Docker Images
    ├── Run Database Migrations
    ├── Restart Services
    └── Health Check Verification
    ↓
✅ Live at https://wwwportfolio.henrihaapala.com
```

---

## Step 1: Configure GitHub Secrets

GitHub Actions needs secrets to deploy to your Oracle Cloud instance. Go to your repository:

**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

#### 1. `OCI_SSH_PRIVATE_KEY`
Your SSH private key for connecting to Oracle Cloud.

**On Windows (your local machine):**
```powershell
# Copy the entire private key content (including BEGIN/END lines)
Get-Content C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key | clip
```

**In GitHub:**
- Name: `OCI_SSH_PRIVATE_KEY`
- Value: Paste the full private key (starting with `-----BEGIN OPENSSH PRIVATE KEY-----`)

#### 2. `OCI_HOST`
Your Oracle Cloud instance public IP address.

- Name: `OCI_HOST`
- Value: `${OCI_HOST}`

#### 3. `OCI_USER`
SSH username for Oracle Cloud.

- Name: `OCI_USER`
- Value: `ubuntu`

#### 4. `COHERE_API_KEY` (for testing)
Your Cohere API key for running tests.

- Name: `COHERE_API_KEY`
- Value: Your actual Cohere API key from https://dashboard.cohere.com/api-keys

---

## Step 2: Verify GitHub Actions Setup

### Enable GitHub Actions

1. Go to **Settings → Actions → General**
2. Under **Actions permissions**, select:
   - ✅ "Allow all actions and reusable workflows"
3. Under **Workflow permissions**, select:
   - ✅ "Read and write permissions"
4. Click **Save**

### Verify Branch Protection (Optional but Recommended)

Protect your `main` branch to ensure CI passes before merging:

1. Go to **Settings → Branches → Add branch protection rule**
2. Branch name pattern: `main`
3. Enable:
   - ✅ "Require a pull request before merging"
   - ✅ "Require status checks to pass before merging"
   - ✅ "Require branches to be up to date before merging"
4. Select required status checks:
   - ✅ CI Pipeline Complete
   - ✅ Backend Tests
   - ✅ Frontend Tests
   - ✅ Docker Build Test
5. Click **Create**

---

## Step 3: Configure Oracle Cloud for Automated Deployment

### Add GitHub Actions Public Key to Oracle Cloud

GitHub Actions will use SSH to connect to your server. We need to authorize GitHub's SSH connection.

**SSH into your Oracle Cloud instance:**
```bash
ssh -i C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key ubuntu@${OCI_HOST}
```

**Add your SSH key to authorized_keys (if not already there):**
```bash
# Ensure your key is authorized
cat ~/.ssh/authorized_keys

# If your key isn't there, add it:
# 1. Copy your public key from local machine:
#    Get-Content C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key.pub
# 2. On the server:
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**Create backup directory:**
```bash
mkdir -p ~/backups
chmod 700 ~/backups
```

**Grant sudo access for nginx reload (passwordless):**
```bash
sudo visudo
```

Add this line at the end:
```
ubuntu ALL=(ALL) NOPASSWD: /usr/bin/systemctl reload nginx, /usr/bin/nginx
```

Save and exit (Ctrl+X, then Y, then Enter).

**Test sudo access:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

Should work without prompting for a password.

---

## Step 4: Test the CI/CD Pipeline

### Test CI Pipeline Only (Pull Request)

1. **Create a feature branch:**
   ```bash
   git checkout -b test-ci-pipeline
   ```

2. **Make a small change:**
   ```bash
   echo "# CI/CD Test" >> README.md
   git add README.md
   git commit -m "Test CI pipeline"
   git push origin test-ci-pipeline
   ```

3. **Create a Pull Request on GitHub**
   - Go to your repository on GitHub
   - Click "Compare & pull request"
   - Create the PR

4. **Watch CI run** (should take ~5-10 minutes)
   - Go to **Actions** tab
   - See all 5 jobs running (backend tests, frontend tests, security, docker build, code quality)

### Test Full CI/CD Pipeline (Deploy to Production)

**⚠️ WARNING: This will deploy to your live site!**

1. **Merge the PR to main** (or push directly to main):
   ```bash
   git checkout main
   git pull origin main
   git merge test-ci-pipeline
   git push origin main
   ```

2. **Watch the deployment**:
   - Go to **Actions** tab on GitHub
   - See two workflows running:
     - "CI/CD Pipeline" (tests)
     - "Deploy to Oracle Cloud" (deployment)

3. **Monitor deployment progress** (~10-15 minutes total):
   - CI tests: ~5-8 minutes
   - Deployment: ~5-7 minutes

4. **Verify deployment**:
   - Check the Actions logs for "🎉 Deployment completed successfully!"
   - Visit https://wwwportfolio.henrihaapala.com
   - Site should be updated with your changes

---

## Step 5: Monitor and Debug

### View Deployment Logs

**On GitHub:**
1. Go to **Actions** tab
2. Click on the latest "Deploy to Oracle Cloud" workflow
3. Click on the "Deploy to Production" job
4. Expand steps to see detailed logs

**On Oracle Cloud (SSH):**
```bash
# SSH to server
ssh -i C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key ubuntu@${OCI_HOST}

# View Docker logs
cd ~/ai-portfolio
docker-compose logs -f

# Check container status
docker-compose ps

# View recent database backups
ls -lh ~/backups/
```

### Common Deployment Issues

#### 1. SSH Connection Fails

**Error:** "Permission denied (publickey)"

**Solution:**
- Verify `OCI_SSH_PRIVATE_KEY` secret is correct
- Ensure private key has no extra whitespace
- Check server's `~/.ssh/authorized_keys` contains your public key

#### 2. Docker Build Fails

**Error:** "failed to build image"

**Solution:**
```bash
# SSH to server and manually rebuild
cd ~/ai-portfolio
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Database Migration Fails

**Error:** "django.db.utils.OperationalError"

**Solution:**
```bash
# Check database status
docker-compose exec postgres psql -U aiportfolio -d aiportfolio

# Manually run migrations
docker-compose exec backend python manage.py migrate

# Restore from backup if needed
docker-compose exec -T postgres psql -U aiportfolio aiportfolio < ~/backups/pre-deploy-YYYYMMDD-HHMMSS.sql
```

#### 4. Health Check Fails

**Error:** "Frontend/Backend health check failed"

**Solution:**
```bash
# Check if containers are running
docker-compose ps

# Check logs for errors
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

#### 5. Deployment Succeeds but Site Shows Old Version

**Possible Causes:**
- Browser cache
- Nginx cache
- Next.js build cache

**Solution:**
```bash
# SSH to server
cd ~/ai-portfolio

# Force rebuild frontend with no cache
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Clear Next.js cache
docker-compose exec frontend rm -rf .next/cache

# Restart nginx
sudo systemctl reload nginx
```

---

## Step 6: Rollback Strategy

If a deployment breaks your site, you can quickly rollback.

### Automatic Rollback

The CD pipeline automatically rolls back on failure. Check the "Rollback on failure" step in the Actions logs.

### Manual Rollback

**SSH to server:**
```bash
ssh -i C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key ubuntu@${OCI_HOST}
cd ~/ai-portfolio

# View recent commits
git log --oneline -5

# Rollback to previous commit
git checkout HEAD~1

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Verify site is working
curl http://localhost:3000
curl http://localhost:8000/api/health/
```

### Restore Database from Backup

```bash
# List backups
ls -lh ~/backups/

# Restore from specific backup
docker-compose exec -T postgres psql -U aiportfolio aiportfolio < ~/backups/pre-deploy-20251209-143022.sql

# Verify data
docker-compose exec postgres psql -U aiportfolio -d aiportfolio -c "SELECT COUNT(*) FROM portfolio_roadmapsection;"
```

---

## Step 7: Advanced Configuration

### Deploy Only Specific Services

Edit `.github/workflows/deploy.yml` to deploy only frontend or backend:

```yaml
# Deploy only frontend
- name: Deploy Frontend Only
  run: |
    ssh ... << 'ENDSSH'
      cd ~/ai-portfolio
      docker-compose build frontend
      docker-compose up -d frontend
    ENDSSH
```

### Add Slack/Discord Notifications

Add a notification step in `deploy.yml`:

```yaml
- name: Send Slack notification
  if: always()
  uses: slackapi/slack-github-action@v1.24.0
  with:
    payload: |
      {
        "text": "Deployment ${{ job.status }}: ${{ github.sha }}",
        "url": "https://wwwportfolio.henrihaapala.com"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Run Database Backups Before Deploy

The pipeline already includes this:

```bash
docker-compose exec -T postgres pg_dump -U aiportfolio aiportfolio > ~/backups/pre-deploy-$(date +%Y%m%d-%H%M%S).sql
```

Backups are stored in `~/backups/` on the Oracle Cloud instance.

### Cleanup Old Backups

Add a cron job to remove old backups:

```bash
# SSH to server
crontab -e

# Add this line (delete backups older than 7 days, run daily at 2 AM)
0 2 * * * find ~/backups -name "pre-deploy-*.sql" -mtime +7 -delete
```

---

## Step 8: Performance Optimization

### Reduce Deployment Downtime

Currently, deployment has ~30 seconds of downtime (while containers restart). To achieve zero-downtime:

**Option 1: Blue-Green Deployment**
Run two sets of containers, switch nginx upstream when new version is ready.

**Option 2: Rolling Updates**
Use Docker Swarm or Kubernetes for rolling updates.

**Option 3: Cache Warming**
Pre-build Next.js pages before switching traffic.

### Speed Up Docker Builds

Use Docker layer caching in GitHub Actions:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
  with:
    driver: docker-container

- name: Build and cache backend
  uses: docker/build-push-action@v5
  with:
    context: ./backend
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

---

## Workflow Triggers

### Current Triggers

**CI Pipeline (`ci.yml`):**
- ✅ Push to `main` or `develop` branches
- ✅ Pull requests to `main`
- ✅ Manual trigger (workflow_dispatch)

**CD Pipeline (`deploy.yml`):**
- ✅ Push to `main` branch only
- ✅ Manual trigger (workflow_dispatch)

### Manual Deployment

To manually trigger a deployment without pushing code:

1. Go to **Actions** tab on GitHub
2. Select "Deploy to Oracle Cloud"
3. Click "Run workflow"
4. Select branch (usually `main`)
5. Click "Run workflow" button

Useful for:
- Redeploying after a rollback
- Deploying after fixing server issues
- Testing deployment without code changes

---

## Monitoring and Logs

### GitHub Actions Dashboard

- **Actions tab**: See all workflow runs
- **Status badges**: Add to README.md

```markdown
![CI/CD](https://github.com/HenriHaapala/ai-experiments-journey/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/HenriHaapala/ai-experiments-journey/actions/workflows/deploy.yml/badge.svg)
```

### Server-Side Monitoring

**Set up log rotation:**
```bash
# SSH to server
sudo nano /etc/docker/daemon.json
```

Add:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Restart Docker:
```bash
sudo systemctl restart docker
cd ~/ai-portfolio
docker-compose up -d
```

**Monitor disk space:**
```bash
df -h
docker system df
```

**Clean up old Docker images:**
```bash
docker system prune -a --volumes -f
```

---

## Security Best Practices

### 1. Rotate Secrets Regularly

Every 3-6 months:
- Generate new SSH key pair
- Update `OCI_SSH_PRIVATE_KEY` in GitHub Secrets
- Update `~/.ssh/authorized_keys` on server

### 2. Limit SSH Access

**On Oracle Cloud instance:**
```bash
sudo nano /etc/ssh/sshd_config
```

Add:
```
# Only allow specific user
AllowUsers ubuntu

# Disable password authentication (key-only)
PasswordAuthentication no

# Disable root login
PermitRootLogin no
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### 3. Enable Firewall Logging

```bash
# Log dropped packets
sudo iptables -A INPUT -j LOG --log-prefix "DROPPED: " --log-level 4

# Save rules
sudo netfilter-persistent save
```

### 4. Monitor Failed Login Attempts

```bash
# View failed SSH attempts
sudo grep "Failed password" /var/log/auth.log | tail -20

# Install fail2ban for automatic blocking
sudo apt update
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Cost Optimization

### GitHub Actions Minutes

**Free tier:** 2,000 minutes/month for private repos (unlimited for public)

**Estimated usage:**
- CI Pipeline: ~8 minutes per run
- CD Pipeline: ~7 minutes per run
- **Total per deployment:** ~15 minutes

**Deployments per month:**
- 10 deployments/month = 150 minutes (well within free tier)
- 50 deployments/month = 750 minutes (still within free tier)

**To reduce minutes:**
1. Cache dependencies (already implemented)
2. Run tests in parallel (already implemented)
3. Skip CD on non-main branches (already implemented)
4. Use matrix strategy for multi-version testing (optional)

---

## Troubleshooting Checklist

Before each deployment, verify:

✅ **Local Tests Pass:**
```bash
cd backend && python manage.py test
cd frontend && npm test
```

✅ **Docker Build Works Locally:**
```bash
docker-compose build
docker-compose up -d
docker-compose ps  # All should be "Up"
```

✅ **Secrets Are Configured:**
- Go to GitHub repo → Settings → Secrets → Actions
- Verify `OCI_SSH_PRIVATE_KEY`, `OCI_HOST`, `OCI_USER`, `COHERE_API_KEY` exist

✅ **Server Is Accessible:**
```bash
ssh -i C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key ubuntu@${OCI_HOST} "echo 'Connection OK'"
```

✅ **Disk Space Available:**
```bash
ssh -i ... ubuntu@${OCI_HOST} "df -h"
# /dev/sda1 should have >5GB free
```

✅ **Database Backup Exists:**
```bash
ssh -i ... ubuntu@${OCI_HOST} "ls -lh ~/backups/ | tail -5"
```

---

## Success Metrics

After deployment, verify:

✅ **All containers running:**
```bash
docker-compose ps
# Should show 6 services: postgres, backend, frontend, agent, redis, adminer
```

✅ **Health checks pass:**
```bash
curl -f https://wwwportfolio.henrihaapala.com/api/health/
curl -f https://wwwportfolio.henrihaapala.com
curl -f https://wwwportfolio.henrihaapala.com/agent/health
```

✅ **SSL certificate valid:**
```bash
curl -vI https://wwwportfolio.henrihaapala.com 2>&1 | grep "SSL certificate verify ok"
```

✅ **No errors in logs:**
```bash
docker-compose logs --tail=50 | grep -i error
```

---

## Next Steps

1. **Add this to your GitHub repo secrets** (Step 1)
2. **Enable GitHub Actions** (Step 2)
3. **Test with a small PR** (Step 4)
4. **Add status badges to README.md**
5. **Set up monitoring/notifications** (Step 7)

Once configured, every push to `main` will automatically:
- ✅ Run tests
- ✅ Build Docker images
- ✅ Deploy to production
- ✅ Run health checks
- ✅ Rollback on failure

**Your deployment flow:**
```bash
git add .
git commit -m "Add new feature"
git push origin main
# ☕ Get coffee, wait 10 minutes
# ✅ Feature is live at https://wwwportfolio.henrihaapala.com
```

---

## Additional Resources

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Docker Compose Docs:** https://docs.docker.com/compose/
- **Oracle Cloud Free Tier:** https://www.oracle.com/cloud/free/
- **Let's Encrypt:** https://letsencrypt.org/
- **nginx Docs:** https://nginx.org/en/docs/

**Questions or issues?** Check the GitHub Actions logs first, then review the troubleshooting section above.
