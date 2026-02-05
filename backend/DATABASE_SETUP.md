# Database Setup Guide for ApexAsset AI

## Overview

This guide explains how to set up and use the database infrastructure for ApexAsset AI, which includes:
- **PostgreSQL** for relational data (users, assets, alerts, maintenance records, etc.)
- **InfluxDB** for time-series data (sensor readings at 1Hz frequency)
- **SQLAlchemy** as the ORM
- **Alembic** for database migrations

## Prerequisites

### 1. Install PostgreSQL

#### Windows:
```powershell
# Download and install from https://www.postgresql.org/download/windows/
# Or using Chocolatey:
choco install postgresql
```

#### Linux:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

#### macOS:
```bash
brew install postgresql
```

### 2. Install InfluxDB

#### Windows:
```powershell
# Download from https://portal.influxdata.com/downloads/
# Or using Chocolatey:
choco install influxdb
```

#### Linux:
```bash
wget https://dl.influxdata.com/influxdb/releases/influxdb2-2.7.1-amd64.deb
sudo dpkg -i influxdb2-2.7.1-amd64.deb
```

#### macOS:
```bash
brew install influxdb
```

## Database Configuration

### 1. PostgreSQL Setup

Create the database and user:

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE apexasset_db;

-- Create user
CREATE USER apexasset WITH PASSWORD 'apexasset123';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE apexasset_db TO apexasset;

-- Exit
\q
```

### 2. InfluxDB Setup

```bash
# Start InfluxDB
influxd

# Open InfluxDB UI in browser: http://localhost:8086

# Create organization: apexasset
# Create bucket: sensor_data
# Create API token and save it
```

### 3. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration. All values are read from `.env` via `config.py`. See **`ENV_SETUP.md`** for the complete list of variables and production requirements.

Minimum for development:
- `SECRET_KEY` and `REFRESH_SECRET_KEY` (generate: `openssl rand -hex 32`)
- `DATABASE_URL` and `DATABASE_ASYNC_URL` (or use defaults)
- `ENVIRONMENT=development`

## Installation

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database

#### Development (ENVIRONMENT=development)

```bash
python -m app.init_db
```

This will:
- Create all database tables (via `create_all`)
- Seed initial data (users, assets, alerts, etc.)
- Display default credentials

#### Production (ENVIRONMENT=production)

**Use Alembic migrations only.** Do not run `create_all` or `python -m app.init_db` for schema creation.

```bash
# Apply migrations
alembic upgrade head

# Optionally seed data (users, assets) after migrations
ENVIRONMENT=development python -m app.init_db  # Only seeds; create_all is skipped in prod
```

Or seed via your deployment script after `alembic upgrade head`.

### 3. Alembic Migrations (Required for Production)

Migrations provide versioned, rollback-safe schema changes:

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one revision
alembic downgrade -1

# Rollback to base (empty schema)
alembic downgrade base

# Create a new migration after model changes
alembic revision --autogenerate -m "Add new_column to assets"

# Show current revision
alembic current
```

**Production deployment:** Run `alembic upgrade head` before starting the app (e.g. in CI/CD, Dockerfile, or init container).

## Database Schema

### Core Tables

#### Users
- `id` (Primary Key)
- `email` (Unique)
- `full_name`
- `hashed_password`
- `role` (Enum: field_operator, maintenance_tech, production_engineer, etc.)
- `is_active`
- `created_at`, `updated_at`, `last_login`

#### Assets
- `id` (Primary Key)
- `name`
- `asset_type` (Enum: well, separator, compressor, pump, etc.)
- `description`
- `status` (Enum: active, inactive, maintenance, decommissioned)
- `parent_id` (Self-referencing for hierarchy)
- `latitude`, `longitude`, `elevation`
- `specifications` (JSON)
- `manufacturer`, `model`, `serial_number`
- `installation_date`, `commissioning_date`

#### Alerts
- `id` (Primary Key)
- `title`, `description`
- `severity` (Enum: low, medium, high, critical)
- `status` (Enum: open, acknowledged, in_progress, resolved, closed)
- `asset_id` (Foreign Key to Assets)
- `created_by`, `assigned_to` (Foreign Keys to Users)
- `occurred_at`, `acknowledged_at`, `resolved_at`
- `threshold_value`, `actual_value`

#### Maintenance Records
- `id` (Primary Key)
- `asset_id` (Foreign Key)
- `maintenance_type` (Enum: preventive, predictive, corrective, breakdown)
- `scheduled_date`, `completed_date`
- `work_performed`, `parts_replaced` (JSON)
- `labor_hours`, `cost`
- `findings`, `recommendations`

