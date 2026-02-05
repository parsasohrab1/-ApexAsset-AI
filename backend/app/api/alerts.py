"""
Alert Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from ..database import get_async_read_db, get_async_write_db
from ..repositories.async_alert_repository import AsyncAlertRepository
from ..db_models import AlertSeverity, AlertStatus
from ..auth import require_engineer, require_manager
from pydantic import BaseModel


router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

# Pagination limits
PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAX = 500


# Pydantic Models
class AlertResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    severity: str
    status: str
    asset_id: str
    alert_type: Optional[str]
    threshold_value: Optional[float]
    actual_value: Optional[float]
    occurred_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    page: int
    page_size: int
    has_next: bool = False
    next_offset: Optional[int] = None


class AlertStatsResponse(BaseModel):
    total: int
    open: int
    acknowledged: int
    resolved: int
    by_severity: dict


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Items per page (max {PAGE_SIZE_MAX})"
    ),
    severity: Optional[AlertSeverity] = None,
    status: Optional[AlertStatus] = None,
    asset_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get list of alerts with pagination and optional filtering"""
    repo = AsyncAlertRepository(db)

    filters = {}
    if severity:
        filters['severity'] = severity
    if status:
        filters['status'] = status
    if asset_id:
        filters['asset_id'] = asset_id

    alerts = await repo.get_all(skip=skip, limit=limit, filters=filters)
    total = await repo.count(filters=filters if filters else None)
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total

    return AlertListResponse(
        alerts=alerts,
        total=total,
        page=page,
        page_size=limit,
        has_next=has_next,
        next_offset=skip + limit if has_next else None,
    )


@router.get("/stats", response_model=AlertStatsResponse)
async def get_alert_stats(
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_manager),
):
    """Get alert statistics"""
    repo = AsyncAlertRepository(db)

    return AlertStatsResponse(
        total=await repo.count(),
        open=await repo.count({'status': AlertStatus.OPEN}),
        acknowledged=await repo.count({'status': AlertStatus.ACKNOWLEDGED}),
        resolved=await repo.count({'status': AlertStatus.RESOLVED}),
        by_severity={
            'critical': await repo.count({'severity': AlertSeverity.CRITICAL}),
            'high': await repo.count({'severity': AlertSeverity.HIGH}),
            'medium': await repo.count({'severity': AlertSeverity.MEDIUM}),
            'low': await repo.count({'severity': AlertSeverity.LOW})
        }
    )


@router.get("/open", response_model=AlertListResponse)
async def get_open_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Items per page (max {PAGE_SIZE_MAX})"
    ),
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get all open alerts with pagination"""
    repo = AsyncAlertRepository(db)
    alerts = await repo.get_open_alerts(skip=skip, limit=limit)
    total = await repo.count({'status': AlertStatus.OPEN})
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total

    return AlertListResponse(
        alerts=alerts,
        total=total,
        page=page,
        page_size=limit,
        has_next=has_next,
        next_offset=skip + limit if has_next else None,
    )


@router.get("/critical", response_model=AlertListResponse)
async def get_critical_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Items per page (max {PAGE_SIZE_MAX})"
    ),
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get critical alerts with pagination"""
    repo = AsyncAlertRepository(db)
    alerts = await repo.get_critical_alerts(skip=skip, limit=limit)
    total = (
        await repo.count({"severity": AlertSeverity.CRITICAL, "status": AlertStatus.OPEN})
        + await repo.count({"severity": AlertSeverity.CRITICAL, "status": AlertStatus.ACKNOWLEDGED})
    )
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total

    return AlertListResponse(
        alerts=alerts,
        total=total,
        page=page,
        page_size=limit,
        has_next=has_next,
        next_offset=skip + limit if has_next else None,
    )


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_async_write_db),
    _: object = Depends(require_manager),
):
    """Acknowledge an alert"""
    repo = AsyncAlertRepository(db)
    alert = await repo.acknowledge_alert(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"status": "success", "message": "Alert acknowledged", "alert_id": alert_id}


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_async_write_db),
    _: object = Depends(require_manager),
):
    """Resolve an alert"""
    repo = AsyncAlertRepository(db)
    alert = await repo.resolve_alert(alert_id, resolution_notes)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"status": "success", "message": "Alert resolved", "alert_id": alert_id}
