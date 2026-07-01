from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.enums import OrderStatus
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderResponse
from app.models.user import User
from app.schemas.base import PaginatedResponse, PaginationMeta, BaseResponse
from sqlalchemy import select, func, and_
from app.models.order import Order
from app.models.order_detail import OrderDetail

router = APIRouter(prefix="/orders", tags=["Admin - Orders"])


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def get_all_orders(
    page: int = 1,
    limit: int = 100,
    status: str | None = None,
    order_code: str | None = None,
    phone: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):

    conditions = []
    if status and status != "all":
        conditions.append(Order.order_status == status)
    if order_code:
        conditions.append(Order.order_code.ilike(f"%{order_code}%"))
    if phone:
        conditions.append(Order.receiver_phone.ilike(f"%{phone}%"))
    if from_date:
        conditions.append(Order.created_at >= from_date)
    if to_date:
        conditions.append(Order.created_at <= to_date)

    where_clause = and_(*conditions) if conditions else True

    count_stmt = select(func.count()).select_from(Order).where(where_clause)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    skip = (page - 1) * limit
    from sqlalchemy.orm import selectinload

    stmt = (
        select(Order)
        .options(selectinload(Order.details))
        .where(where_clause)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page, limit=limit, total_items=total, total_pages=total_pages
        ),
    )


@router.get("/{order_id}", response_model=BaseResponse[OrderResponse])
async def get_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = OrderRepository(db)
    order = await repo.get_with_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return BaseResponse(data=order)


from app.models.order_status_log import OrderStatusLog
from app.schemas.order import OrderStatusUpdate, OrderCancel


@router.patch("/{order_id}/status", response_model=BaseResponse)
async def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = OrderRepository(db)
    order = await repo.get_by_id(order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    order.order_status = payload.status
    log = OrderStatusLog(
        order_id=order_id, new_status=payload.status, note=payload.note
    )
    db.add(log)
    await db.commit()
    return BaseResponse(data=None)


@router.patch("/{order_id}/cancel", response_model=BaseResponse)
async def admin_cancel_order(
    order_id: int,
    payload: OrderCancel,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = OrderRepository(db)
    order = await repo.get_by_id(order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    order.order_status = OrderStatus.cancelled
    log = OrderStatusLog(
        order_id=order_id,
        new_status="cancelled",
        note=f"Admin cancelled: {payload.reason}",
    )
    db.add(log)
    await db.commit()
    return BaseResponse(data=None)
