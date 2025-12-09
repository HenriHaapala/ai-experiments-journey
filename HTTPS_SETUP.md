# HTTPS Setup Guide for Oracle Cloud Deployment

## Overview
This guide will help you add SSL/TLS certificates to your AI Portfolio application using nginx and Let's Encrypt (free SSL certificates).

## Prerequisites
- ✅ Oracle Cloud instance running (${OCI_HOST})
- ✅ DNS configured (wwwportfolio.henrihaapala.com → ${OCI_HOST})
- ✅ Docker containers running
- ✅ SSH access to instance

## Step 1: Connect to Your Oracle Instance

```bash
ssh -i C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key ubuntu@${OCI_HOST}
```

## Step 2: Install nginx and Certbot

```bash
# Update package list
sudo apt update

# Install nginx and certbot
sudo apt install -y nginx certbot python3-certbot-nginx

# Verify installation
nginx -v
certbot --version
```

## Step 3: Configure Firewall (Oracle Security List)

**IMPORTANT**: You need to add HTTPS (port 443) to your Oracle Cloud security rules.

### In Oracle Cloud Console:
1. Go to: **Networking → Virtual Cloud Networks → aiportfolio-vcn**
2. Click: **Security Lists → Default Security List**
3. Click: **Add Ingress Rules**
4. Add this rule:

```
Source CIDR: 0.0.0.0/0
IP Protocol: TCP
Destination Port Range: 443
Description: HTTPS traffic
```

### On the Instance (Ubuntu firewall):
```bash
# Allow HTTPS through UFW
sudo ufw allow 443/tcp
sudo ufw allow 'Nginx Full'
sudo ufw status
```

## Step 4: Create nginx Configuration

```bash
# Create nginx config file
sudo nano /etc/nginx/sites-available/aiportfolio
```

**Paste this configuration:**

```nginx
# HTTP server - will be upgraded to HTTPS by certbot
server {
    listen 80;
    listen [::]:80;
    server_name wwwportfolio.henrihaapala.com;

    # Increase buffer sizes for large requests
    client_max_body_size 100M;
    client_body_buffer_size 128k;

    # Frontend (Next.js on port 3000)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Backend API (Django on port 8000)
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers (if needed)
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header Access-Control-Allow-Headers 'Content-Type, Authorization' always;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Agent Service (FastAPI on port 8001)
    location /agent/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Adminer (Database admin on port 8080)
    location /adminer/ {
        proxy_pass http://localhost:8080/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (if needed)
    location /static/ {
        alias /home/ubuntu/ai-experiments-journey/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (if needed)
    location /media/ {
        alias /home/ubuntu/ai-experiments-journey/backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

## Step 5: Enable the Site

```bash
# Create symlink to enable the site
sudo ln -s /etc/nginx/sites-available/aiportfolio /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
sudo systemctl status nginx
```

## Step 6: Get SSL Certificate from Let's Encrypt

```bash
# Run certbot to get SSL certificate
sudo certbot --nginx -d wwwportfolio.henrihaapala.com

# Follow the prompts:
# 1. Enter your email address (for renewal notifications)
# 2. Agree to Terms of Service (Y)
# 3. Share email with EFF (optional - Y or N)
# 4. Choose option 2: Redirect HTTP to HTTPS (recommended)
```

**Certbot will automatically:**
- Generate SSL certificates
- Modify your nginx config to use HTTPS
- Set up automatic HTTP → HTTPS redirect
- Configure auto-renewal

## Step 7: Verify SSL Certificate

```bash
# Check certificate status
sudo certbot certificates

# Test auto-renewal (dry run)
sudo certbot renew --dry-run
```

## Step 8: Update Django Settings

```bash
# Edit .env file to add HTTPS settings
cd /home/ubuntu/ai-experiments-journey
nano .env
```

**Add/Update these lines:**
```bash
# Existing ALLOWED_HOSTS (update to remove ports)
ALLOWED_HOSTS=wwwportfolio.henrihaapala.com,${OCI_HOST},localhost,127.0.0.1

# Add these new settings for HTTPS
CSRF_TRUSTED_ORIGINS=https://wwwportfolio.henrihaapala.com
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
USE_X_FORWARDED_HOST=True
SECURE_SSL_REDIRECT=False  # nginx handles redirect
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Save and exit**: `Ctrl+X`, `Y`, `Enter`

## Step 9: Update Frontend Environment (if needed)

```bash
# If you have a .env.local in frontend, update API URL
cd /home/ubuntu/ai-experiments-journey/frontend
nano .env.local
```

**Add:**
```bash
NEXT_PUBLIC_API_URL=https://wwwportfolio.henrihaapala.com/api
```

