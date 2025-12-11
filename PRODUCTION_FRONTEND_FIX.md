# Production Frontend API Fix

## Issue
Frontend was built with `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`, causing "Failed to fetch" errors in production because:
- Next.js bakes environment variables into the JavaScript bundle at build time
- Browser tries to fetch from `localhost:8000` which doesn't exist on user's machine

## Solution
Updated `docker-compose.yml` to use environment variable for API URL, allowing different values for local vs production.

## Deployment Steps (On Production Server)

### 1. Update Environment Variable

Add this line to your `.env` file on the production server:

```bash
NEXT_PUBLIC_API_BASE_URL=https://wwwportfolio.henrihaapala.com
```

### 2. Pull Latest Code

```bash
cd ~/ai-portfolio
git pull origin main
```

### 3. Rebuild Frontend Container

The frontend needs to be rebuilt because environment variables are baked in at build time:

```bash
# Stop frontend container
docker-compose stop frontend

# Remove old frontend container and image
docker-compose rm -f frontend
docker rmi ai-portfolio-frontend || true

# Rebuild with production API URL
docker-compose build frontend

# Start all services
docker-compose up -d
```

### 4. Verify Fix

```bash
# Check container logs
docker-compose logs -f frontend

# Test from browser
# Navigate to: https://wwwportfolio.henrihaapala.com
# Should see: "Backend health: ok"
# Chat should work without "Failed to fetch" errors
```

## Alternative: Quick Deploy Script

Create a file `deploy-frontend.sh` on your production server:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying frontend with production API URL..."

# Pull latest code
git pull origin main

# Rebuild frontend with production URL
docker-compose stop frontend
docker-compose rm -f frontend
docker rmi ai-portfolio-frontend || true
docker-compose build frontend
docker-compose up -d

echo "✅ Frontend deployed successfully!"
echo "🌐 Visit: https://wwwportfolio.henrihaapala.com"
```

Make it executable and run:

```bash
chmod +x deploy-frontend.sh
./deploy-frontend.sh
```

## Local Development (No Changes Needed)

Local development continues to work as before:
- `.env` uses `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` (default)
- Docker Compose automatically uses this value

## Why This Happened

1. **Next.js Environment Variables**: `NEXT_PUBLIC_*` variables are embedded in the client-side JavaScript bundle at build time, not runtime
2. **Docker Build Context**: The production container was built with the default localhost value
3. **Client-Side Fetching**: Browser makes requests from user's machine, not from the Docker container

## Technical Details

**Before (Broken in Production)**:
```yaml
frontend:
  build:
    args:
      NEXT_PUBLIC_API_BASE_URL: http://localhost:8000  # Hardcoded
```

**After (Works in Production)**:
```yaml
frontend:
  build:
    args:
      NEXT_PUBLIC_API_BASE_URL: ${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000}  # From .env
```

**Production `.env`**:
```bash
NEXT_PUBLIC_API_BASE_URL=https://wwwportfolio.henrihaapala.com
```

## Testing Checklist

After deployment, verify:
- [ ] Homepage loads without errors
- [ ] "Backend health: ok" (not "Backend health: error")
- [ ] Chat input accepts text
- [ ] Sending message returns AI response (not "Failed to fetch")
- [ ] Browser console shows no CORS or network errors
- [ ] API requests go to `https://wwwportfolio.henrihaapala.com/api/` (check Network tab)

## Related Files Modified

- [docker-compose.yml](docker-compose.yml) - Added `${NEXT_PUBLIC_API_BASE_URL}` variable
- [.env.example](.env.example) - Added documentation for `NEXT_PUBLIC_API_BASE_URL`
- [PRODUCTION_FRONTEND_FIX.md](PRODUCTION_FRONTEND_FIX.md) - This file

## Next Steps

After this fix is deployed:
1. Test all frontend functionality
2. Verify roadmap page loads data
3. Test chat functionality end-to-end
4. Consider adding automated tests (see [TESTING_TODO.md](TESTING_TODO.md))
