from pydantic import BaseModel, model_validator
from typing import Optional, List, Any
from datetime import datetime

from app.core.enums import OrderStatus, ShippingMethod


class OrderDetailBase(BaseModel):
    sku_id: int
    quantity: int
    unit_price: float
    discount_type_snapshot: str = "none"
    discount_value_snapshot: float = 0.0


class OrderDetailCreate(OrderDetailBase):
    sku_code_snapshot: str
    product_name_snapshot: str
    color_name_snapshot: str
    size_snapshot: str
    image_url_snapshot: Optional[str] = None
    discounted_price: float
    line_total: float


class OrderBase(BaseModel):
    customer_id: Optional[int] = None
    receiver_name: str
    receiver_phone: str
    shipping_address: str
    shipping_method: Optional[ShippingMethod] = ShippingMethod.standard
    note: Optional[str] = None
    payment_method: str
    voucher_id: Optional[int] = None


class OrderCreate(OrderBase):
    voucher_code: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    note: Optional[str] = None


class OrderCancel(BaseModel):
    reason: str


class OrderStatusLogResponse(BaseModel):
    log_id: int
    order_id: int
    old_status: Optional[str] = None
    new_status: str
    note: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True


class OrderDetailResponse(OrderDetailCreate):
    order_detail_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderResponse(OrderBase):
    order_id: int
    order_code: str
    payment_status: str
    voucher_code_snapshot: Optional[str] = None
    subtotal_amount: float
    voucher_discount_amount: float
    shipping_fee: float
    total_amount: float
    order_status: str
    cancelled_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    details: List[OrderDetailResponse] = []
    status_logs: List[OrderStatusLogResponse] = []

    class Config:
        from_attributes = True
