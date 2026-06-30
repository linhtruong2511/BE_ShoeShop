from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.enums import VoucherStatus
from app.repositories.voucher_repository import VoucherRepository
from app.schemas.voucher import VoucherResponse
from app.schemas.base import PaginatedResponse, PaginationMeta, BaseResponse

router = APIRouter(prefix="/vouchers", tags=["vouchers"])


@router.get("/", response_model=PaginatedResponse[VoucherResponse])
async def get_active_vouchers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = VoucherRepository(db)
    skip = (page - 1) * limit
    items, total = await repo.get_active_vouchers(skip=skip, limit=limit)
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page, limit=limit, total_items=total, total_pages=total_pages
        ),
    )


@router.get("/code/{code}", response_model=BaseResponse[VoucherResponse])
async def get_voucher_by_code(code: str, db: AsyncSession = Depends(get_db)):
    repo = VoucherRepository(db)
    voucher = await repo.get_by_code(code.upper().strip())
    if not voucher:
        raise HTTPException(status_code=404, detail="Mã giảm giá không tồn tại!")

    if voucher.status == "paused":
        raise HTTPException(
            status_code=400, detail="Mã giảm giá đã bị tạm ngưng sử dụng!"
        )

    if voucher.status == "expired":
        raise HTTPException(status_code=400, detail="Mã giảm giá đã hết hạn sử dụng!")

    if voucher.status not in ["active", "hidden"]:
        raise HTTPException(status_code=400, detail="Mã giảm giá không khả dụng!")

    return BaseResponse(data=voucher)