## Step 10: Restart Docker Services

```bash
# Go back to project root
cd /home/ubuntu/ai-experiments-journey

# Restart containers to apply new environment variables
docker-compose down
docker-compose up -d

# Check all containers are running
docker-compose ps

# Check logs for any errors
docker-compose logs backend
docker-compose logs frontend
```

## Step 11: Test HTTPS Access

### From your local machine:

```bash
# Test HTTPS redirect
curl -I http://wwwportfolio.henrihaapala.com

# Should return 301 redirect to https://

# Test HTTPS frontend
curl -I https://wwwportfolio.henrihaapala.com

# Test HTTPS API
curl https://wwwportfolio.henrihaapala.com/api/health/
```

### In your browser:
1. **Frontend**: https://wwwportfolio.henrihaapala.com
2. **Backend API**: https://wwwportfolio.henrihaapala.com/api/health/
3. **Agent Service**: https://wwwportfolio.henrihaapala.com/agent/health
4. **Adminer** (DB Admin): https://wwwportfolio.henrihaapala.com/adminer/

**Check for:**
- 🔒 Padlock icon in browser (secure connection)
- ✅ Valid certificate (click padlock to verify)
- ✅ No mixed content warnings

## Step 12: Set Up Auto-Renewal (Already Done by Certbot)

Certbot automatically creates a systemd timer for certificate renewal.

```bash
# Verify auto-renewal is set up
sudo systemctl list-timers | grep certbot

# Should show: certbot.timer

# Check renewal configuration
sudo cat /etc/letsencrypt/renewal/wwwportfolio.henrihaapala.com.conf
```

Certificates will auto-renew 30 days before expiration (Let's Encrypt certs are valid for 90 days).

## Troubleshooting

### Issue: nginx fails to start
```bash
# Check syntax
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
```

### Issue: Certbot fails
```bash
# Make sure port 80 is accessible
curl -I http://wwwportfolio.henrihaapala.com

# Check certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Try manual verification
sudo certbot certonly --standalone -d wwwportfolio.henrihaapala.com
```

### Issue: 502 Bad Gateway
```bash
# Check if Docker containers are running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Verify ports are listening
sudo netstat -tlnp | grep -E '(3000|8000|8001)'
```

### Issue: Mixed content warnings
- Make sure all API calls in frontend use relative URLs or `https://`
- Check browser console for blocked resources

### Issue: CORS errors
- Verify `CSRF_TRUSTED_ORIGINS` in Django settings
- Check nginx CORS headers in `/etc/nginx/sites-available/aiportfolio`

## Security Checklist

After setup, verify:
- ✅ HTTP redirects to HTTPS
- ✅ SSL certificate is valid (not expired)
- ✅ Grade A on [SSL Labs Test](https://www.ssllabs.com/ssltest/)
- ✅ HSTS header is set
- ✅ No mixed content warnings
- ✅ Cookies are secure (Session/CSRF cookies)

## Useful Commands

```bash
# Reload nginx after config changes
sudo nginx -t && sudo systemctl reload nginx

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check certificate expiration
sudo certbot certificates

# Force certificate renewal (testing)
sudo certbot renew --force-renewal

# Restart nginx
sudo systemctl restart nginx

# Check nginx status
sudo systemctl status nginx
```

## Final URLs (After HTTPS Setup)

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | https://wwwportfolio.henrihaapala.com | Main application |
| Backend API | https://wwwportfolio.henrihaapala.com/api/ | REST API endpoints |
| API Health | https://wwwportfolio.henrihaapala.com/api/health/ | Backend health check |
| Agent Service | https://wwwportfolio.henrihaapala.com/agent/ | AI assistant service |
| Database Admin | https://wwwportfolio.henrihaapala.com/adminer/ | Adminer (PostgreSQL UI) |

## Cost Impact

- **Let's Encrypt SSL**: FREE (forever)
- **nginx**: FREE (open source)
- **Auto-renewal**: Automated, no maintenance cost
- **Oracle A1.Flex instance**: Still FREE (part of Always Free tier)

**Total additional cost: €0**

## Next Steps

After HTTPS is working:
1. ✅ Test all functionality (frontend, API, agent)
2. ✅ Update any hardcoded HTTP URLs in your code
3. ✅ Test on multiple browsers
4. ✅ Add security headers (optional but recommended)
5. ✅ Consider implementing instance scheduler for cost optimization

---

**Need Help?**
- Check logs: `sudo tail -f /var/log/nginx/error.log`
- Test SSL: https://www.ssllabs.com/ssltest/
- Certbot docs: https://certbot.eff.org/
