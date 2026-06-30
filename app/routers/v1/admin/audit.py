from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.dependencies import get_db, get_current_admin
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditLogResponse
from app.models.user import User
from app.schemas.base import PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/", response_model=PaginatedResponse[AuditLogResponse])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    repo = AuditRepository(db)
    items, total = await repo.get_all(skip=skip, limit=limit)
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(page=page, limit=limit, total_items=total, total_pages=total_pages)
    )
