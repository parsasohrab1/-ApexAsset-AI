"""Async Asset Repository"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .async_base import AsyncBaseRepository
from ..db_models import Asset, AssetType, AssetStatus


class AsyncAssetRepository(AsyncBaseRepository[Asset]):
    """Async repository for Asset operations"""

    def __init__(self, db: AsyncSession):
        super().__init__(Asset, db)

    async def get_by_type(
        self, asset_type: AssetType, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        """Get assets by type"""
        stmt = (
            select(Asset)
            .where(Asset.asset_type == asset_type)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(
        self, status: AssetStatus, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        """Get assets by status"""
        stmt = (
            select(Asset)
            .where(Asset.status == status)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_assets(
        self, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        """Get all active assets"""
        return await self.get_by_status(AssetStatus.ACTIVE, skip, limit)

    async def get_children(
        self, parent_id: str, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        """Get child assets of a parent with pagination"""
        stmt = (
            select(Asset)
            .where(Asset.parent_id == parent_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_children(self, parent_id: str) -> int:
        """Count children of a parent asset"""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(Asset).where(Asset.parent_id == parent_id)
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def get_root_assets(
        self, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        """Get assets with no parent"""
        stmt = (
            select(Asset)
            .where(Asset.parent_id == None)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def change_status(
        self, asset_id: str, new_status: AssetStatus
    ) -> Optional[Asset]:
        """Change asset status"""
        return await self.update(asset_id, {"status": new_status})
