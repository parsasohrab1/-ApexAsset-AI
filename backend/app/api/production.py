"""
Production Data API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional
from datetime import datetime, date

from ..database import get_async_read_db
from ..db_models import ProductionData, Asset
from ..auth import require_engineer, require_manager
from pydantic import BaseModel


router = APIRouter(prefix="/api/production", tags=["Production"])

# Pagination limits
PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAX = 500


# Pydantic Models
class ProductionResponse(BaseModel):
    id: str
    asset_id: str
    production_date: datetime
    oil_production: Optional[float]
    gas_production: Optional[float]
    water_production: Optional[float]
    oil_rate: Optional[float]
    gas_rate: Optional[float]
    water_cut: Optional[float]
    uptime_hours: Optional[float]
    
    class Config:
        from_attributes = True


class ProductionSummary(BaseModel):
    total_oil: float
    total_gas: float
    total_water: float
    avg_oil_rate: float
    avg_gas_rate: float
    avg_water_cut: float
    total_records: int


@router.get("/", response_model=List[ProductionResponse])
async def list_production_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX),
    asset_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get production data with optional filtering"""
    stmt = select(ProductionData)

    if asset_id:
        stmt = stmt.where(ProductionData.asset_id == asset_id)
    if start_date:
        stmt = stmt.where(ProductionData.production_date >= start_date)
    if end_date:
        stmt = stmt.where(ProductionData.production_date <= end_date)

    stmt = stmt.order_by(desc(ProductionData.production_date)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/summary", response_model=ProductionSummary)
async def get_production_summary(
    asset_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_manager),
):
    """Get production summary statistics"""
    stmt = select(
        func.sum(ProductionData.oil_production).label('total_oil'),
        func.sum(ProductionData.gas_production).label('total_gas'),
        func.sum(ProductionData.water_production).label('total_water'),
        func.avg(ProductionData.oil_rate).label('avg_oil_rate'),
        func.avg(ProductionData.gas_rate).label('avg_gas_rate'),
        func.avg(ProductionData.water_cut).label('avg_water_cut'),
        func.count().label('total_records')
    ).select_from(ProductionData)

    if asset_id:
        stmt = stmt.where(ProductionData.asset_id == asset_id)
    if start_date:
        stmt = stmt.where(ProductionData.production_date >= start_date)
    if end_date:
        stmt = stmt.where(ProductionData.production_date <= end_date)

    result = await db.execute(stmt)
    row = result.one()

    return ProductionSummary(
        total_oil=row.total_oil or 0,
        total_gas=row.total_gas or 0,
        total_water=row.total_water or 0,
        avg_oil_rate=row.avg_oil_rate or 0,
        avg_gas_rate=row.avg_gas_rate or 0,
        avg_water_cut=row.avg_water_cut or 0,
        total_records=row.total_records or 0
    )


@router.get("/by-asset/{asset_id}", response_model=List[ProductionResponse])
async def get_production_by_asset(
    asset_id: str,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_read_db),
    _: object = Depends(require_engineer),
):
    """Get recent production data for a specific asset"""
    # Verify asset exists
    asset_result = await db.execute(select(Asset).where(Asset.id == asset_id))
    if not asset_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Asset not found")

    stmt = (
        select(ProductionData)
        .where(ProductionData.asset_id == asset_id)
        .order_by(desc(ProductionData.production_date))
        .limit(days)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
