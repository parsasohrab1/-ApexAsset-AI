from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    FIELD_OPERATOR = "field_operator"
    MAINTENANCE_TECH = "maintenance_technician"
    PRODUCTION_ENGINEER = "production_engineer"
    RESERVOIR_ENGINEER = "reservoir_engineer"
    HSE_MANAGER = "hse_manager"
    ASSET_MANAGER = "asset_manager"
    DATA_SCIENTIST = "data_scientist"
    EXECUTIVE = "executive"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
