---
description: How to deploy the application to Oracle Cloud
---
# Deployment Workflow

This workflow describes how to trigger a deployment of the AI Portfolio to the production Oracle Cloud environment.

> [!NOTE]
> Ensure you have committed all necessary code changes to the `main` branch before triggering a deployment.

## Prerequisites
1.  Verify that all new dependencies have been added to `backend/requirements.txt` or `frontend/package.json`.
2.  Verify that no secrets are hardcoded in the codebase.
3.  Ensure your working directory is clean (`git status`).

## Step 1: Push to Main

The deployment process is entirely handled by GitHub actions. There is no need to SSH into the Oracle Cloud instance manually unless a deployment fails.

```bash
git add .
git commit -m "Deploying latest changes to production"
git push origin main
```

## Step 2: Monitor GitHub Actions

After pushing, the GitHub Action (`.github/workflows/deploy.yml`) will automatically trigger. It performs the following:
1.  Connects to the Oracle Cloud instance via SSH.
2.  Pulls the latest code from the `main` branch.
3.  Rebuilds the Docker containers (`docker-compose build`).
4.  Restarts the services (`docker-compose up -d`).

You can view the progress of the deployment in the "Actions" tab of the GitHub repository.

## Step 3: Verify Deployment

Once the GitHub Action completes successfully, verify the deployment by visiting the live URL and checking that the recent changes are visible.

If backend changes were made, verify them at `https://your-portfolio-url.com/api/health/` (or equivalent health check endpoint).
