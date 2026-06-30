import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.order import Order
from app.models.order_detail import OrderDetail
from app.models.product_sku import ProductSku
from app.models.product_color import ProductColor
from app.models.product import Product
from app.models.order_status_log import OrderStatusLog
from fastapi import HTTPException

class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)

    async def get_with_details(self, order_id: int) -> Order | None:
        result = await self.db.execute(
            select(Order).options(selectinload(Order.details)).where(Order.order_id == order_id)
        )
        return result.scalars().first()

    async def get_all_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Order], int]:
        count_stmt = select(func.count()).select_from(Order).where(Order.customer_id == customer_id)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.details))
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def create_order(self, order_data: dict) -> Order:
        details_data = order_data.pop("details", [])
        
        # Calculate subtotal
        subtotal = 0.0
        voucher_code_snapshot = order_data.pop('voucher_code')
        order_code = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        order = Order(
            **order_data,
            voucher_code_snapshot=voucher_code_snapshot,
            order_code=order_code,
            subtotal_amount=0,
            total_amount=0
        )
        self.db.add(order)
        await self.db.flush()

        for detail_in in details_data:
            sku_id = detail_in["sku_id"]
            quantity = detail_in["quantity"]
            
            # In real system, we'd query SKU to get current price, product name, etc.
            # Here we simplify by using provided or querying DB.
            sku = await self.db.get(ProductSku, sku_id)
            if not sku:
                raise ValueError(f"SKU {sku_id} not found")
                
            color = await self.db.get(ProductColor, sku.color_id)

            if not color: 
                raise HTTPException(400, "Product color is not found")
            
            product = await self.db.get(Product, color.product_id)
            
            unit_price = float(color.price)
            discounted_price = unit_price - float(color.discount_value) # Simplistic
            line_total = discounted_price * quantity
            subtotal += line_total
            
            detail = OrderDetail(
                order_id=order.order_id,
                sku_id=sku_id,
                sku_code_snapshot=sku.sku_code,
                product_name_snapshot=product.product_name if product else "",
                color_name_snapshot=color.color_name,
                size_snapshot=sku.size,
                image_url_snapshot=None,
                quantity=quantity,
                unit_price=unit_price,
                discount_type_snapshot=color.discount_type,
                discount_value_snapshot=color.discount_value,
                discounted_price=discounted_price,
                line_total=line_total
            )
            self.db.add(detail)
            
            # Reduce stock
            sku.stock_quantity -= quantity
            self.db.add(sku)
            
        order.subtotal_amount = subtotal
        # In a real app we'd apply voucher discounts here
        order.total_amount = subtotal + float(order.shipping_fee) - float(order.voucher_discount_amount)
        self.db.add(order)
        
        # Log initial status
        log = OrderStatusLog(
            order_id=order.order_id,
            new_status="pending",
            note="Order created"
        )
        self.db.add(log)
        
        return order
