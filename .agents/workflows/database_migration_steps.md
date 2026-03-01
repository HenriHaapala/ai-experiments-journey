---
description: Database Migration Steps
---
# Database Migration Workflow

This workflow ensures database changes (new models, altered fields) in Django are safely propagated to the local PostgreSQL instance via Docker.

## Step 1: Detect Changes

After modifying `backend/portfolio/models.py`, you must generate the migration scripts. Because the backend runs inside Docker, the command must be executed within the container.

```bash
docker-compose exec backend python manage.py makemigrations
```

> [!NOTE]
> If the `backend` container is not currently running, you can run: 
> `docker-compose run --rm backend python manage.py makemigrations`

## Step 2: Apply Migrations

Once the migration files (e.g., `0002_auto_....py`) are generated in `backend/portfolio/migrations/`, apply them to the PostgreSQL database.

```bash
// turbo
docker-compose exec backend python manage.py migrate
```

## Step 3: Verify & Commit

1.  Check that the local application is still running correctly without database errors.
2.  Commit the newly generated migration files (inside `backend/portfolio/migrations/`) to version control. **Do not** add them to `.gitignore`. They are required for the production database to update during the next deployment.

```bash
git add backend/portfolio/migrations/
git commit -m "Generated database migrations for [feature name]"
```
