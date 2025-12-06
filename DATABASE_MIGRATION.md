# Database Migration Guide

## Overview
You have an existing Docker postgres container with data that needs to be migrated to the new Docker setup.

**Current situation:**
- Old container: `aiportfolio-postgres` (stopped, contains data)
- Old volume: `ai-portfolio_postgres_data` (contains database files)
- New setup: Uses same database name and volume structure

## Safe Migration Steps

### Step 1: Export Data from Old Container

Start the old container temporarily:
```bash
docker start aiportfolio-postgres
```

Wait 5 seconds for postgres to be ready, then export the database:
```bash
docker exec aiportfolio-postgres pg_dump -U ai_portfolio_user -d ai_portfolio_dev --clean --if-exists --no-owner --no-acl > database_backup.sql
```

This creates `database_backup.sql` in your current directory with all your data.

### Step 2: Stop and Remove Old Container

Stop the container:
```bash
docker stop aiportfolio-postgres
```

Remove the container (this is safe - the volume is preserved):
```bash
docker rm aiportfolio-postgres
```

### Step 3: Start New Docker Stack

Now start your new Docker setup:
```bash
docker-compose up -d
```

Wait for all services to start (~20 seconds). Check status:
```bash
docker-compose ps
```

### Step 4: Import Data to New Database

Import the backup into the new postgres container:
```bash
docker exec -i aiportfolio-postgres psql -U ai_portfolio_user -d ai_portfolio_dev < database_backup.sql
```

### Step 5: Verify Migration

Check that data imported successfully:
```bash
docker exec aiportfolio-postgres psql -U ai_portfolio_user -d ai_portfolio_dev -c "\dt"
```

This should show all your tables (RoadmapSection, LearningEntry, KnowledgeChunk, etc.)

Count your learning entries to verify:
```bash
docker exec aiportfolio-postgres psql -U ai_portfolio_user -d ai_portfolio_dev -c "SELECT COUNT(*) FROM portfolio_learningentry;"
```

### Step 6: Test the Application

Access your application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/health/
- Database Admin: http://localhost:8080

Check that:
- ✅ Roadmap loads correctly
- ✅ Learning entries appear
- ✅ Chat/RAG functionality works

## Cleanup (After Verification)

Once you've confirmed everything works, you can remove the old volume:

```bash
docker volume rm ai-portfolio_postgres_data
```

⚠️ **Only do this after verifying the migration was successful!**

## Quick Command Reference

```bash
# Export data from old container
docker start aiportfolio-postgres
docker exec aiportfolio-postgres pg_dump -U ai_portfolio_user -d ai_portfolio_dev --clean --if-exists --no-owner --no-acl > database_backup.sql
docker stop aiportfolio-postgres
docker rm aiportfolio-postgres

# Start new stack and import
docker-compose up -d
docker exec -i aiportfolio-postgres psql -U ai_portfolio_user -d ai_portfolio_dev < database_backup.sql

# Verify
docker-compose ps
docker exec aiportfolio-postgres psql -U ai_portfolio_user -d ai_portfolio_dev -c "\dt"
```

## Troubleshooting

**"relation already exists" errors during import:**
- This is normal if migrations already created empty tables
- The `--clean --if-exists` flags handle this

**Import takes a long time:**
- Large databases may take several minutes
- Watch for "INSERT" statements in the output

**Connection refused:**
- Wait longer for postgres to start (healthcheck takes ~10 seconds)
- Check logs: `docker-compose logs postgres`

**Data missing after import:**
- Check the backup file size: `ls -lh database_backup.sql`
- If 0 bytes, the export failed - try again with old container running

## Rollback Plan

If something goes wrong:

1. Stop new stack:
   ```bash
   docker-compose down
   ```

2. Restore old container:
   ```bash
   docker run -d \
     --name aiportfolio-postgres \
     -v ai-portfolio_postgres_data:/var/lib/postgresql/data \
     -p 5432:5432 \
     -e POSTGRES_DB=ai_portfolio_dev \
     -e POSTGRES_USER=ai_portfolio_user \
     -e POSTGRES_PASSWORD=your_password_here \
     pgvector/pgvector:pg16
   ```

3. Your data is safe in the `ai-portfolio_postgres_data` volume
