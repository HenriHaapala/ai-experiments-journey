# Agent Service Routing Fix

## Problem

**Local development**: Agent service works at `http://localhost:8001/health` ✅
**Production**: nginx forwards `https://wwwportfolio.henrihaapala.com/agent/health` → `http://localhost:8001/agent/health` ❌

The issue: Agent service listens on `/health`, but nginx sends `/agent/health` (with prefix).

## Solution: Configure nginx to Strip `/agent` Prefix

### Why This Approach?
- ✅ Keeps local development unchanged (`http://localhost:8001/health`)
- ✅ Production works through nginx path rewriting
- ✅ No need to maintain dual endpoints in agent code
- ✅ Follows standard nginx proxy pattern

### nginx Configuration Fix

**File on server**: `/etc/nginx/sites-available/aiportfolio`

**Current configuration** (broken):
```nginx
# Agent service (port 8001)
location /agent/ {
    proxy_pass http://localhost:8001/agent/;  # ❌ Forwards /agent/health → http://localhost:8001/agent/health
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

**Fixed configuration** (strips `/agent` prefix):
```nginx
# Agent service (port 8001) - Strip /agent prefix
location /agent/ {
    proxy_pass http://localhost:8001/;  # ✅ Strips prefix: /agent/health → http://localhost:8001/health
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

**Key change**: `proxy_pass http://localhost:8001/agent/;` → `proxy_pass http://localhost:8001/;`

The trailing `/` in `proxy_pass` tells nginx to strip the matched location prefix.

## Implementation Steps

### 1. SSH to Production Server

```bash
# Use connection details from .env.production
ssh ubuntu@${OCI_HOST}
cd ~/ai-portfolio
```

### 2. Edit nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/aiportfolio
```

Find the `location /agent/` block (around line 40-50) and change:
```nginx
proxy_pass http://localhost:8001/agent/;
```
to:
```nginx
proxy_pass http://localhost:8001/;
```

Save and exit (Ctrl+X, Y, Enter).

### 3. Test nginx Configuration

```bash
sudo nginx -t
```

Expected output:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 4. Reload nginx

```bash
sudo systemctl reload nginx
```

### 5. Verify Fix

```bash
# Test agent health endpoint
curl https://wwwportfolio.henrihaapala.com/agent/health

# Expected output:
# {"status":"healthy","timestamp":"2025-12-10T...","service":"ai-portfolio-agent","version":"1.0.0"}
```

## Verification Checklist

After applying the fix:

- [ ] nginx configuration test passes (`sudo nginx -t`)
- [ ] nginx reloaded successfully (`sudo systemctl reload nginx`)
- [ ] Agent health endpoint returns 200 OK: `curl https://wwwportfolio.henrihaapala.com/agent/health`
- [ ] Local development still works: `curl http://localhost:8001/health`
- [ ] AI chat page works: https://wwwportfolio.henrihaapala.com/chat

## Alternative nginx Configurations

### Option 2: Using rewrite directive
```nginx
location /agent/ {
    rewrite ^/agent(.*)$ $1 break;
    proxy_pass http://localhost:8001;
    # ... other headers
}
```

### Option 3: Using regex location
```nginx
location ~ ^/agent/(.*) {
    proxy_pass http://localhost:8001/$1;
    # ... other headers
}
```

**Recommendation**: Use Option 1 (trailing slash in proxy_pass) - simplest and most reliable.

## Troubleshooting

### Issue: Still getting 502 Bad Gateway

**Check agent service is running:**
```bash
cd ~/ai-portfolio
docker-compose ps agent
```

Expected: `Up (healthy)`

**Check agent logs:**
```bash
docker-compose logs agent --tail=50
```

**Test agent directly (bypassing nginx):**
```bash
curl http://localhost:8001/health
```

If this works but nginx doesn't, the issue is nginx configuration.

### Issue: nginx test fails

```bash
sudo nginx -t
```

If syntax error, double-check:
- No missing semicolons
- Matching braces `{}`
- Proper indentation

### Issue: Permission denied

```bash
# View nginx error log
sudo tail -50 /var/log/nginx/error.log

# Check nginx user can access the socket
sudo systemctl status nginx
```

## Related Files

- [SESSION_SUMMARY_DEC10.md](SESSION_SUMMARY_DEC10.md) - Root cause analysis
- [HTTPS_SETUP.md](HTTPS_SETUP.md) - Full nginx configuration
- [agent_service/api.py](agent_service/api.py) - Agent service endpoints

## Summary

**Before fix:**
- Local: `http://localhost:8001/health` ✅
- Production: `https://wwwportfolio.henrihaapala.com/agent/health` ❌ 502

**After fix:**
- Local: `http://localhost:8001/health` ✅ (unchanged)
- Production: `https://wwwportfolio.henrihaapala.com/agent/health` ✅ (nginx strips `/agent`)

**Implementation time**: 5 minutes
**Downtime**: None (nginx reload is instant)

---

**Created**: December 10, 2025
**Status**: Ready to implement
**Priority**: High (blocks AI chat functionality)
