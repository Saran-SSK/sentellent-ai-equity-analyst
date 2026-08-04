#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

until pg_isready \
  -h host.docker.internal \
  -p 5432 \
  -U postgres
do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug