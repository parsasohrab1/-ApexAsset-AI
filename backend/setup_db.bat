@echo off
echo ============================================================
echo ApexAsset AI - Database Setup Script (Windows)
echo ============================================================
echo.

echo Step 1: Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo ✓ Dependencies installed successfully
echo.

echo Step 2: Checking PostgreSQL connection...
psql -U postgres -c "SELECT version();" > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo WARNING: PostgreSQL connection failed. Make sure PostgreSQL is running.
    echo You can start it with: net start postgresql-x64-14
)
echo.

echo Step 3: Creating database and user...
psql -U postgres -c "CREATE DATABASE apexasset_db;" 2>nul
psql -U postgres -c "CREATE USER apexasset WITH PASSWORD 'apexasset123';" 2>nul
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE apexasset_db TO apexasset;" 2>nul
echo ✓ Database setup complete
echo.

echo Step 4: Initializing database schema and seed data...
python -m app.init_db
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to initialize database
    exit /b 1
)
echo.

echo ============================================================
echo Database setup complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Configure .env file with your settings
echo 2. Set up InfluxDB for time-series data
echo 3. Start the backend server: uvicorn app.main:app --reload
echo.
pause
