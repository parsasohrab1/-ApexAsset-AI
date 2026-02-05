from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import AsyncGenerator, Generator
from .config import settings

# Sync Engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.ENVIRONMENT == "development"
)

# Async Write Engine (primary – for writes)
async_engine = create_async_engine(
    settings.DATABASE_ASYNC_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.ENVIRONMENT == "development"
)

# Async Read Engine (replica for reports/dashboard – optional)
_async_read_url = (settings.DATABASE_READ_ASYNC_URL or "").strip()
async_read_engine = (
    create_async_engine(
        _async_read_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.ENVIRONMENT == "development"
    )
    if _async_read_url
    else async_engine  # fallback to primary if no replica configured
)

# Session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

# Async write session (primary)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Async read session (replica for dashboard, reports, list endpoints)
AsyncReadSessionLocal = async_sessionmaker(
    bind=async_read_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


# Dependency for sync database session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency for async database session (default: write/primary)
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Dependency for read-only queries (dashboard, reports, list endpoints)
async def get_async_read_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncReadSessionLocal() as session:
        yield session


# Dependency for write operations (create, update, delete)
async def get_async_write_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
