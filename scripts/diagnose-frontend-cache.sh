#!/bin/bash
# Frontend Cache Diagnostic Script
# Run this on the production server to diagnose why frontend changes aren't showing

set -e

echo "🔍 Frontend Cache Diagnostic Tool"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check nginx configuration
echo "1️⃣ Checking nginx configuration..."
echo ""

NGINX_SITE_CONFIG="/etc/nginx/sites-available/aiportfolio"
if [ -f "$NGINX_SITE_CONFIG" ]; then
    echo "✅ nginx config exists at $NGINX_SITE_CONFIG"

    # Check for cache-control headers in frontend location
    if grep -A 5 "location / {" "$NGINX_SITE_CONFIG" | grep -q "Cache-Control"; then
        echo -e "${GREEN}✅ Cache-Control headers found in frontend location${NC}"
        echo "   Headers configured:"
        grep -A 5 "location / {" "$NGINX_SITE_CONFIG" | grep "Cache-Control\|Pragma\|Expires"
    else
        echo -e "${RED}❌ Cache-Control headers NOT found in frontend location${NC}"
        echo "   This means nginx might be caching frontend responses!"
    fi

    # Check for static asset caching
    if grep -q "location ~\*.*\.(js|css|png" "$NGINX_SITE_CONFIG"; then
        echo -e "${GREEN}✅ Static asset caching configured${NC}"
    else
        echo -e "${YELLOW}⚠️  No separate static asset caching rule${NC}"
    fi
else
    echo -e "${RED}❌ nginx config not found at $NGINX_SITE_CONFIG${NC}"
fi

echo ""

# 2. Check nginx cache directory
echo "2️⃣ Checking nginx cache..."
echo ""

