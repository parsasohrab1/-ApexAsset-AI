"""Async Alert Repository"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from .async_base import AsyncBaseRepository
from ..db_models import Alert, AlertSeverity, AlertStatus


class AsyncAlertRepository(AsyncBaseRepository[Alert]):
    """Async repository for Alert operations"""

    def __init__(self, db: AsyncSession):
        super().__init__(Alert, db)

    async def get_by_asset(
        self, asset_id: str, skip: int = 0, limit: int = 100
    ) -> List[Alert]:
        """Get alerts for a specific asset"""
        stmt = (
            select(Alert)
            .where(Alert.asset_id == asset_id)
            .order_by(desc(Alert.occurred_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_severity(
        self, severity: AlertSeverity, skip: int = 0, limit: int = 100
    ) -> List[Alert]:
        """Get alerts by severity"""
        stmt = (
            select(Alert)
            .where(Alert.severity == severity)
            .order_by(desc(Alert.occurred_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_open_alerts(
        self, skip: int = 0, limit: int = 100
    ) -> List[Alert]:
        """Get all open alerts"""
        stmt = (
            select(Alert)
            .where(Alert.status == AlertStatus.OPEN)
            .order_by(desc(Alert.occurred_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_critical_alerts(
        self, skip: int = 0, limit: int = 100
    ) -> List[Alert]:
        """Get critical open alerts"""
        stmt = (
            select(Alert)
            .where(Alert.severity == AlertSeverity.CRITICAL)
            .where(Alert.status.in_([AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED]))
            .order_by(desc(Alert.occurred_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def acknowledge_alert(
        self, alert_id: str, acknowledged_by: str = None
    ) -> Optional[Alert]:
        """Acknowledge an alert"""
        return await self.update(alert_id, {
            "status": AlertStatus.ACKNOWLEDGED,
            "acknowledged_at": datetime.utcnow()
        })

    async def resolve_alert(
        self, alert_id: str, resolution_notes: str = None
    ) -> Optional[Alert]:
        """Resolve an alert"""
        data = {
            "status": AlertStatus.RESOLVED,
            "resolved_at": datetime.utcnow()
        }
        if resolution_notes:
            data["resolution_notes"] = resolution_notes
        return await self.update(alert_id, data)
