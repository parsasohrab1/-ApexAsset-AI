from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .models import TokenData, User, UserRole
from .config import settings

# JWT Configuration — keys from settings (validated at startup)
SECRET_KEY = settings.SECRET_KEY
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str, secret_key: str) -> TokenData:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role_raw = payload.get("role")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        role = UserRole(role_raw) if isinstance(role_raw, str) else role_raw
        return TokenData(email=email, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Get the current authenticated user from the token."""
    return decode_token(token, SECRET_KEY)


async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Get the current active user."""
    # In a real app, check if user is active in database
    return current_user


class RoleChecker:
    """Dependency to check if user has required role."""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        role = (
            UserRole(current_user.role)
            if isinstance(current_user.role, str)
            else current_user.role
        )
        if role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user


# Role-based access dependencies
require_admin = RoleChecker([UserRole.ADMIN])
require_manager = RoleChecker([
    UserRole.ADMIN,
    UserRole.ASSET_MANAGER,
    UserRole.HSE_MANAGER,
    UserRole.EXECUTIVE,
])
require_engineer = RoleChecker([
    UserRole.ADMIN,
    UserRole.ASSET_MANAGER,
    UserRole.HSE_MANAGER,
    UserRole.EXECUTIVE,
    UserRole.PRODUCTION_ENGINEER,
    UserRole.RESERVOIR_ENGINEER,
    UserRole.DATA_SCIENTIST,
])
require_operator = RoleChecker([
    UserRole.ADMIN,
    UserRole.ASSET_MANAGER,
    UserRole.HSE_MANAGER,
    UserRole.EXECUTIVE,
    UserRole.PRODUCTION_ENGINEER,
    UserRole.RESERVOIR_ENGINEER,
    UserRole.DATA_SCIENTIST,
    UserRole.FIELD_OPERATOR,
    UserRole.MAINTENANCE_TECH,
])
