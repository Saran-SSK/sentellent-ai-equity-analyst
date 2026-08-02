#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=Postgres123 psql -h postgres -U postgres -d sentellent -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - running migrations"

echo "Running Alembic migrations..."
alembic upgrade head

echo "Migrations completed successfully"

echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
