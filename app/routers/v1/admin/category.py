from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.models.user import User
from app.schemas.base import BaseResponse

router = APIRouter(prefix="/categories", tags=["Admin - Categories"])

@router.post("/", response_model=BaseResponse[CategoryResponse])
async def create_category(category_in: CategoryCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)):
    repo = CategoryRepository(db)
    existing = await repo.get_by_code(category_in.category_code)
    if existing:
        raise HTTPException(status_code=400, detail="Category code already exists")
    
    category = repo.create(category_in.model_dump())
    await db.commit()
    await db.refresh(category)
    return BaseResponse(data=category)

@router.put("/{category_id}", response_model=BaseResponse[CategoryResponse])
async def update_category(category_id: int, category_in: CategoryUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)):
    repo = CategoryRepository(db)
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    await repo.update(category, category_in.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(category)
    return BaseResponse(data=category)

@router.patch("/{category_id}/status", response_model=BaseResponse)
async def update_category_status(category_id: int, status: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)):
    repo = CategoryRepository(db)
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await repo.update(category, {"status": status})
    await db.commit()
    return BaseResponse(data=None)
