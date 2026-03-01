# nginx Deployment Strategy

## Question: Should nginx be in Docker or installed on the instance?

**TL;DR**: For this project, install nginx **on the Oracle Cloud instance** (not in Docker). No changes needed to docker-compose.yml or local development setup.

## Recommended Approach: Cloud-Only nginx

### Architecture

**Production (Oracle Cloud)**:
```
Internet (HTTPS:443)
    ↓
nginx (on Ubuntu, outside Docker)
  - SSL termination (Let's Encrypt)
  - Reverse proxy
  - Static file serving
    ↓
Docker Containers (internal HTTP)
  - frontend:3000
  - backend:8000
  - agent:8001
  - adminer:8080
```

**Local Development**:
```
Your Computer
    ↓
docker-compose up
    ↓
Access directly:
  - http://localhost:3000 (frontend)
  - http://localhost:8000 (backend)
  - http://localhost:8001 (agent)
```

### Why This Approach?

✅ **Simplicity**:
- No changes to docker-compose.yml
- No changes to local development workflow
- nginx only exists where SSL is needed (production)

✅ **Separation of Concerns**:
- nginx handles SSL/TLS (infrastructure concern)
- Docker handles application (portable across environments)
- Clear boundary between "infrastructure" and "application"

✅ **Flexibility**:
- Easy to swap nginx for Traefik/Caddy later
- Can move to managed load balancer (AWS ALB, etc.) without changing Docker setup
- Let's Encrypt renewal doesn't require container rebuilds

✅ **Performance**:
- nginx runs natively on host (not containerized overhead)
- Direct access to host network stack
- Easier to tune for production

✅ **Easier SSL Management**:
- Certbot works directly with nginx
- No volume mounts for certificates
- Auto-renewal is simpler

### What This Means for Your Workflow

**Local Development** (No changes needed):
```bash
# Still works exactly as before
docker-compose up -d

# Access services directly
http://localhost:3000  # Frontend
http://localhost:8000  # Backend
```

**Production Deployment**:
```bash
# On Oracle Cloud instance

# 1. Install nginx (one-time)
sudo apt install nginx certbot python3-certbot-nginx

# 2. Configure nginx (one-time)
sudo nano /etc/nginx/sites-available/aiportfolio

# 3. Get SSL cert (one-time)
sudo certbot --nginx -d wwwportfolio.henrihaapala.com

# 4. Deploy Docker containers (same as always)
docker-compose up -d
```

**Result**:
- Local: HTTP, no nginx, direct access
- Production: HTTPS, nginx reverse proxy, clean URLs

## Alternative: nginx in Docker (Not Recommended for This Project)

If you wanted nginx in Docker, you would need:

### docker-compose.yml changes:
```yaml
services:
  # ... existing services ...

  nginx:
    image: nginx:alpine
    container_name: aiportfolio-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - certbot_certs:/etc/letsencrypt
    depends_on:
      - frontend
      - backend
      - agent

  certbot:
    image: certbot/certbot
    container_name: aiportfolio-certbot
    volumes:
      - certbot_certs:/etc/letsencrypt
      - certbot_www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  certbot_certs:
  certbot_www:
```

### Problems with this approach:
❌ Complicates local development (need to access through nginx locally)
❌ SSL certificate management in containers is complex
❌ Certbot renewal requires container orchestration
❌ Need to rebuild/restart nginx container for config changes
❌ Volume mounts for certificates are tricky
❌ Harder to debug SSL issues

### When nginx-in-Docker makes sense:
- Kubernetes deployments (everything is containerized)
- Multi-cloud portability is critical
- You want identical local and production environments
- You're using Docker Swarm or similar orchestration
- You have complex routing that benefits from container networking

## Summary Table

| Aspect | nginx on Host | nginx in Docker |
|--------|---------------|-----------------|
| **Local Dev** | No nginx needed, direct access | nginx required, adds complexity |
| **SSL Setup** | Easy (certbot --nginx) | Complex (volume mounts, renewal) |
| **Config Changes** | `sudo systemctl reload nginx` | Rebuild container |
| **Production** | Standard Linux setup | Container overhead |
| **Debugging** | Standard nginx logs | Container logs |
| **Portability** | Instance-specific | Fully portable |
| **Complexity** | Low | Medium-High |
| **Recommended for** | Most deployments | Kubernetes, orchestration |

## Recommendation for This Project

**Use nginx on the Oracle Cloud instance** (not in Docker):

1. ✅ Follow [HTTPS_SETUP.md](HTTPS_SETUP.md) to install nginx on Ubuntu
2. ✅ Keep docker-compose.yml unchanged
3. ✅ Local development stays simple (no nginx)
4. ✅ Production gets HTTPS via instance-level nginx

## Files to Update

### ✅ Already Updated:
- `CLAUDE.md` - Architecture section updated with nginx info
- `HTTPS_SETUP.md` - Complete step-by-step guide

### ❌ No Changes Needed:
- `docker-compose.yml` - Stays the same
- `backend/Dockerfile` - No changes
- `frontend/Dockerfile` - No changes
- `.env` files - Only add HTTPS-related Django settings

### ✅ To Add (Optional):
- `nginx/README.md` - Quick reference for nginx commands
- `.github/workflows/deploy.yml` - CI/CD pipeline (future)

## CI/CD Considerations (Future)

When you set up automated deployments:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Oracle Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: SSH to instance
        run: |
          ssh ubuntu@130.61.72.122 << 'EOF'
            cd /home/ubuntu/ai-portfolio
            git pull
            docker-compose down
            docker-compose up -d --build
            sudo systemctl reload nginx
          EOF
```

nginx config is **not** part of the Git repo - it lives on the instance.

**Why?**
- nginx config contains instance-specific details (domain, paths)
- SSL certificates are instance-specific
- Keeps application code separate from infrastructure config

## Next Steps

1. **Now**: Follow HTTPS_SETUP.md to set up nginx on Oracle instance
2. **Today**: Test HTTPS access to your application
3. **Later**: Consider adding nginx config to a separate "infrastructure" repo (optional)
4. **Future**: Add CI/CD pipeline that deploys Docker containers (nginx stays on instance)

---

**Questions?**
- Local dev: Keep using `docker-compose up` as you do now
- Production: nginx installed once on instance, Docker containers updated via git pull + docker-compose
