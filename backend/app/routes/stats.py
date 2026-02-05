"""
Statistics routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_read_db
from ..repositories import AsyncUserRepository, AsyncAssetRepository, AsyncAlertRepository
from ..db_models import AssetStatus, AlertSeverity, AlertStatus
from ..auth import require_manager

router = APIRouter(prefix="/api", tags=["Statistics"])


@router.get("/stats")
async def get_statistics(
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_manager),
):
    """Get system statistics"""
    asset_repo = AsyncAssetRepository(db)
    alert_repo = AsyncAlertRepository(db)
    user_repo = AsyncUserRepository(db)

    return {
        "assets": {
            "total": await asset_repo.count(),
            "active": await asset_repo.count({"status": AssetStatus.ACTIVE}),
            "maintenance": await asset_repo.count({"status": AssetStatus.MAINTENANCE}),
            "inactive": await asset_repo.count({"status": AssetStatus.INACTIVE}),
        },
        "alerts": {
            "total": await alert_repo.count(),
            "open": await alert_repo.count({"status": AlertStatus.OPEN}),
            "critical": await alert_repo.count({
                "severity": AlertSeverity.CRITICAL,
                "status": AlertStatus.OPEN,
            }),
            "high": await alert_repo.count({
                "severity": AlertSeverity.HIGH,
                "status": AlertStatus.OPEN,
            }),
        },
        "users": {
            "total": await user_repo.count(),
            "active": await user_repo.count({"is_active": True}),
        },
    }
