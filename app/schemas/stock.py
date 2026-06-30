from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StockLogBase(BaseModel):
    sku_id: int
    change_quantity: int
    reason: str
    reason_note: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None

class StockLogCreate(StockLogBase):
    pass

class StockLogResponse(StockLogBase):
    log_id: int
    stock_before: int
    stock_after: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
