from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product_sku import ProductSku
from app.models.product_color import ProductColor
from app.models.product import Product
from app.models.brand import Brand


class CartRepository(BaseRepository[Cart]):
    def __init__(self, db: AsyncSession):
        super().__init__(Cart, db)

    async def get_or_create_cart(
        self,
        customer_id: int | None = None,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> Cart:
        stmt = select(Cart).options(
            selectinload(Cart.items)
            .selectinload(CartItem.sku)
            .selectinload(ProductSku.color)
            .selectinload(ProductColor.product)
            .selectinload(Product.brand),
            selectinload(Cart.items)
            .selectinload(CartItem.sku)
            .selectinload(ProductSku.color)
            .selectinload(ProductColor.images),
        )
        if customer_id:
            stmt = stmt.where(Cart.customer_id == customer_id)
        elif user_id:
            stmt = stmt.where(Cart.user_id == user_id)
        elif session_id:
            stmt = stmt.where(Cart.session_id == session_id)
        else:
            raise ValueError("Must provide customer_id or session_id")

        result = await self.db.execute(stmt)
        cart = result.scalars().first()

        if not cart:
            cart = Cart(user_id=user_id, customer_id=customer_id, session_id=session_id)
            self.db.add(cart)
            await self.db.flush()
        return cart

    async def add_item(self, cart_id: int, sku_id: int, quantity: int) -> CartItem:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart_id, CartItem.sku_id == sku_id
        )
        result = await self.db.execute(stmt)
        item = result.scalars().first()

        if item:
            item.quantity += quantity
            self.db.add(item)
        else:
            item = CartItem(cart_id=cart_id, sku_id=sku_id, quantity=quantity)
            self.db.add(item)
        return item

    async def update_item(
        self,
        cart_id: int,
        cart_item_id: int,
        quantity: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> bool:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart_id, CartItem.cart_item_id == cart_item_id
        )
        result = await self.db.execute(stmt)
        item = result.scalars().first()
        if item:
            if quantity is not None:
                item.quantity = quantity
            if is_active is not None:
                item.is_active = is_active
            return True
        return False

    async def remove_item(self, cart_id: int, cart_item_id: int) -> bool:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart_id, CartItem.cart_item_id == cart_item_id
        )
        result = await self.db.execute(stmt)
        item = result.scalars().first()
        if item:
            await self.db.delete(item)
            return True
        return False

    async def clear_cart(self, cart_id: int):
        stmt = select(CartItem).where(CartItem.cart_id == cart_id)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        for item in items:
            await self.db.delete(item)
