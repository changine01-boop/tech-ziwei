#!/bin/sh
set -e
echo "[entrypoint] running alembic upgrade head..."
alembic upgrade head
echo "[entrypoint] starting uvicorn..."
exec uvicorn tech_ziwei.main:app --host 0.0.0.0 --port "${PORT:-8000}"
