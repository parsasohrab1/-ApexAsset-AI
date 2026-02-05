"""
Asset management routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_read_db
from ..repositories import AsyncAssetRepository
from ..auth import require_engineer

router = APIRouter(prefix="/api/assets", tags=["Assets"])

PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAX = 500


@router.get("")
async def get_assets(
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX,
        description=f"Number of items per page (max {PAGE_SIZE_MAX})"
    ),
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get all assets with pagination (offset-based)"""
    repo = AsyncAssetRepository(db)
    assets = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()
    page = skip // limit + 1 if limit > 0 else 1
    has_next = skip + limit < total
    return {
        "assets": assets,
        "total": total,
        "page": page,
        "page_size": limit,
        "has_next": has_next,
        "next_offset": skip + limit if has_next else None,
    }


@router.get("/{asset_id}")
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
