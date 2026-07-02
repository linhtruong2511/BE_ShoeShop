from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.dependencies import get_db, get_current_admin
from app.core.enums import VoucherStatus
from app.repositories.voucher_repository import VoucherRepository
from app.schemas.voucher import (
    VoucherCreate,
    VoucherResponse,
    VoucherStatusUpdate,
    VoucherUpdate,
)
from app.models.user import User
from app.schemas.base import (
    PaginatedResponse,
    PaginationMeta,
    BaseResponse,
    StatusUpdate,
)
from app.models.order import Order
from sqlalchemy import select

router = APIRouter(prefix="/vouchers", tags=["vouchers"])


@router.get("/", response_model=PaginatedResponse[VoucherResponse])
async def get_vouchers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = VoucherRepository(db)
    items, total = await repo.get_all(skip=skip, limit=limit)
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page, limit=limit, total_items=total, total_pages=total_pages
        ),
    )


@router.post("/", response_model=BaseResponse[VoucherResponse])
async def create_voucher(
    voucher_in: VoucherCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = VoucherRepository(db)
    existing = await repo.get_by_code(voucher_in.voucher_code)
    if existing:
        raise HTTPException(status_code=400, detail="Voucher code already exists")

    voucher = await repo.create(voucher_in.model_dump())
    await db.commit()
    await db.refresh(voucher)
    return BaseResponse(data=voucher)


@router.put("/{voucher_id}", response_model=BaseResponse[VoucherResponse])
async def update_voucher(
    voucher_id: int,
    voucher_in: VoucherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = VoucherRepository(db)
    voucher = await repo.get_by_id(voucher_id)
    if not voucher:
        raise HTTPException(404, "Voucher not found")
    await repo.update(voucher, voucher_in.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(voucher)
    return BaseResponse(data=voucher)


@router.patch("/{voucher_id}/status", response_model=BaseResponse)
async def update_voucher_status(
    voucher_id: int,
    status_data: VoucherStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = VoucherRepository(db)
    voucher = await repo.get_by_id(voucher_id)
    if not voucher:
        raise HTTPException(404, "Voucher not found")
    voucher.status = status_data.status
    await db.commit()
    return BaseResponse(data=None)


@router.get("/{voucher_id}/usages", response_model=BaseResponse)
async def get_voucher_usages(
    voucher_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):

    query = (
        select(Order)
        .where(Order.voucher_id == voucher_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    orders = result.scalars().all()

    usages = [
        {
            "order_id": o.order_id,
            "order_code": o.order_code,
            "customer_id": o.customer_id,
            "receiver_name": o.receiver_name,
            "total_amount": o.total_amount,
            "voucher_discount_amount": o.voucher_discount_amount,
            "order_status": o.order_status,
            "created_at": o.created_at,
        }
        for o in orders
    ]
    return BaseResponse(data=usages)
