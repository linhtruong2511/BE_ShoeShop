from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.core.enums import UserStatus


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: str
    status: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None


class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class UserAdminListResponse(UserResponse):
    pass


class UserAdminDetailResponse(UserResponse):
    pass


class UserAdminCreate(UserCreate):
    pass


class UserAdminUpdate(UserUpdate):
    pass


class UserStatusUpdate(BaseModel):
    status: UserStatus = UserStatus.active
