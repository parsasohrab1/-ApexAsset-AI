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
from .realtime.websocket import handle_websocket_client
from .routes import auth_routes, dashboard, assets, alerts, stats
from .readiness import run_readiness_checks

# Create tables on startup only in development. In production, run: alembic upgrade head
if settings.ENVIRONMENT != "production":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ApexAsset AI Backend",
    version="0.1.0",
    description="Backend API for ApexAsset AI - Complete Asset Lifecycle Digital Twin Platform",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(dashboard.router)
app.include_router(assets.router)
app.include_router(alerts.router)
app.include_router(stats.router)


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
        "version": "0.1.0",
        "websocket": settings.websocket_url,
        "read_replica": bool(settings.DATABASE_READ_ASYNC_URL.strip()),
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time data streaming.
    Connect: ws://localhost:8000/ws
    Actions: subscribe/unsubscribe to topics (sensors, alerts, production), ping.
    """
    await handle_websocket_client(websocket)


@app.get("/srs", response_class=PlainTextResponse)
def get_srs() -> str:
    """Get Software Requirements Specification"""
    repo_root = Path(__file__).resolve().parents[2]
    srs_path = repo_root / "README.md"
    if not srs_path.exists():
        return "SRS not found."
    return srs_path.read_text(encoding="utf-8")
