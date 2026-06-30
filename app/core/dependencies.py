from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User

security_scheme = HTTPBearer()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    token_creds: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = token_creds.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    token_type = payload.get("type")
    if token_type != "staff":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
        
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    if user.status != "active":
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository

async def get_current_customer(
    token_creds: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Customer:
    token = token_creds.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    token_type = payload.get("type")
    if token_type != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
        
    try:
        customer_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    customer_repo = CustomerRepository(db)
    customer = await customer_repo.get_by_id(customer_id)
    if customer is None:
        raise credentials_exception
    # Customer status check if applicable
    return customer

optional_security_scheme = HTTPBearer(auto_error=False)

async def get_current_user_optional(
    token_creds: Optional[HTTPAuthorizationCredentials] = Depends(optional_security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[Customer | User]:
    if not token_creds:
        return None
    token = token_creds.credentials
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None
        
    try:
        user_id = int(user_id_str)
    except ValueError:
        return None    
    
    token_type = payload.get("type")
    if token_type == "customer":
        customer_repo = CustomerRepository(db)
        customer = await customer_repo.get_by_id(user_id)
        return customer
    elif token_type == "staff" or token_type == 'admin':
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        return user

