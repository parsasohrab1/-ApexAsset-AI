from typing import Optional
from sqlalchemy.orm import Session
from .base import BaseRepository
from ..db_models import User


class UserRepository(BaseRepository[User]):
    """Repository for User operations"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_active_users(self, skip: int = 0, limit: int = 100):
        """Get all active users"""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def deactivate_user(self, user_id: str) -> Optional[User]:
        """Deactivate a user"""
        return self.update(user_id, {"is_active": False})
    
    def activate_user(self, user_id: str) -> Optional[User]:
        """Activate a user"""
        return self.update(user_id, {"is_active": True})
