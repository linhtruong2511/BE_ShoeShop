from typing import Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user_optional
from app.models.user import User
from app.schemas.cart import CartResponse, CartItemCreate
from app.models.customer import Customer
from app.schemas.base import BaseResponse
from app.services import CartService

router = APIRouter(prefix="/cart", tags=["carts"])


@router.get("/", response_model=BaseResponse[CartResponse])
async def get_cart(
    x_session_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Customer | User] = Depends(get_current_user_optional),
):
    service = CartService(db)
    cart = await service.get_user_cart(current_user, x_session_id)
    return BaseResponse(data=cart)


@router.post("/items", response_model=BaseResponse[CartResponse])
async def add_to_cart(
    item_in: CartItemCreate,
    x_session_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
    current_customer: Optional[Customer] = Depends(get_current_user_optional),
):
    service = CartService(db)
    cart = await service.add_item(current_customer, x_session_id, item_in)
    return BaseResponse(data=cart)


@router.patch("/items/{cart_item_id}", response_model=BaseResponse)
async def update_cart_item(
    cart_item_id: int,
    quantity: Optional[int] = None,
    is_active: Optional[bool] = None,
    x_session_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
    current_customer: Optional[Customer] = Depends(get_current_user_optional),
):
    service = CartService(db)
    await service.update_item(
        current_customer, x_session_id, cart_item_id, quantity, is_active
    )
    return BaseResponse(data=None)


@router.delete("/items/{cart_item_id}", response_model=BaseResponse)
async def delete_cart_item(
    cart_item_id: int,
    x_session_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
    current_customer: Optional[Customer] = Depends(get_current_user_optional),
):
    service = CartService(db)
    await service.remove_item(current_customer, x_session_id, cart_item_id)
    return BaseResponse(data=None)


@router.delete("/", response_model=BaseResponse)
async def clear_cart(
    x_session_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
    current_customer: Optional[Customer] = Depends(get_current_user_optional),
):
    service = CartService(db)
    await service.clear_cart(current_customer, x_session_id)
    return BaseResponse(data=None)


@router.post("/voucher", response_model=BaseResponse)
async def apply_voucher(
    voucher_code: str,
    x_session_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
    current_customer: Optional[Customer] = Depends(get_current_user_optional),
):
    service = CartService(db)
    await service.apply_voucher(current_customer, x_session_id, voucher_code)
    return BaseResponse(data={"voucher_code": voucher_code})


@router.delete("/voucher", response_model=BaseResponse)
async def remove_voucher(
    x_session_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
    current_customer: Optional[Customer] = Depends(get_current_user_optional),
):
    service = CartService(db)
    await service.remove_voucher(current_customer, x_session_id)
    return BaseResponse(data=None)


@router.post("/checkout-preview", response_model=BaseResponse)
async def preview_checkout(
    checkout_info: dict,
    x_session_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
    current_customer: Optional[Customer] = Depends(get_current_user_optional),
):
    service = CartService(db)
    result = await service.preview_checkout(
        current_customer, x_session_id, checkout_info
    )
    return BaseResponse(data=result)