NGINX_CACHE="/var/cache/nginx"
if [ -d "$NGINX_CACHE" ]; then
    CACHE_SIZE=$(du -sh $NGINX_CACHE 2>/dev/null | cut -f1)
    CACHE_FILES=$(find $NGINX_CACHE -type f 2>/dev/null | wc -l)

    if [ "$CACHE_FILES" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  nginx has cached files: $CACHE_SIZE ($CACHE_FILES files)${NC}"
        echo "   Run: sudo rm -rf /var/cache/nginx/* && sudo systemctl reload nginx"
    else
        echo -e "${GREEN}✅ nginx cache is empty${NC}"
    fi
else
    echo "ℹ️  No nginx cache directory (might not be configured)"
fi

echo ""

# 3. Check Docker frontend container
echo "3️⃣ Checking Docker frontend container..."
echo ""

if docker ps | grep -q "aiportfolio-frontend"; then
    echo -e "${GREEN}✅ Frontend container is running${NC}"

    # Get container build time
    CONTAINER_CREATED=$(docker inspect aiportfolio-frontend --format='{{.Created}}' 2>/dev/null)
    echo "   Container created: $CONTAINER_CREATED"

    # Check Next.js build ID inside container
    BUILD_ID=$(docker exec aiportfolio-frontend cat /app/.next/BUILD_ID 2>/dev/null || echo "NOT_FOUND")
    if [ "$BUILD_ID" != "NOT_FOUND" ]; then
        echo "   Next.js Build ID: $BUILD_ID"
    else
        echo -e "${YELLOW}⚠️  Could not read Next.js BUILD_ID${NC}"
    fi

    # Check if .next directory exists and size
    NEXT_SIZE=$(docker exec aiportfolio-frontend du -sh /app/.next 2>/dev/null | cut -f1 || echo "UNKNOWN")
    echo "   .next directory size: $NEXT_SIZE"

else
    echo -e "${RED}❌ Frontend container is NOT running${NC}"
fi

echo ""

# 4. Check Redis (agent service memory)
echo "4️⃣ Checking Redis..."
echo ""

if docker ps | grep -q "aiportfolio-redis"; then
    echo -e "${GREEN}✅ Redis container is running${NC}"

    # Get Redis memory usage
    REDIS_KEYS=$(docker exec aiportfolio-redis redis-cli DBSIZE 2>/dev/null | grep -o '[0-9]*' || echo "0")
    REDIS_MEM=$(docker exec aiportfolio-redis redis-cli INFO memory 2>/dev/null | grep "used_memory_human" | cut -d: -f2 | tr -d '\r' || echo "UNKNOWN")

    echo "   Redis keys: $REDIS_KEYS"
    echo "   Redis memory: $REDIS_MEM"

    if [ "$REDIS_KEYS" -gt 0 ]; then
        echo -e "${YELLOW}   ℹ️  Redis has data (agent conversations)${NC}"
        echo "   To flush: docker exec aiportfolio-redis redis-cli FLUSHALL"
    fi
else
    echo -e "${YELLOW}⚠️  Redis container is NOT running${NC}"
fi

echo ""

# 5. Test actual HTTP headers
echo "5️⃣ Testing actual HTTP headers from frontend..."
echo ""

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "Direct to container (port 3000):"
    curl -sI http://localhost:3000 | grep -i "cache\|expires\|pragma" || echo "   No cache headers"
    echo ""

    echo "Through nginx (port 443 HTTPS):"
    DOMAIN="wwwportfolio.henrihaapala.com"
    curl -skI https://$DOMAIN | grep -i "cache\|expires\|pragma" || echo "   No cache headers"
else
    echo -e "${RED}❌ Frontend not responding on localhost:3000${NC}"
fi

echo ""

# 6. Check environment variables
echo "6️⃣ Checking environment variables..."
echo ""

if [ -f ~/ai-portfolio/.env ]; then
    if grep -q "NEXT_PUBLIC_API_BASE_URL" ~/ai-portfolio/.env; then
        API_URL=$(grep "NEXT_PUBLIC_API_BASE_URL" ~/ai-portfolio/.env | cut -d= -f2)
        echo -e "${GREEN}✅ NEXT_PUBLIC_API_BASE_URL is set${NC}"
        echo "   Value: $API_URL"
    else
        echo -e "${RED}❌ NEXT_PUBLIC_API_BASE_URL not found in .env${NC}"
    fi
else
    echo -e "${RED}❌ .env file not found${NC}"
fi

echo ""

# 7. Summary and Recommendations
echo "📊 SUMMARY & RECOMMENDATIONS"
echo "============================"
echo ""

# Check all issues
ISSUES=0

# Issue 1: nginx cache
if [ -d "$NGINX_CACHE" ] && [ "$(find $NGINX_CACHE -type f 2>/dev/null | wc -l)" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Issue 1: nginx has cached files${NC}"
    echo "   Fix: sudo rm -rf /var/cache/nginx/* && sudo systemctl reload nginx"
    ((ISSUES++))
fi

# Issue 2: Cache headers missing
if ! grep -q "Cache-Control" "$NGINX_SITE_CONFIG" 2>/dev/null; then
    echo -e "${RED}❌ Issue 2: Cache-Control headers missing from nginx config${NC}"
    echo "   Fix: Add no-cache headers to location / block"
    ((ISSUES++))
fi

# Issue 3: Container might be old
CONTAINER_AGE=$(docker inspect aiportfolio-frontend --format='{{.Created}}' 2>/dev/null | cut -d'T' -f1 || echo "UNKNOWN")
CURRENT_DATE=$(date -I)
if [ "$CONTAINER_AGE" != "$CURRENT_DATE" ]; then
    echo -e "${YELLOW}⚠️  Issue 3: Frontend container was built on $CONTAINER_AGE (not today)${NC}"
    echo "   Fix: Run deployment to rebuild: docker-compose down && docker-compose up -d --build --force-recreate"
    ((ISSUES++))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ No issues found! Frontend should be updating correctly.${NC}"
    echo ""
    echo "If changes still not showing, likely causes:"
    echo "1. Browser cache - tell users to hard refresh (Ctrl+Shift+R)"
    echo "2. CDN/proxy cache (if using Cloudflare/similar)"
    echo "3. Changes not committed to Git properly"
else
    echo ""
    echo -e "${RED}Found $ISSUES potential issues. Fix them and redeploy.${NC}"
fi

echo ""
echo "🔧 Quick Fix Commands:"
echo "---------------------"
echo "# Clear nginx cache:"
echo "sudo rm -rf /var/cache/nginx/* && sudo systemctl reload nginx"
echo ""
echo "# Flush Redis (agent conversations):"
echo "docker exec aiportfolio-redis redis-cli FLUSHALL"
echo ""
echo "# Force rebuild frontend:"
echo "cd ~/ai-portfolio"
echo "docker-compose down"
echo "docker-compose build --no-cache frontend"
echo "docker-compose up -d --force-recreate"
echo ""
echo "# Full deployment (recommended):"
echo "cd ~/ai-portfolio && git pull && docker-compose down && docker-compose build --no-cache && docker-compose up -d --force-recreate"
echo ""
