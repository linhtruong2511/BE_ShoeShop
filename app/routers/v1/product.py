from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    ProductListResponse,
    ProductDetailResponse,
)
from app.schemas.base import PaginatedResponse, PaginationMeta, BaseResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=PaginatedResponse[ProductListResponse])
async def get_products(
    keyword: Optional[str] = Query(None),
    brand_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    color_name: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    in_stock: Optional[bool] = Query(None),
    on_sale: Optional[bool] = Query(None),
    gender_target: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
):

    service = ProductService(db)
    products, total, total_pages = await service.search_products(
        keyword=keyword,
        brand_id=brand_id,
        category_id=category_id,
        color_name=color_name,
        size=size,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        on_sale=on_sale,
        gender_target=gender_target,
        skip=(page - 1) * limit,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return PaginatedResponse(
        data=products,
        pagination=PaginationMeta(
            page=page, limit=limit, total_items=total, total_pages=total_pages
        ),
    )


@router.get("/{product_id}", response_model=BaseResponse[ProductDetailResponse])
async def get_product_detail(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    product = await service.get_with_details(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return BaseResponse(data=product)
