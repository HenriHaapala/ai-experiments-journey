# HTTPS Setup Checklist

Copy-paste these commands into your SSH session on Oracle Cloud.

## Prerequisites
- ✅ SSH into instance: `ssh -i C:\AIandClaude\oraclecloud\ssh-key-2025-12-09.key ubuntu@130.61.72.122`
- ✅ Docker containers running: `docker-compose ps`

## Step-by-Step Commands

### 1. Install nginx and Certbot
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
nginx -v  # Verify installation
```

### 2. Add HTTPS to Oracle Cloud Security List

**Do this in Oracle Cloud Console (web browser):**
1. Go to: **Networking → Virtual Cloud Networks → aiportfolio-vcn**
2. Click: **Security Lists → Default Security List**
3. Click: **Add Ingress Rules**
4. Fill in:
   - Source CIDR: `0.0.0.0/0`
   - IP Protocol: `TCP`
   - Destination Port: `443`
   - Description: `HTTPS traffic`
5. Click **Add Ingress Rules**

### 3. Configure Ubuntu Firewall
```bash
sudo ufw allow 443/tcp
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### 4. Create nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/aiportfolio
```

**Paste this entire configuration** (Ctrl+Shift+V in PuTTY, or right-click in Windows Terminal):

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name wwwportfolio.henrihaapala.com;

    client_max_body_size 100M;
    client_body_buffer_size 128k;

    # Frontend (Next.js)
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
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Agent Service
    location /agent/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Adminer (Database admin)
    location /adminer/ {
        proxy_pass http://localhost:8080/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /home/ubuntu/ai-portfolio/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/ubuntu/ai-portfolio/backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### 5. Enable the Site
```bash
sudo ln -s /etc/nginx/sites-available/aiportfolio /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
sudo systemctl status nginx
```

**Expected output**: "nginx.service - A high performance web server..."

### 6. Get SSL Certificate
```bash
sudo certbot --nginx -d wwwportfolio.henrihaapala.com
```

**Follow prompts**:
1. Enter your email: `[your-email@example.com]`
2. Agree to Terms of Service: `Y`
3. Share email with EFF: `N` (optional)
4. Choose: `2` (Redirect HTTP to HTTPS)

**Expected output**: "Successfully deployed certificate!"

### 7. Verify SSL Certificate
```bash
sudo certbot certificates
```

**Expected output**: Should show certificate for wwwportfolio.henrihaapala.com

### 8. Update Django Settings
```bash
cd /home/ubuntu/ai-portfolio
nano .env
```

**Add these lines to the end of the file**:
```bash
CSRF_TRUSTED_ORIGINS=https://wwwportfolio.henrihaapala.com
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
USE_X_FORWARDED_HOST=True
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Update ALLOWED_HOSTS** (find this line and update it):
```bash
ALLOWED_HOSTS=wwwportfolio.henrihaapala.com,130.61.72.122,localhost,127.0.0.1
```

**Save:** `Ctrl+X`, `Y`, `Enter`

### 9. Restart Docker Containers
```bash
cd /home/ubuntu/ai-portfolio
docker-compose down
docker-compose up -d
docker-compose ps  # Verify all containers are running
```

**Expected output**: All 6 containers should show "Up"

### 10. Test HTTPS Access

**From your SSH session**:
```bash
# Test HTTP → HTTPS redirect
curl -I http://wwwportfolio.henrihaapala.com

# Test HTTPS frontend
curl -I https://wwwportfolio.henrihaapala.com

# Test HTTPS API
curl https://wwwportfolio.henrihaapala.com/api/health/
```

**From your browser** (on your Windows machine):
1. Open: https://wwwportfolio.henrihaapala.com
2. Check for 🔒 padlock icon
3. Click padlock → "Connection is secure"
4. Test API: https://wwwportfolio.henrihaapala.com/api/health/
5. Test Agent: https://wwwportfolio.henrihaapala.com/agent/health

## Success Checklist

- ✅ nginx installed and running
- ✅ Port 443 open in Oracle Cloud security list
- ✅ SSL certificate obtained from Let's Encrypt
- ✅ HTTP redirects to HTTPS
- ✅ Padlock icon shows in browser
- ✅ Frontend accessible without port number
- ✅ API accessible at /api/
- ✅ No mixed content warnings

## Troubleshooting

### Problem: nginx test fails
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### Problem: Certbot fails
```bash
# Check if port 80 is accessible
curl -I http://wwwportfolio.henrihaapala.com

# Check certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### Problem: 502 Bad Gateway
```bash
# Check Docker containers
docker-compose ps

# Check backend logs
docker-compose logs backend
docker-compose logs frontend

# Verify ports are listening
sudo netstat -tlnp | grep -E '(3000|8000|8001)'
```

### Problem: Certificate renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Force renewal (if needed)
sudo certbot renew --force-renewal
```

## Useful Commands

```bash
# Reload nginx after config changes
sudo nginx -t && sudo systemctl reload nginx

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check certificate status
sudo certbot certificates

# Restart nginx
sudo systemctl restart nginx

# Check Docker status
docker-compose ps
docker-compose logs -f
```

## Final URLs (After Setup)

| Service | URL |
|---------|-----|
| **Frontend** | https://wwwportfolio.henrihaapala.com |
| **Backend API** | https://wwwportfolio.henrihaapala.com/api/ |
| **API Health** | https://wwwportfolio.henrihaapala.com/api/health/ |
| **Agent Service** | https://wwwportfolio.henrihaapala.com/agent/ |
| **Database Admin** | https://wwwportfolio.henrihaapala.com/adminer/ |

## Cost

- nginx: **FREE**
- Let's Encrypt SSL: **FREE**
- Oracle A1.Flex instance: **FREE**
- **Total: €0/month**

---

**Estimated time**: 15-20 minutes

**Next step after HTTPS works**: Debug agent service (if needed)
