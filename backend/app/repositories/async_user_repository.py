"""Async User Repository"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .async_base import AsyncBaseRepository
from ..db_models import User


class AsyncUserRepository(AsyncBaseRepository[User]):
    """Async repository for User operations"""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_users(
        self, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get all active users"""
        stmt = (
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def deactivate_user(self, user_id: str) -> Optional[User]:
        """Deactivate a user"""
        return await self.update(user_id, {"is_active": False})

    async def activate_user(self, user_id: str) -> Optional[User]:
        """Activate a user"""
        return await self.update(user_id, {"is_active": True})