#### Work Orders
- `id` (Primary Key)
- `work_order_number` (Unique)
- `asset_id`, `assigned_to` (Foreign Keys)
- `priority` (Enum: low, medium, high, critical)
- `status` (Enum: pending, scheduled, in_progress, completed, cancelled)
- `scheduled_start`, `scheduled_end`, `actual_start`, `actual_end`
- `estimated_hours`, `actual_hours`, `estimated_cost`, `actual_cost`

#### Production Data
- `id` (Primary Key)
- `asset_id` (Foreign Key)
- `production_date`
- `oil_production`, `gas_production`, `water_production`
- `oil_rate`, `gas_rate`, `water_cut`, `gor`
- `wellhead_pressure`, `flowing_pressure`, `static_pressure`
- `uptime_hours`, `downtime_hours`

#### Sensor Readings (Aggregated)
- For aggregated/historical sensor data (1-minute, hourly, daily averages)
- Real-time 1Hz data goes to InfluxDB

### InfluxDB Schema

**Measurement**: Various sensor types (temperature, pressure, flow_rate, vibration, etc.)

**Tags** (Indexed):
- `asset_id`
- `sensor_id`
- `sensor_type`
- `location`

**Fields** (Values):
- `value` (main sensor reading)
- `quality_flag`
- Additional sensor-specific fields

## Usage Examples

### 1. Using Repositories (Recommended)

```python
from app.database import SessionLocal
from app.repositories import AssetRepository, AlertRepository, UserRepository

# Create database session
db = SessionLocal()

try:
    # Asset operations
    asset_repo = AssetRepository(db)
    
    # Get all active assets
    active_assets = asset_repo.get_active_assets()
    
    # Get asset by ID
    asset = asset_repo.get("some-asset-id")
    
    # Create new asset
    new_asset = asset_repo.create({
        "name": "New Compressor",
        "asset_type": AssetType.COMPRESSOR,
        "status": AssetStatus.ACTIVE
    })
    
    # Alert operations
    alert_repo = AlertRepository(db)
    
    # Get open alerts
    open_alerts = alert_repo.get_open_alerts()
    
    # Get critical alerts
    critical_alerts = alert_repo.get_critical_alerts()
    
    # Acknowledge alert
    alert_repo.acknowledge_alert("alert-id")
    
finally:
    db.close()
```

### 2. Writing Time-Series Data to InfluxDB

```python
from app.influxdb_client import influxdb_manager
from datetime import datetime

# Write single sensor reading
influxdb_manager.write_sensor_data(
    measurement="temperature",
    asset_id="asset-123",
    sensor_id="temp-sensor-01",
    value=85.5,
    timestamp=datetime.utcnow(),
    additional_tags={"location": "platform_alpha"},
    additional_fields={"unit": "celsius", "quality": "good"}
)

# Query sensor data
data = influxdb_manager.query_sensor_data(
    measurement="temperature",
    asset_id="asset-123",
    start_time="-1h",
    aggregation_window="1m"  # 1-minute averages
)
```

### 3. Using FastAPI Endpoints

```bash
# Get health check
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/api/stats

# Get all assets
curl http://localhost:8000/api/assets

# Get open alerts
curl http://localhost:8000/api/alerts/open

# Get dashboard data
curl http://localhost:8000/dashboard
```

## Running the Application

### Development Mode

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Default Credentials

After running `python -m app.init_db`, you'll have these default users:

| Email | Password | Role |
|-------|----------|------|
| admin@apexasset.com | admin123 | Admin |
| operator@apexasset.com | operator123 | Field Operator |
| engineer@apexasset.com | engineer123 | Production Engineer |
| maintenance@apexasset.com | maint123 | Maintenance Tech |

**⚠️ Important**: Change these passwords in production!

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
Get-Service postgresql-x64-14     # Windows PowerShell

# Test connection
psql -U apexasset -d apexasset_db -h localhost
```

### InfluxDB Connection Issues

```bash
# Check if InfluxDB is running
influx ping

# Verify token
influx auth list
```

### Migration Issues

```bash
# Reset migrations (development only)
alembic downgrade base
alembic upgrade head

# Development: recreate database with create_all
ENVIRONMENT=development python -m app.init_db
```

## Database Maintenance

### Backup PostgreSQL

```bash
pg_dump -U apexasset -d apexasset_db -F c -f backup.dump
```

### Restore PostgreSQL

```bash
pg_restore -U apexasset -d apexasset_db backup.dump
```

### Backup InfluxDB

```bash
influx backup /path/to/backup --org apexasset
```

### Monitor Database Performance

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Next Steps

1. ✅ Set up authentication endpoints
2. ✅ Implement CRUD operations for all entities
3. ✅ Add data validation and error handling
4. ✅ Set up API documentation with Swagger UI (automatic with FastAPI)
5. ✅ Implement real-time WebSocket connections for sensor data
6. ✅ Add background tasks for data aggregation
7. ✅ Implement caching with Redis (optional)
8. ✅ Set up monitoring and logging

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
