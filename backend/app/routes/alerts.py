"""
Alert management routes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_read_db
from ..repositories import AsyncAlertRepository
from ..db_models import AlertSeverity, AlertStatus
from ..auth import require_engineer

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAX = 500


@router.get("")
async def get_alerts(
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Number of items per page (max {PAGE_SIZE_MAX})"
    ),
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get all alerts with pagination (offset-based)"""
    repo = AsyncAlertRepository(db)
    alerts = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total
    return {
        "alerts": alerts,
        "total": total,
        "page": page,
        "page_size": limit,
        "has_next": has_next,
        "next_offset": skip + limit if has_next else None,
    }


@router.get("/open")
async def get_open_alerts(
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Number of items per page (max {PAGE_SIZE_MAX})"
    ),
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get open alerts with pagination (offset-based)"""
    repo = AsyncAlertRepository(db)
    alerts = await repo.get_open_alerts(skip=skip, limit=limit)
    total = await repo.count({"status": AlertStatus.OPEN})
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total
    return {
        "alerts": alerts,
        "total": total,
        "page": page,
        "page_size": limit,
        "has_next": has_next,
        "next_offset": skip + limit if has_next else None,
    }


@router.get("/critical")
async def get_critical_alerts(
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Number of items per page (max {PAGE_SIZE_MAX})"
    ),
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get critical alerts with pagination (offset-based)"""
    repo = AsyncAlertRepository(db)
    alerts = await repo.get_critical_alerts(skip=skip, limit=limit)
    total = (
        await repo.count({"severity": AlertSeverity.CRITICAL, "status": AlertStatus.OPEN})
        + await repo.count({"severity": AlertSeverity.CRITICAL, "status": AlertStatus.ACKNOWLEDGED})
    )
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total
    return {
        "alerts": alerts,
        "total": total,
        "page": page,
        "page_size": limit,
        "has_next": has_next,
        "next_offset": skip + limit if has_next else None,
    }
