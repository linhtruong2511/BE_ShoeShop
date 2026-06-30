import shutil
from typing import Any, Dict
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.brand import Brand
import os
import pathlib

UPLOAD_DIR = "static/uploads/brands"


class BrandRepository(BaseRepository[Brand]):
    def __init__(self, db: AsyncSession):
        super().__init__(Brand, db)

    async def get_by_code(self, brand_code: str) -> Brand | None:
        result = await self.db.execute(
            select(Brand).where(Brand.brand_code == brand_code)
        )
        return result.scalars().first()

    async def create_with_file(
        self, obj_in: Dict[str, Any], file: UploadFile | None = None
    ) -> Brand:
        if file:
            if file.content_type and not file.content_type.startswith("image/"):
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

        brand = self.create(obj_in)
        await self.db.commit()
        await self.db.refresh(brand)
        return brand
