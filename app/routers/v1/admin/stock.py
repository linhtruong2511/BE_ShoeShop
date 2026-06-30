from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.dependencies import get_db, get_current_admin
from app.repositories.stock_repository import StockRepository
from app.schemas.stock import StockLogCreate, StockLogResponse
from app.models.user import User
from app.schemas.base import PaginatedResponse, PaginationMeta, BaseResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.post("/adjust", response_model=BaseResponse[StockLogResponse])
async def adjust_stock(
    stock_in: StockLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    repo = StockRepository(db)
    try:
        log = await repo.update_stock(
            sku_id=stock_in.sku_id,
            change_quantity=stock_in.change_quantity,
            reason=stock_in.reason,
            reason_note=stock_in.reason_note,
            user_id=current_user.user_id,
            reference_type=stock_in.reference_type,
            reference_id=stock_in.reference_id
        )
        await db.commit()
        await db.refresh(log)
        return BaseResponse(data=log)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/logs", response_model=PaginatedResponse[StockLogResponse])
async def get_stock_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    repo = StockRepository(db)
    items, total = await repo.get_all(skip=skip, limit=limit)
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(page=page, limit=limit, total_items=total, total_pages=total_pages)
    )
