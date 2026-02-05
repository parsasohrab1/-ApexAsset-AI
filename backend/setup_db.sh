#!/bin/bash

echo "============================================================"
echo "ApexAsset AI - Database Setup Script (Linux/macOS)"
echo "============================================================"
echo

echo "Step 1: Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed successfully"
echo

echo "Step 2: Checking PostgreSQL connection..."
psql -U postgres -c "SELECT version();" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "WARNING: PostgreSQL connection failed. Make sure PostgreSQL is running."
    echo "You can start it with: sudo systemctl start postgresql"
fi
echo

echo "Step 3: Creating database and user..."
psql -U postgres -c "CREATE DATABASE apexasset_db;" 2>/dev/null
psql -U postgres -c "CREATE USER apexasset WITH PASSWORD 'apexasset123';" 2>/dev/null
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE apexasset_db TO apexasset;" 2>/dev/null
echo "✓ Database setup complete"
echo

echo "Step 4: Initializing database schema and seed data (development)..."
echo "  For production, use: alembic upgrade head"
python -m app.init_db
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to initialize database"
    exit 1
fi
echo

echo "============================================================"
echo "Database setup complete!"
echo "============================================================"
echo
echo "Next steps:"
echo "1. Configure .env file with your settings"
echo "2. Set up InfluxDB for time-series data"
echo "3. Start the backend server: uvicorn app.main:app --reload"
echo
