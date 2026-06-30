from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartResponse, CartItemCreate
from app.models.customer import Customer
from app.models.cart import Cart
from fastapi import HTTPException
from app.models.user import User


class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CartRepository(db)

    async def get_user_cart(
        self, current_user: Optional[Customer | User], x_session_id: Optional[str]
    ) -> Cart:
        if current_user and isinstance(current_user, Customer):
            cart = await self.repo.get_or_create_cart(
                customer_id=current_user.customer_id
            )
        elif current_user and isinstance(current_user, User):
            cart = await self.repo.get_or_create_cart(user_id=current_user.user_id)
        elif x_session_id:
            cart = await self.repo.get_or_create_cart(session_id=x_session_id)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either authorization token or X-Session-ID header is required",
            )
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def add_item(
        self,
        current_customer: Optional[Customer],
        x_session_id: Optional[str],
        item_in: CartItemCreate,
    ) -> Cart:
        cart = await self.get_user_cart(current_customer, x_session_id)
        await self.repo.add_item(
            cart_id=cart.cart_id, sku_id=item_in.sku_id, quantity=item_in.quantity
        )
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def update_item(
        self,
        current_customer: Optional[Customer],
        x_session_id: Optional[str],
        cart_item_id: int,
        quantity: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Cart:
        cart = await self.get_user_cart(current_customer, x_session_id)
        success = await self.repo.update_item(
            cart.cart_id, cart_item_id, quantity, is_active
        )
        if not success:
            raise HTTPException(status_code=404, detail="Cart item not found")
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def remove_item(
        self,
        current_customer: Optional[Customer],
        x_session_id: Optional[str],
        cart_item_id: int,
    ) -> Cart:
        cart = await self.get_user_cart(current_customer, x_session_id)
        success = await self.repo.remove_item(cart.cart_id, cart_item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cart item not found")
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def clear_cart(
        self, current_customer: Optional[Customer], x_session_id: Optional[str]
    ) -> Cart:
        cart = await self.get_user_cart(current_customer, x_session_id)
        await self.repo.clear_cart(cart.cart_id)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def apply_voucher(
        self,
        current_customer: Optional[Customer],
        x_session_id: Optional[str],
        voucher_code: str,
    ) -> Cart:
        cart = await self.get_user_cart(current_customer, x_session_id)
        cart.applied_voucher_code = voucher_code
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def remove_voucher(
        self, current_customer: Optional[Customer], x_session_id: Optional[str]
    ) -> Cart:
        cart = await self.get_user_cart(current_customer, x_session_id)
        cart.applied_voucher_code = None
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def preview_checkout(
        self,
        current_customer: Optional[Customer],
        x_session_id: Optional[str],
        checkout_info: dict,
    ) -> dict:
        cart = await self.get_user_cart(current_customer, x_session_id)
        active_items = [item for item in cart.items if item.is_active]
        subtotal = sum(item.line_total for item in active_items)
        
        discount_amount = 0.0
        if cart.applied_voucher_code:
            from app.models.voucher import Voucher
            from sqlalchemy import select
            stmt = select(Voucher).where(Voucher.voucher_code == cart.applied_voucher_code)
            voucher_res = await self.db.execute(stmt)
            voucher = voucher_res.scalars().first()
            if voucher and voucher.status in ["active", "hidden"] and subtotal >= float(voucher.min_order_amount):
                if voucher.discount_type == "percent":
                    discount_amount = subtotal * (float(voucher.discount_value) / 100.0)
                    if voucher.max_discount is not None:
                        discount_amount = min(discount_amount, float(voucher.max_discount))
                else:
                    discount_amount = float(voucher.discount_value)
                discount_amount = min(discount_amount, subtotal)
                
        return {
            "subtotal": subtotal,
            "discount": discount_amount,
            "shipping_fee": 30000,
            "total": subtotal + 30000 - discount_amount,
        }
