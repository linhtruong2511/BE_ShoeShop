from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.dependencies import get_db, get_current_user, get_current_admin
from app.repositories.return_repository import ReturnRepository
from app.schemas.return_request import ReturnRequestCreate, ReturnRequestResponse
from app.models.user import User
from app.schemas.base import PaginatedResponse, PaginationMeta, BaseResponse

router = APIRouter(prefix="/returns", tags=["returns"])

@router.get("/", response_model=PaginatedResponse[ReturnRequestResponse])
async def get_returns(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    repo = ReturnRepository(db)
    items, total = await repo.get_all(skip=skip, limit=limit)
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(page=page, limit=limit, total_items=total, total_pages=total_pages)
    )

@router.patch("/{return_id}/review", response_model=BaseResponse)
async def review_return(return_id: int, status: str, note: str = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)):
    repo = ReturnRepository(db)
    req = await repo.get_by_id(return_id)
    if not req: raise HTTPException(404, "Return request not found")
    req.return_status = status
    if note:
        req.admin_note = note
    await db.commit()
    return BaseResponse(data=None)

@router.patch("/{return_id}/complete", response_model=BaseResponse)
async def complete_return(return_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)):
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.return_request import ReturnRequest
    from app.models.product_sku import ProductSku
    from app.models.stock_log import StockLog
    
    req = await db.scalar(select(ReturnRequest).options(selectinload(ReturnRequest.items).selectinload("order_detail")).where(ReturnRequest.return_id == return_id))
    if not req: raise HTTPException(404, "Return request not found")
    if req.status == "completed": return BaseResponse(data=None)
    
    req.status = "completed"
    
    for item in req.items:
        sku_id = item.order_detail.sku_id
        sku = await db.get(ProductSku, sku_id)
        if sku:
            stock_before = sku.stock_quantity
            sku.stock_quantity += item.quantity
            
            # create log
            log = StockLog(
                sku_id=sku_id,
                change_quantity=item.quantity,
                reason="cancel_return",
                reason_note=f"Hoàn trả hàng theo yêu cầu đổi trả {return_id}",
                stock_before=stock_before,
                stock_after=sku.stock_quantity,
                created_by=current_user.user_id
            )
            db.add(log)
            
    await db.commit()
    return BaseResponse(data=None)
