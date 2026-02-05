from typing import List, Optional
from sqlalchemy.orm import Session
from .base import BaseRepository
from ..db_models import Asset, AssetType, AssetStatus


class AssetRepository(BaseRepository[Asset]):
    """Repository for Asset operations"""
    
    def __init__(self, db: Session):
        super().__init__(Asset, db)
    
    def get_by_type(self, asset_type: AssetType, skip: int = 0, limit: int = 100) -> List[Asset]:
        """Get assets by type"""
        return self.db.query(Asset).filter(Asset.asset_type == asset_type).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: AssetStatus, skip: int = 0, limit: int = 100) -> List[Asset]:
        """Get assets by status"""
        return self.db.query(Asset).filter(Asset.status == status).offset(skip).limit(limit).all()
    
    def get_active_assets(self, skip: int = 0, limit: int = 100) -> List[Asset]:
        """Get all active assets"""
        return self.get_by_status(AssetStatus.ACTIVE, skip, limit)
    
    def get_children(self, parent_id: str) -> List[Asset]:
        """Get child assets of a parent"""
        return self.db.query(Asset).filter(Asset.parent_id == parent_id).all()
    
    def get_root_assets(self, skip: int = 0, limit: int = 100) -> List[Asset]:
        """Get assets with no parent"""
        return self.db.query(Asset).filter(Asset.parent_id == None).offset(skip).limit(limit).all()
    
    def change_status(self, asset_id: str, new_status: AssetStatus) -> Optional[Asset]:
        """Change asset status"""
        return self.update(asset_id, {"status": new_status})
