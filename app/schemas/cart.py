from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CartItemBase(BaseModel):
    sku_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    cart_item_id: int
    product_id: int
    sku_code: str
    product_name: str
    brand_name: str
    color_name: str

    size: str
    image_url: str
    unit_price: float
    discount_type: str
    discount_value: float
    discounted_price: float
    line_total: float
    stock_quantity: int
    is_available: bool
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


    class Config:
        from_attributes = True


class CartBase(BaseModel):
    customer_id: Optional[int] = None
    session_id: Optional[str] = None
    status: str = "active"

class CartSummaryResponse(BaseModel):
    subtotal: float
    item_count: int

class CartResponse(CartBase):
    cart_id: int
    items: List[CartItemResponse] = []
    summary: CartSummaryResponse
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
