from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.dependencies import get_db, get_current_admin
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.models.user import User
from app.schemas.base import PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=PaginatedResponse[CategoryResponse])
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = CategoryRepository(db)
    items, total = await repo.get_all(skip=skip, limit=limit)
    
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(page=page, limit=limit, total_items=total, total_pages=total_pages)
    )

