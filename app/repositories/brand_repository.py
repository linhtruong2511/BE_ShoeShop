import shutil
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BrandStatus
from app.repositories.base_repository import BaseRepository
from app.models.brand import Brand
import os
import pathlib

UPLOAD_DIR = "static/uploads/brands"


class BrandRepository(BaseRepository[Brand]):
    def __init__(self, db: AsyncSession):
        super().__init__(Brand, db)

    async def get_all_brands(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[BrandStatus] = BrandStatus.active,
    ) -> tuple[list[Brand], int]:
        base_stmt = select(Brand)

        if status:
            base_stmt = base_stmt.where(Brand.status == status)

        result = await self.db.execute(
            base_stmt.order_by(Brand.created_at.desc()).offset(skip).limit(limit)
        )

        cnt_stmt = select(func.count()).select_from(Brand)
        total_result = await self.db.execute(cnt_stmt)
        total = total_result.scalar() or 0
        return list(result.scalars().all()), total

    async def get_by_code(self, brand_code: str) -> Brand | None:
        result = await self.db.execute(
            select(Brand).where(Brand.brand_code == brand_code)
        )
        return result.scalars().first()

    async def create_with_file(
        self, obj_in: Dict[str, Any], file: UploadFile | None = None
    ) -> Brand:
        if file:
            if file.content_type and file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="File must be an image")
            file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
            file_name = f"{uuid4()}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, file_name)
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                raise HTTPException(status_code=500, detail="Could not upload file")
            obj_in["logo_url"] = file_path
        else:
            obj_in["logo_url"] = None

        brand = await self.create(obj_in)
        await self.db.commit()
        await self.db.refresh(brand)
        return brand
