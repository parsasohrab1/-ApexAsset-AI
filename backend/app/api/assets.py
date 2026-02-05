"""
Asset Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from ..database import get_async_read_db
from ..repositories.async_asset_repository import AsyncAssetRepository
from ..db_models import AssetType, AssetStatus
from ..auth import require_engineer
from pydantic import BaseModel


router = APIRouter(prefix="/api/assets", tags=["Assets"])

# Pagination limits
PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAX = 500


# Pydantic Models for API
class AssetResponse(BaseModel):
    id: str
    name: str
    asset_type: str
    description: Optional[str]
    status: str
    parent_id: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    manufacturer: Optional[str]
    model: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    assets: List[AssetResponse]
    total: int
    page: int
    page_size: int
    has_next: bool = False
    next_offset: Optional[int] = None


@router.get("/", response_model=AssetListResponse)
async def list_assets(
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Items per page (max {PAGE_SIZE_MAX})"
    ),
    asset_type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get list of assets with pagination and optional filtering"""
    repo = AsyncAssetRepository(db)

    filters = {}
    if asset_type:
        filters['asset_type'] = asset_type
    if status:
        filters['status'] = status

    assets = await repo.get_all(skip=skip, limit=limit, filters=filters)
    total = await repo.count(filters=filters if filters else None)
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total

    return AssetListResponse(
        assets=assets,
        total=total,
        page=page,
        page_size=limit,
        has_next=has_next,
        next_offset=skip + limit if has_next else None,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get asset by ID"""
    repo = AsyncAssetRepository(db)
    asset = await repo.get(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.get("/{asset_id}/children", response_model=AssetListResponse)
async def get_asset_children(
    asset_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Items per page (max {PAGE_SIZE_MAX})"
    ),
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get child assets of a parent asset with pagination"""
    repo = AsyncAssetRepository(db)

    # Verify parent exists
    parent = await repo.get(asset_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent asset not found")

    children = await repo.get_children(asset_id, skip=skip, limit=limit)
    total = await repo.count_children(asset_id)
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total

    return AssetListResponse(
        assets=children,
        total=total,
        page=page,
        page_size=limit,
        has_next=has_next,
        next_offset=skip + limit if has_next else None,
    )


@router.get("/type/{asset_type}", response_model=AssetListResponse)
async def get_assets_by_type(
    asset_type: AssetType,
    skip: int = Query(0, ge=0),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Items per page (max {PAGE_SIZE_MAX})"
    ),
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get assets by type with pagination"""
    repo = AsyncAssetRepository(db)
    assets = await repo.get_by_type(asset_type, skip=skip, limit=limit)
    total = await repo.count({'asset_type': asset_type})
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total

    return AssetListResponse(
        assets=assets,
        total=total,
        page=page,
        page_size=limit,
        has_next=has_next,
        next_offset=skip + limit if has_next else None,
    )
