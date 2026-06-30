from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VoucherBase(BaseModel):
    voucher_code: str
    voucher_name: str
    description: Optional[str] = None
    discount_type: str
    discount_value: float
    min_order_amount: float = 0
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    max_usage_per_customer: Optional[int] = None
    start_date: datetime
    end_date: datetime
    status: str = "active"

class VoucherCreate(VoucherBase):
    pass

class VoucherUpdate(BaseModel):
    voucher_name: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    min_order_amount: Optional[float] = None
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    max_usage_per_customer: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None

class VoucherResponse(VoucherBase):
    voucher_id: int
    used_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
