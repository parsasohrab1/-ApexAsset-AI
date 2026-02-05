from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from ..config import settings
from ..rate_limit import limiter
from ..models import Token, User, UserCreate, UserLogin, RefreshTokenRequest, TokenData
from ..auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_SECRET_KEY,
)
from ..database import get_db
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_REGISTER)
def register(request: Request, user: UserCreate, db=Depends(get_db)):
    """Register a new user."""
    auth_service = AuthService(db)
    try:
        new_user = auth_service.create_user(user)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
):
    """Login and get access token."""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires,
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role.value}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
@limiter.limit(settings.RATE_LIMIT_REFRESH)
def refresh_token(request: Request, body: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        token_data = decode_token(body.refresh_token, REFRESH_SECRET_KEY)
        
        # Create new tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        role_val = token_data.role.value if hasattr(token_data.role, "value") else token_data.role
        access_token = create_access_token(
            data={"sub": token_data.email, "role": role_val},
            expires_delta=access_token_expires,
        )
        refresh_token = create_refresh_token(
            data={"sub": token_data.email, "role": role_val}
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.get("/me", response_model=TokenData)
def get_me(current_user: TokenData = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.post("/logout")
def logout(current_user: TokenData = Depends(get_current_active_user)):
    """Logout (client should delete tokens)."""
    # In a production app, you might want to blacklist the token
    return {"message": "Successfully logged out"}
