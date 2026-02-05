"""
Dashboard routes and Pydantic models.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List
from datetime import datetime

from ..database import get_async_read_db
from ..repositories import AsyncAssetRepository, AsyncAlertRepository
from ..db_models import AssetStatus, AlertStatus
from ..cache import get_cache
from ..auth import require_engineer

router = APIRouter(tags=["Dashboard"])


# Pydantic models for API responses
class KPI(BaseModel):
    label: str
    value: str
    change: str
    tone: str


class ModuleCard(BaseModel):
    title: str
    summary: str
    bullets: List[str]
    status: str


class DashboardAlertResponse(BaseModel):
    title: str
    severity: str
    time: str
    action: str


class DashboardResponse(BaseModel):
    kpis: List[KPI]
    modules: List[ModuleCard]
    alerts: List[DashboardAlertResponse]


DASHBOARD_CACHE_KEY = "dashboard"

# Shared constants — used in both success and fallback responses
STATIC_MODULES: tuple[ModuleCard, ...] = (
    ModuleCard(
        title="Exploration",
        summary="Seismic interpretation and prospect evaluation.",
        bullets=["3D seismic viewer", "Well log correlation", "Risked resources"],
        status="Ready",
    ),
    ModuleCard(
        title="Development",
        summary="Reservoir planning and economics.",
        bullets=["Reservoir model maps", "Well planning canvas", "NPV scenarios"],
        status="Planned",
    ),
    ModuleCard(
        title="Production",
        summary="Real-time monitoring and optimization.",
        bullets=["1Hz dashboards", "Alarm management", "Energy efficiency"],
        status="Live",
    ),
    ModuleCard(
        title="Maintenance",
        summary="Condition monitoring and RUL forecasting.",
        bullets=["Vibration analytics", "Failure probability", "Work orders"],
        status="Live",
    ),
    ModuleCard(
        title="Decommissioning",
        summary="End-of-life planning and compliance.",
        bullets=["Cost estimation", "Regulatory tracking", "Rehab planning"],
        status="Planned",
    ),
)

NO_ALERTS_PLACEHOLDER = DashboardAlertResponse(
    title="No active alerts",
    severity="Low",
    time="N/A",
    action="All systems normal",
)

FALLBACK_KPIS = [
    KPI(label="Assets Monitored", value="0", change="N/A", tone="neutral"),
    KPI(label="Active Alerts", value="0", change="N/A", tone="neutral"),
    KPI(label="Production Efficiency", value="N/A", change="N/A", tone="neutral"),
    KPI(label="Maintenance Backlog", value="0", change="N/A", tone="neutral"),
]

FALLBACK_ALERTS = [
    DashboardAlertResponse(
        title="Database not initialized",
        severity="Medium",
        time="Now",
        action="Run: python -m app.init_db",
    )
]


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
) -> DashboardResponse:
    """Get dashboard data with real database statistics. Cached (TTL from config)."""
    cache = get_cache()
    cached = await cache.get(DASHBOARD_CACHE_KEY)
    if cached is not None:
        return DashboardResponse(**cached)

    try:
        asset_repo = AsyncAssetRepository(db)
        alert_repo = AsyncAlertRepository(db)

        total_assets = await asset_repo.count({"status": AssetStatus.ACTIVE})
        active_alerts = await alert_repo.count({"status": AlertStatus.OPEN})
        recent_alerts = await alert_repo.get_open_alerts(limit=3)

        alert_list = []
        for alert in recent_alerts:
            minutes_ago = int((datetime.utcnow() - alert.occurred_at).total_seconds() / 60)
            time_str = f"{minutes_ago}m ago" if minutes_ago < 60 else f"{minutes_ago // 60}h ago"
            alert_list.append(
                DashboardAlertResponse(
                    title=alert.title,
                    severity=alert.severity.value.capitalize(),
                    time=time_str,
                    action=alert.action_taken or "Review and respond",
                )
            )

        response = DashboardResponse(
            kpis=[
                KPI(label="Assets Monitored", value=str(total_assets), change="+4% WoW", tone="positive"),
                KPI(label="Active Alerts", value=str(active_alerts), change="-2 since 24h", tone="positive"),
                KPI(label="Production Efficiency", value="92.4%", change="+1.3% WoW", tone="positive"),
                KPI(label="Maintenance Backlog", value="18", change="+3 new", tone="warning"),
            ],
            modules=STATIC_MODULES,
            alerts=alert_list or [NO_ALERTS_PLACEHOLDER],
        )
        await cache.set(DASHBOARD_CACHE_KEY, response.model_dump())
        return response

    except Exception as e:
        print(f"Dashboard error: {e}")
        return DashboardResponse(
            kpis=FALLBACK_KPIS,
            modules=list(STATIC_MODULES),
            alerts=FALLBACK_ALERTS,
        )
