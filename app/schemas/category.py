from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    category_id: Optional[int] = None
    category_code: str
    category_name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    status: str = "active"


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CategoryResponse(CategoryBase):
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryTreeRespone(CategoryResponse):
    children: Optional[List[CategoryResponse]]
