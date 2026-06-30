from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import verify_password, create_access_token
from app.core.dependencies import get_db, get_current_user
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token, LoginCustomerResponse, LoginAdminResponse
from app.schemas.user import UserResponse, UserLogin
from app.models.user import User
from app.config import settings
from app.schemas.base import BaseResponse

from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerLogin
from app.repositories.customer_repository import CustomerRepository
from app.core.security import hash_password
from app.core.dependencies import get_current_customer
from app.models.customer import Customer

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/admin/login", response_model=BaseResponse[LoginAdminResponse])
async def login_access_token(
    form_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[LoginAdminResponse]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(username=form_data.email)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif user.status != "active":
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.JWT_STAFF_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.user_id,
        token_type="staff",
        role=user.role,
        expires_delta=access_token_expires,
    )
    return BaseResponse(
        data=LoginAdminResponse(
            access_token=token,
            token_type="bearer",
            expires_in=access_token_expires.seconds // 60,
            user=UserResponse.model_validate(user),
        )
    )


@router.get("/me", response_model=BaseResponse[UserResponse])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current staff user
    """
    return BaseResponse(data=current_user)


@router.post("/register", response_model=BaseResponse[CustomerResponse])
async def register_customer(
    customer_in: CustomerCreate, db: AsyncSession = Depends(get_db)
) -> BaseResponse[CustomerResponse]:
    repo = CustomerRepository(db)

    # Check email
    existing_email = await repo.get_by_email(customer_in.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check phone if provided
    if customer_in.phone:
        existing_phone = await repo.get_by_phone(customer_in.phone)
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone already registered")

    # Hash password
    hashed_password = hash_password(customer_in.password)
    customer_data = customer_in.model_dump(exclude={"password"})
    customer_data["password_hash"] = hashed_password

    customer = await repo.create(customer_data)

    if not customer:
        raise

    await db.commit()
    await db.refresh(customer)

    response = CustomerResponse.model_validate(customer)
    return BaseResponse(data=response)


@router.post("/login/customer", response_model=BaseResponse[LoginCustomerResponse])
async def login_customer(
    form_data: CustomerLogin, db: AsyncSession = Depends(get_db)
) -> BaseResponse[LoginCustomerResponse]:
    repo = CustomerRepository(db)
    customer = await repo.get_by_email(form_data.email)

    if not customer or not verify_password(form_data.password, customer.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if customer.status != "active":
        raise HTTPException(status_code=400, detail="Inactive customer account")

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
    token = create_access_token(
        subject=customer.customer_id,
        token_type="customer",
        role="customer",
        expires_delta=access_token_expires,
    )
    return BaseResponse(
        data=LoginCustomerResponse(
            access_token=token,
            token_type="bearer",
            expires_in=access_token_expires.days // 60,
            customer=CustomerResponse.model_validate(customer),
        )
    )


@router.get("/me/customer", response_model=BaseResponse[CustomerResponse])
async def read_customer_me(current_customer: Customer = Depends(get_current_customer)):
    return BaseResponse(data=current_customer)
