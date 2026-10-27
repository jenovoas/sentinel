#!/bin/bash
set -e

echo "⏳ Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
  sleep 1
done

echo "✅ PostgreSQL is ready!"
echo "🔄 Running Alembic migrations..."

python -m alembic upgrade head

echo "🚀 Starting Sentinel Backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
