from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    default_address: Optional[str] = None

class CustomerCreate(CustomerBase):
    password: str = Field(..., min_length=6)

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    default_address: Optional[str] = None

class CustomerResponse(CustomerBase):
    customer_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CustomerLogin(BaseModel):
    email: EmailStr
    password: str

class CustomerStatsResponse(BaseModel):
    total_orders: int = 0
    total_spent: float = 0.0

class CustomerAdminListResponse(CustomerResponse):
    pass

class CustomerAdminDetailResponse(CustomerResponse):
    stats: Optional[CustomerStatsResponse] = None
