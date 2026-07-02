from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import (
    CustomerAdminListResponse,
    CustomerAdminDetailResponse,
    CustomerStatusUpdate,
    CustomerUpdate,
)
from app.models.user import User
from app.schemas.base import (
    PaginatedResponse,
    BaseResponse,
    PaginationMeta,
    StatusUpdate,
)

router = APIRouter(prefix="/customers", tags=["Admin - Customers"])


@router.get("/", response_model=PaginatedResponse[CustomerAdminListResponse])
async def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = CustomerRepository(db)
    items, total = await repo.get_customers_paginated(page, limit, search, status)
    total_pages = (total + limit - 1) // limit

    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page, limit=limit, total_items=total, total_pages=total_pages
        ),
    )


@router.get("/{customer_id}", response_model=BaseResponse[CustomerAdminDetailResponse])
async def get_customer_detail(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = CustomerRepository(db)
    result = await repo.get_customer_with_stats(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer_data = result["customer"].__dict__
    customer_data["stats"] = result["stats"]

    return BaseResponse(data=customer_data)


@router.put("/{customer_id}", response_model=BaseResponse[CustomerAdminDetailResponse])
async def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = CustomerRepository(db)
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    await repo.update_customer(customer_id, customer_in.model_dump(exclude_unset=True))
    
    result = await repo.get_customer_with_stats(customer_id)
    customer_data = result["customer"].__dict__
    customer_data["stats"] = result["stats"]

    return BaseResponse(data=customer_data)


@router.patch(
    "/{customer_id}/status", response_model=BaseResponse[CustomerAdminDetailResponse]
)
async def update_customer_status(
    customer_id: int,
    status_update: CustomerStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = CustomerRepository(db)
    customer = await repo.update_status(customer_id, status_update.status.value)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    result = await repo.get_customer_with_stats(customer_id)
    customer_data = result["customer"].__dict__
    customer_data["stats"] = result["stats"]

    return BaseResponse(data=customer_data)
