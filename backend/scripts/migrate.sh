#!/bin/bash
# Run Alembic migrations. Use in production before starting the app.
set -e
cd "$(dirname "$0")/.."
echo "Running database migrations..."
alembic upgrade head
echo "✓ Migrations complete"
