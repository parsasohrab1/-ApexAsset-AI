from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .base import BaseRepository
from ..db_models import Alert, AlertSeverity, AlertStatus


class AlertRepository(BaseRepository[Alert]):
    """Repository for Alert operations"""
    
    def __init__(self, db: Session):
        super().__init__(Alert, db)
    
    def get_by_asset(self, asset_id: str, skip: int = 0, limit: int = 100) -> List[Alert]:
        """Get alerts for a specific asset"""
        return self.db.query(Alert).filter(Alert.asset_id == asset_id).order_by(desc(Alert.occurred_at)).offset(skip).limit(limit).all()
    
    def get_by_severity(self, severity: AlertSeverity, skip: int = 0, limit: int = 100) -> List[Alert]:
        """Get alerts by severity"""
        return self.db.query(Alert).filter(Alert.severity == severity).order_by(desc(Alert.occurred_at)).offset(skip).limit(limit).all()
    
    def get_open_alerts(self, skip: int = 0, limit: int = 100) -> List[Alert]:
        """Get all open alerts"""
        return self.db.query(Alert).filter(Alert.status == AlertStatus.OPEN).order_by(desc(Alert.occurred_at)).offset(skip).limit(limit).all()
    
    def get_critical_alerts(self, skip: int = 0, limit: int = 100) -> List[Alert]:
        """Get critical open alerts"""
        return (
            self.db.query(Alert)
            .filter(Alert.severity == AlertSeverity.CRITICAL)
            .filter(Alert.status.in_([AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED]))
            .order_by(desc(Alert.occurred_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = None) -> Alert:
        """Acknowledge an alert"""
        return self.update(alert_id, {
            "status": AlertStatus.ACKNOWLEDGED,
            "acknowledged_at": datetime.utcnow()
        })
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = None) -> Alert:
        """Resolve an alert"""
        data = {
            "status": AlertStatus.RESOLVED,
            "resolved_at": datetime.utcnow()
        }
        if resolution_notes:
            data["resolution_notes"] = resolution_notes
        return self.update(alert_id, data)
