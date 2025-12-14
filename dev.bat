@echo off
REM Development mode with hot-reloading
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d %*
