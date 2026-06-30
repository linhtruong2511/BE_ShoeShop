from pydantic import BaseModel, EmailStr
from typing import Optional
from .customer import CustomerBase, CustomerResponse
from .user import UserResponse
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
    
class LoginCustomerResponse(Token):
    customer: CustomerResponse
    

class LoginAdminResponse(Token):
    user: UserResponse