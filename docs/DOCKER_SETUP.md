# Docker Setup Guide

## Security First! 🔒

**CRITICAL:** Never commit your `.env` file with real API keys to git!

## Quick Start

### 1. Copy the environment template
```bash
cp .env.example .env
```

### 2. Edit `.env` with your actual secrets
Open `.env` and replace all placeholder values:

```env
# Required - Get from your existing backend/.env
COHERE_API_KEY=your_actual_cohere_key
GROQ_API_KEY=your_actual_groq_key

# Required - Generate a new Django secret key
DJANGO_SECRET_KEY=your-long-random-secret-key-here

# Required - Set a secure database password
DB_PASSWORD=your_secure_password_123

# Optional - these have defaults
DB_NAME=ai_portfolio_dev
DB_USER=ai_portfolio_user
```

### 3. Build and start the stack
```bash
docker-compose up --build
```

### 4. Verify services are running

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/health/
- Adminer (DB): http://localhost:8080
- PostgreSQL: localhost:5432

## Services

| Service | Port | Description |
|---------|------|-------------|
| postgres | 5432 | PostgreSQL 16 + pgvector |
| backend | 8000 | Django REST API |
| frontend | 3000 | Next.js portfolio |
| adminer | 8080 | Database admin UI |

## Common Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run Django management commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py build_knowledge_index
```

## Troubleshooting

**Database connection failed:**
- Wait for postgres healthcheck to complete (~10 seconds)
- Check DB_PASSWORD matches in .env

**Port already in use:**
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Backend on 8001 instead of 8000
```

**Frontend can't connect to backend:**
- Verify NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
- Check backend is healthy: curl http://localhost:8000/api/health/

## Security Checklist

✅ `.env` is in `.gitignore`
✅ `.env.example` has no real secrets
✅ Never commit API keys
✅ Use strong DB_PASSWORD
✅ Rotate DJANGO_SECRET_KEY for production

## Next Steps

Once Docker is running:
1. Access Django admin: http://localhost:8000/admin
2. Create superuser (see commands above)
3. Populate roadmap data
4. Test the portfolio at http://localhost:3000
