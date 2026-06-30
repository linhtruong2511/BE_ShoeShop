from fastapi import UploadFile
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BrandBase(BaseModel):
    brand_code: str
    brand_name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    status: str = "active"


class BrandCreate(BaseModel):
    brand_name: str
    description: Optional[str] = None
    file: UploadFile | None = None


class BrandUpdate(BaseModel):
    brand_name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[str] = None


class BrandResponse(BrandBase):
    brand_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
