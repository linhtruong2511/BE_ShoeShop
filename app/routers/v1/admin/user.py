from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserAdminCreate, UserAdminUpdate, UserAdminListResponse, UserAdminDetailResponse
from app.models.user import User
from app.schemas.base import PaginatedResponse, BaseResponse, PaginationMeta, StatusUpdate
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["Admin - Users"])

@router.get("/", response_model=PaginatedResponse[UserAdminListResponse])
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    role: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    repo = UserRepository(db)
    items, total = await repo.get_users_paginated(page, limit, search, role, status)
    total_pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total_items=total,
            total_pages=total_pages
        )
    )

@router.get("/{user_id}", response_model=BaseResponse[UserAdminDetailResponse])
async def get_user_detail(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_admin)
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return BaseResponse(data=user)

@router.post("/", response_model=BaseResponse[UserAdminDetailResponse])
async def create_user(
    user_in: UserAdminCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_admin)
):
    repo = UserRepository(db)
    
    if await repo.get_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await repo.get_by_username(user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")
        
    user_data = user_in.model_dump()
    user_data["password_hash"] = hash_password(user_data.pop("password"))
    
    user = repo.create(user_data)
    await db.commit()
    await db.refresh(user)
    
    return BaseResponse(data=user)

@router.put("/{user_id}", response_model=BaseResponse[UserAdminDetailResponse])
async def update_user(
    user_id: int, 
    user_in: UserAdminUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_admin)
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await repo.update(user, user_in.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(user)
    
    return BaseResponse(data=user)

@router.patch("/{user_id}/status", response_model=BaseResponse[UserAdminDetailResponse])
async def update_user_status(
    user_id: int, 
    status_update: StatusUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_admin)
):
    repo = UserRepository(db)
    user = await repo.update_status(user_id, status_update.status)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return BaseResponse(data=user)
