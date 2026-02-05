# Quick Start Guide - ApexAsset AI Backend

## What's Been Set Up

✅ **PostgreSQL Database**
- Full schema with 8 core tables (Users, Assets, Alerts, Maintenance, Work Orders, Production Data, Sensor Readings)
- SQLAlchemy ORM with async support
- Comprehensive indexes for performance

✅ **InfluxDB Integration**
- Client for 1Hz time-series sensor data
- Query and write APIs
- Aggregation support

✅ **Database Migrations**
- Alembic configured and ready
- Initial migration templates

✅ **Repository Pattern**
- BaseRepository with common CRUD operations
- Specialized repositories (User, Asset, Alert)
- Clean separation of concerns

✅ **CRUD Services**
- Authentication service with JWT tokens
- Password hashing with bcrypt
- Role-based access control (RBAC)

✅ **API Endpoints**
- Health check with DB connectivity test
- Dashboard with real-time data
- Asset management endpoints
- Alert management endpoints
- Statistics endpoint

## Quick Start (Windows)

```powershell
# 1. Start PostgreSQL (if not running)
net start postgresql-x64-14

# 2. Run setup script
cd backend
.\setup_db.bat

# 3. Start the server
uvicorn app.main:app --reload
```

## Quick Start (Linux/macOS)

```bash
# 1. Start PostgreSQL (if not running)
sudo systemctl start postgresql

# 2. Run setup script
cd backend
chmod +x setup_db.sh
./setup_db.sh

# 3. Start the server
uvicorn app.main:app --reload
```

## Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env
# Edit .env with your database credentials

# 3. Initialize database
python -m app.init_db

# 4. Start server
uvicorn app.main:app --reload
```

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Dashboard
curl http://localhost:8000/dashboard

# Statistics
curl http://localhost:8000/api/stats

# Assets
curl http://localhost:8000/api/assets

# Open alerts
curl http://localhost:8000/api/alerts/open
```

## Access Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Default Test Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@apexasset.com | admin123 | Admin |
| operator@apexasset.com | operator123 | Field Operator |
| engineer@apexasset.com | engineer123 | Production Engineer |
| maintenance@apexasset.com | maint123 | Maintenance Tech |

## Project Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── env.py
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── db_models.py            # SQLAlchemy models
│   ├── models.py               # Pydantic models (API)
│   ├── influxdb_client.py      # InfluxDB integration
│   ├── init_db.py              # Database initialization
│   ├── repositories/           # Data access layer
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── asset_repository.py
│   │   └── alert_repository.py
│   └── services/               # Business logic
│       └── auth_service.py
├── .env.example                # Environment variables template
├── .env                        # Your local environment (create this)
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
├── setup_db.bat               # Windows setup script
├── setup_db.sh                # Linux/macOS setup script
├── DATABASE_SETUP.md          # Detailed setup guide
└── QUICK_START.md             # This file
```

## Database Models Overview

### Users
Complete user management with roles and authentication

### Assets
Hierarchical asset structure with support for:
- Wells, Separators, Compressors, Pumps, Heat Exchangers, Pipelines, Storage Tanks, Platforms, Facilities
- Parent-child relationships
- Geographic location
- Technical specifications (JSON)

### Alerts
Real-time alert management with:
- Severity levels (Low, Medium, High, Critical)
- Status tracking (Open, Acknowledged, In Progress, Resolved, Closed)
- Asset association
- Threshold monitoring

### Maintenance Records
Track all maintenance activities:
- Preventive, Predictive, Corrective, Breakdown
- Labor hours and costs
- Parts replaced (JSON)
- Findings and recommendations

### Work Orders
Complete work order lifecycle:
- Priority levels
- Status tracking
- Scheduling (planned vs actual)
- Cost tracking (estimated vs actual)
- Assignment to technicians

### Production Data
Daily production tracking:
- Oil, gas, water production
- Production rates
- Pressures and temperatures
- Uptime/downtime tracking

### Sensor Readings
Aggregated sensor data (1-minute to daily averages)
- Real-time 1Hz data stored in InfluxDB

## Next Steps

1. ⚠️ **Change default passwords** in production
2. 🔐 **Configure .env** with production credentials
3. 🗄️ **Set up InfluxDB** for time-series data
4. 🔄 **Configure backups** for PostgreSQL and InfluxDB
5. 📊 **Connect frontend** to these APIs
6. 🧪 **Add unit tests** for repositories and services
7. 📝 **Add API authentication** (JWT tokens)
8. 🚀 **Deploy** to production environment

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the backend directory
cd backend
pip install -r requirements.txt
```

### Database connection errors
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Test connection
psql -U apexasset -d apexasset_db -h localhost
```

### Port already in use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## Need Help?

- 📖 Read the full [DATABASE_SETUP.md](DATABASE_SETUP.md)
- 🐛 Check error logs in the terminal
- 💡 Review FastAPI docs: https://fastapi.tiangolo.com/
- 📚 SQLAlchemy docs: https://docs.sqlalchemy.org/
