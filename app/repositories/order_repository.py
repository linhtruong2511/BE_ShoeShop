import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import ShippingMethod
from app.models.product_image import ProductImage
from app.repositories.base_repository import BaseRepository
from app.models.order import Order
from app.models.order_detail import OrderDetail
from app.models.product_sku import ProductSku
from app.models.product_color import ProductColor
from app.models.product import Product
from app.models.order_status_log import OrderStatusLog
from app.models.voucher import Voucher
from fastapi import HTTPException


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)

    async def get_with_details(self, order_id: int) -> Order | None:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.details))
            .where(Order.order_id == order_id)
        )
        return result.scalars().first()

    async def get_all_by_customer(
        self, customer_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[Order], int]:
        count_stmt = (
            select(func.count())
            .select_from(Order)
            .where(Order.customer_id == customer_id)
        )
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
        voucher_code_snapshot = order_data.pop("voucher_code")
        order_code = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        shipping_method: ShippingMethod = order_data.pop("shipping_method")
        order = Order(
            **order_data,
            voucher_code_snapshot=voucher_code_snapshot,
            shipping_fee=30000 if shipping_method == ShippingMethod.standard else 50000,
            shipping_method=shipping_method,
            order_code=order_code,
            subtotal_amount=0,
            total_amount=0,
        )
        self.db.add(order)
        await self.db.flush()

        for detail_in in details_data:
            sku_id = detail_in["sku_id"]
            quantity = detail_in["quantity"]

            sku = await self.db.get(ProductSku, sku_id)
            if not sku:
                raise ValueError(f"SKU {sku_id} not found")

            color = await self.db.get(ProductColor, sku.color_id)

            if not color:
                raise HTTPException(400, "Product color is not found")

            product = await self.db.get(Product, color.product_id)

            unit_price = float(color.price)
            if color.discount_type == "percent":
                discount_value = unit_price * float(color.discount_value) / 100
                discounted_price = unit_price - discount_value
                line_total = discounted_price * quantity
                subtotal += line_total
            else:
                discount_value = float(color.discount_value)
                discounted_price = max(0.0, unit_price - discount_value)
                line_total = discounted_price * quantity
                subtotal += line_total
            stmt = select(ProductImage).where(
                ProductImage.color_id == color.color_id, ProductImage.is_main == True
            )
            color_images = await self.db.execute(stmt)
            color_images = color_images.scalars().first()

            if color_images:
                image_url_snapshot = color_images.image_url
            else:
                image_url_snapshot = None

            detail = OrderDetail(
                order_id=order.order_id,
                sku_id=sku_id,
                sku_code_snapshot=sku.sku_code,
                product_name_snapshot=product.product_name if product else "",
                color_name_snapshot=color.color_name,
                size_snapshot=sku.size,
                image_url_snapshot=image_url_snapshot,
                quantity=quantity,
                unit_price=unit_price,
                discount_type_snapshot=color.discount_type,
                discount_value_snapshot=color.discount_value,
                discounted_price=discounted_price,
                line_total=line_total,
            )
            self.db.add(detail)

            # Reduce stock
            sku.stock_quantity -= quantity
            self.db.add(sku)

        order.subtotal_amount = subtotal

        # Calculate voucher discount
        discount_amount = 0.0
        if voucher_code_snapshot:
            stmt = select(Voucher).where(Voucher.voucher_code == voucher_code_snapshot)
            voucher_res = await self.db.execute(stmt)
            voucher = voucher_res.scalars().first()
            if voucher:
                if voucher.status in ["active", "hidden"] and subtotal >= float(voucher.min_order_amount):
                    if voucher.discount_type == "percent":
                        discount_amount = subtotal * (float(voucher.discount_value) / 100.0)
                        if voucher.max_discount is not None:
                            discount_amount = min(discount_amount, float(voucher.max_discount))
                    else:  # fixed or amount
                        discount_amount = float(voucher.discount_value)
                    discount_amount = min(discount_amount, subtotal)
                    
                    order.voucher_discount_amount = discount_amount
                    order.voucher_id = voucher.voucher_id
                    voucher.used_count += 1
                    self.db.add(voucher)

        order.total_amount = (
            subtotal + float(order.shipping_fee) - discount_amount
        )
        self.db.add(order)

        log = OrderStatusLog(
            order_id=order.order_id, new_status="pending", note="Order created"
        )
        self.db.add(log)

        return order
