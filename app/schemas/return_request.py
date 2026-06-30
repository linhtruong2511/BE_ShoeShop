from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ReturnItemBase(BaseModel):
    order_detail_id: int
    quantity: int
    condition: str

class ReturnItemCreate(ReturnItemBase):
    pass

class ReturnItemResponse(ReturnItemBase):
    return_item_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReturnRequestBase(BaseModel):
    order_id: int
    reason: str

class ReturnRequestCreate(ReturnRequestBase):
    items: List[ReturnItemCreate]

class ReturnRequestResponse(ReturnRequestBase):
    return_id: int
    customer_id: int
    status: str
    refund_amount: Optional[float] = None
    processed_by: Optional[int] = None
    processed_at: Optional[datetime] = None
    note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ReturnItemResponse] = []

    class Config:
        from_attributes = True
