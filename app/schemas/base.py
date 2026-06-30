from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar('T')

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int

class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "Thao tác thành công"

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    pagination: PaginationMeta
    message: str = "Thao tác thành công"

class StatusUpdate(BaseModel):
    status: str
