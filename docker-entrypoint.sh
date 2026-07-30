#!/bin/bash
set -e

echo "Waiting for database..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done
echo "Database is ready!"

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
