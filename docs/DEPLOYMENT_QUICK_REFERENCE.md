# Deployment Quick Reference

> **📝 Note:** This file uses `${OCI_HOST}` placeholders. Real values are in `.env.production` (not committed).

## 🚀 Quick Commands

### Local Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose build
docker-compose up -d

# Stop all services
docker-compose down

# Clean restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### SSH to Production Server

```powershell
# From Windows
ssh -i C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key ubuntu@${OCI_HOST}
```

```bash
# From Linux/Mac
ssh -i ~/path/to/ssh-key-2025-12-09.key ubuntu@${OCI_HOST}
```

### Production Server Commands

```bash
# Navigate to project
cd ~/ai-portfolio

# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f agent

# Restart a service
docker-compose restart backend

# Pull latest code and restart
git pull origin main
docker-compose build
docker-compose up -d

# Database backup
docker-compose exec -T postgres pg_dump -U aiportfolio aiportfolio > ~/backups/backup-$(date +%Y%m%d-%H%M%S).sql

# Database restore
docker-compose exec -T postgres psql -U aiportfolio aiportfolio < ~/backups/backup-20251209-143022.sql

# Run Django migrations
docker-compose exec backend python manage.py migrate

# Reload nginx
sudo nginx -t
sudo systemctl reload nginx

# Check disk space
df -h
docker system df
```

---

## 🔍 Debugging Commands

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/api/health/

# Frontend
curl http://localhost:3000

# Agent service
curl http://localhost:8001/health

# Public HTTPS endpoints
curl https://wwwportfolio.henrihaapala.com
curl https://wwwportfolio.henrihaapala.com/api/health/
curl https://wwwportfolio.henrihaapala.com/agent/health
```

### View Container Status

```bash
# Detailed status
docker-compose ps

# Resource usage
docker stats

# Inspect specific container
docker inspect aiportfolio-backend
docker inspect aiportfolio-frontend
docker inspect aiportfolio-agent
```

### Database Debugging

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U aiportfolio -d aiportfolio

# Inside psql:
\dt                           # List tables
\d portfolio_roadmapsection   # Describe table
SELECT COUNT(*) FROM portfolio_learningentry;  # Count entries
\q                            # Quit

# Check database size
docker-compose exec postgres psql -U aiportfolio -d aiportfolio -c "SELECT pg_size_pretty(pg_database_size('aiportfolio'));"
```

### View Application Logs

```bash
# All logs (last 100 lines)
docker-compose logs --tail=100

# Follow logs in real-time
docker-compose logs -f

# Backend logs only
docker-compose logs -f backend

# Frontend logs only
docker-compose logs -f frontend

# Search for errors
docker-compose logs | grep -i error
docker-compose logs | grep -i exception
```

### Network Debugging

```bash
# Check open ports
sudo netstat -tulpn | grep LISTEN

# Check iptables rules
sudo iptables -L -n -v

# Test internal connectivity
docker-compose exec backend ping postgres
docker-compose exec backend curl http://frontend:3000
```

---

## 🛠️ Maintenance Commands

### Clean Up Docker Resources

```bash
# Remove stopped containers
docker-compose down

# Remove unused images
docker image prune -a

# Remove all unused resources (BE CAREFUL!)
docker system prune -a --volumes

# Clean up old Docker images (safe)
docker system prune -a --filter "until=72h"
```

### Update Dependencies

```bash
# Backend (Python packages)
cd backend
pip list --outdated
pip install --upgrade package_name
pip freeze > requirements.txt

# Frontend (npm packages)
cd frontend
npm outdated
npm update
npm audit fix
```

### SSL Certificate Renewal

```bash
# Auto-renewal is set up via cron, but to manually renew:
sudo certbot renew --dry-run  # Test renewal
sudo certbot renew            # Actual renewal
sudo systemctl reload nginx   # Apply new certificate
```

### Database Maintenance

```bash
# Vacuum database (optimize)
docker-compose exec postgres psql -U aiportfolio -d aiportfolio -c "VACUUM ANALYZE;"

# Check database statistics
docker-compose exec postgres psql -U aiportfolio -d aiportfolio -c "SELECT schemaname, tablename, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;"

# Create scheduled backups (add to crontab)
crontab -e
# Add: 0 2 * * * cd ~/ai-portfolio && docker-compose exec -T postgres pg_dump -U aiportfolio aiportfolio > ~/backups/daily-$(date +\%Y\%m\%d).sql
```

---

## 📊 Monitoring Commands

### Server Resources

```bash
# CPU and memory usage
htop

# Disk usage
df -h
du -sh ~/ai-portfolio/*

# Docker resource usage
docker stats --no-stream

# Check for OOM (Out of Memory) errors
dmesg | grep -i "out of memory"
```

### Application Metrics

```bash
# Request count (nginx logs)
sudo tail -100 /var/log/nginx/access.log

# Error count (nginx logs)
sudo tail -100 /var/log/nginx/error.log

# Django errors (if DEBUG=False)
docker-compose exec backend tail -100 /var/log/django.log

# Count requests by status code
sudo awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn
```

---

## 🚨 Emergency Procedures

### Site is Down - Quick Fix

```bash
# 1. SSH to server
ssh -i C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key ubuntu@${OCI_HOST}

# 2. Check container status
cd ~/ai-portfolio
docker-compose ps

# 3. Restart all services
docker-compose restart

# 4. If that doesn't work, full restart
docker-compose down
docker-compose up -d

# 5. Check logs for errors
docker-compose logs --tail=50
```

### Rollback to Previous Version

```bash
# 1. SSH to server
cd ~/ai-portfolio

# 2. View commit history
git log --oneline -10

# 3. Rollback to specific commit
git checkout <commit-hash>

# 4. Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# 5. Verify site is working
curl http://localhost:3000
```

### Restore Database from Backup

```bash
# 1. List available backups
ls -lh ~/backups/

# 2. Stop backend to prevent writes
docker-compose stop backend agent

# 3. Restore database
docker-compose exec -T postgres psql -U aiportfolio aiportfolio < ~/backups/backup-20251209-143022.sql

# 4. Restart services
docker-compose up -d

# 5. Verify data
docker-compose exec postgres psql -U aiportfolio -d aiportfolio -c "SELECT COUNT(*) FROM portfolio_learningentry;"
```

### SSL Certificate Issues

```bash
# Check certificate expiry
echo | openssl s_client -servername wwwportfolio.henrihaapala.com -connect ${OCI_HOST}:443 2>/dev/null | openssl x509 -noout -dates

# Force renewal
sudo certbot renew --force-renewal
sudo systemctl reload nginx

# Check nginx configuration
sudo nginx -t
```

---

## 🔐 Security Commands

### Check for Failed Login Attempts

```bash
# View failed SSH attempts
sudo grep "Failed password" /var/log/auth.log | tail -20

# View successful logins
last -20
```

### Update System Packages

```bash
# Update Ubuntu packages
sudo apt update
sudo apt upgrade -y

# Update Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
```

### Firewall Status

```bash
# Check iptables rules
sudo iptables -L -n -v

# Check open ports
sudo ss -tulpn | grep LISTEN

# Add new firewall rule (example)
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo netfilter-persistent save
```

---

## 📝 GitHub Actions Commands

### Trigger Manual Deployment

1. Go to: https://github.com/HenriHaapala/ai-experiments-journey/actions
2. Select "Deploy to Oracle Cloud"
3. Click "Run workflow" → Select branch → "Run workflow"

### View Recent Deployments

```bash
# Using GitHub CLI (if installed)
gh run list --workflow=deploy.yml --limit 5

# View specific run logs
gh run view <run-id> --log
```

### Cancel Running Deployment

1. Go to: https://github.com/HenriHaapala/ai-experiments-journey/actions
2. Click on the running workflow
3. Click "Cancel workflow"

---

## 🎯 Common Workflows

### Deploy New Feature

```bash
# 1. Make changes locally
cd c:\ai-portfolio
# ... make changes ...

# 2. Test locally
docker-compose build
docker-compose up -d
# Test at http://localhost:3000

# 3. Commit and push
git add .
git commit -m "Add new feature"
git push origin main

# 4. Monitor deployment
# Go to: https://github.com/HenriHaapala/ai-experiments-journey/actions

# 5. Verify live site (wait ~10 minutes)
# Visit: https://wwwportfolio.henrihaapala.com
```

### Fix Production Bug (Hotfix)

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-bug

# 2. Fix the bug
# ... make changes ...

# 3. Test locally
docker-compose build
docker-compose up -d

# 4. Push and merge to main
git add .
git commit -m "Fix critical bug"
git push origin hotfix/critical-bug

# 5. Create PR and merge on GitHub
# OR merge directly to main if urgent:
git checkout main
git merge hotfix/critical-bug
git push origin main

# 6. Monitor deployment
```

### Update Production Environment Variables

```bash
# 1. SSH to server
ssh -i C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key ubuntu@${OCI_HOST}

# 2. Edit .env file
cd ~/ai-portfolio
nano .env

# 3. Update variables
# Example: Change COHERE_API_KEY=new_key

# 4. Restart affected services
docker-compose restart backend agent

# 5. Verify changes
docker-compose exec backend env | grep COHERE_API_KEY
```

---

## 📞 Support Information

### Useful Links

- **Live Site:** https://wwwportfolio.henrihaapala.com
- **GitHub Repo:** https://github.com/HenriHaapala/ai-experiments-journey
- **GitHub Actions:** https://github.com/HenriHaapala/ai-experiments-journey/actions
- **Oracle Cloud Console:** https://cloud.oracle.com/

### Server Details

- **IP:** ${OCI_HOST}
- **Domain:** wwwportfolio.henrihaapala.com
- **OS:** Ubuntu 22.04 LTS
- **Instance:** VM.Standard.A1.Flex (4 OCPUs, 24 GB RAM)

### Service Ports

| Service | Internal Port | External URL |
|---------|---------------|--------------|
| Frontend | 3000 | https://wwwportfolio.henrihaapala.com |
| Backend | 8000 | https://wwwportfolio.henrihaapala.com/api/ |
| Agent | 8001 | https://wwwportfolio.henrihaapala.com/agent/ |
| Adminer | 8080 | https://wwwportfolio.henrihaapala.com/adminer/ |
| PostgreSQL | 5432 | Internal only |
| Redis | 6379 | Internal only |

---

## ✅ Health Check Checklist

Before considering deployment successful, verify:

```bash
# 1. All containers running
docker-compose ps
# Should show: postgres, backend, frontend, agent, redis, adminer (all Up)

# 2. Health endpoints respond
curl -f https://wwwportfolio.henrihaapala.com/api/health/
curl -f https://wwwportfolio.henrihaapala.com/agent/health
curl -f https://wwwportfolio.henrihaapala.com

# 3. SSL certificate valid
curl -vI https://wwwportfolio.henrihaapala.com 2>&1 | grep "subject:"

# 4. No errors in logs (last 50 lines)
docker-compose logs --tail=50 | grep -i error

# 5. Database accessible
docker-compose exec postgres psql -U aiportfolio -d aiportfolio -c "SELECT 1;"

# 6. Disk space available (>5GB free)
df -h | grep sda1
```

**All checks pass? ✅ Deployment successful!**
