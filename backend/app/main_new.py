from fastapi import FastAPI, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pathlib import Path
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .rate_limit import limiter
from .database import get_async_read_db, engine, Base
from .api import assets, alerts, production
from .auth import require_admin
from .routes import auth_routes
from .realtime.websocket import handle_websocket_client
from .realtime.mqtt_client import initialize_mqtt_client
from .readiness import run_readiness_checks

# Create tables on startup only in development. In production, run: alembic upgrade head
if settings.ENVIRONMENT != "production":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ApexAsset AI Backend",
    version="0.2.0",
    description="Backend API for ApexAsset AI - Complete Asset Lifecycle Digital Twin Platform with Real-time Data",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_routes.router)
app.include_router(assets.router)
app.include_router(alerts.router)
app.include_router(production.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 60)
    print("ApexAsset AI Backend - Starting Up")
    print("=" * 60)
    
    # Initialize MQTT client (optional)
    try:
        initialize_mqtt_client(
            broker_host=settings.MQTT_BROKER_HOST,
            broker_port=settings.MQTT_BROKER_PORT,
        )
    except Exception as e:
        print(f"MQTT initialization skipped: {e}")
    
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down ApexAsset AI Backend...")


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_async_read_db)) -> dict:
    """Liveness probe: basic app and DB connectivity"""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "database": db_status,
        "version": "0.2.0",
        "websocket": settings.websocket_url,
        "features": ["REST API", "WebSocket", "MQTT", "InfluxDB"],
    }


@app.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_async_read_db)):
    """
    Readiness probe for Kubernetes/load balancers.
    Checks Database (required), InfluxDB (if configured), MQTT (if initialized).
    Returns 200 if ready to serve traffic, 503 otherwise.
    """
    ready, details = await run_readiness_checks(db)
    body = {"ready": ready, "checks": details}
    return JSONResponse(
        status_code=200 if ready else 503,
        content=body,
    )


@app.get("/srs", response_class=PlainTextResponse)
def get_srs() -> str:
    """Get Software Requirements Specification"""
    repo_root = Path(__file__).resolve().parents[2]
    srs_path = repo_root / "README.md"
    if not srs_path.exists():
        return "SRS not found."
    return srs_path.read_text(encoding="utf-8")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time data streaming
    
    Connect: ws://localhost:8000/ws
    
    Send messages:
    - Subscribe to sensors: {"action": "subscribe", "topic": "sensors"}
    - Subscribe to alerts: {"action": "subscribe", "topic": "alerts"}
    - Subscribe to production: {"action": "subscribe", "topic": "production"}
    - Unsubscribe: {"action": "unsubscribe", "topic": "sensors"}
    - Ping: {"action": "ping"}
    """
    await handle_websocket_client(websocket)


@app.get("/")
def root():
    """API root endpoint"""
    return {
        "name": "ApexAsset AI Backend",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
        "websocket": settings.websocket_url,
        "api_endpoints": {
            "assets": "/api/assets",
            "alerts": "/api/alerts",
            "production": "/api/production"
        }
    }


# Data Import Endpoint (ETL uses its own sync session)
@app.post("/api/admin/import-data")
async def import_sample_data(_: object = Depends(require_admin)):
    """
    Import sample synthetic data (Admin only)
    Generates and imports synthetic data for testing
    """
    from .data_generator.synthetic_data_generator import generate_sample_dataset
    from .etl.data_importer import run_etl_pipeline
    
    try:
        # Generate data
        print("Generating sample data...")
        generate_sample_dataset('sample_data')
        
        # Import data
        print("Importing data to database...")
        stats = run_etl_pipeline('sample_data')
        
        return {
            "status": "success",
            "message": "Sample data imported successfully",
            "statistics": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
