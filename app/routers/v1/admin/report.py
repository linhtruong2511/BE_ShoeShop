from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.dependencies import get_db, get_current_admin
from app.models.order import Order
from app.models.user import User
from app.schemas.base import BaseResponse

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/revenue", response_model=BaseResponse)
async def get_sales_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    from app.models.order_detail import OrderDetail
    from app.models.product_sku import ProductSku

    # Total revenue
    revenue_stmt = select(func.sum(Order.total_amount)).where(Order.payment_status == "paid", Order.order_status == "completed")
    revenue_res = await db.execute(revenue_stmt)
    total_revenue = revenue_res.scalar() or 0

    # Total orders
    orders_stmt = select(func.count(Order.order_id)).where(Order.order_status == "completed")
    orders_res = await db.execute(orders_stmt)
    total_orders = orders_res.scalar() or 0

    # Total items sold
    items_sold_stmt = (
        select(func.sum(OrderDetail.quantity))
        .select_from(OrderDetail)
        .join(Order, Order.order_id == OrderDetail.order_id)
        .where(Order.order_status == "completed")
    )
    items_sold_res = await db.execute(items_sold_stmt)
    total_items_sold = items_sold_res.scalar() or 0

    # Total low stock
    low_stock_stmt = select(func.count(ProductSku.sku_id)).where(ProductSku.stock_quantity <= 5)
    low_stock_res = await db.execute(low_stock_stmt)
    total_low_stock = low_stock_res.scalar() or 0

    return BaseResponse(data={
        "total_revenue": float(total_revenue),
        "total_orders": total_orders,
        "total_items_sold": int(total_items_sold),
        "total_low_stock": total_low_stock
    })

@router.get("/inventory", response_model=BaseResponse)
async def get_inventory_report(
    low_stock_threshold: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    from app.models.product_sku import ProductSku
    from app.models.product_color import ProductColor
    from app.models.product import Product
    
    stmt = (
        select(
            Product.product_name,
            ProductColor.color_name,
            ProductSku.size,
            ProductSku.sku_code,
            ProductSku.stock_quantity
        )
        .select_from(ProductSku)
        .join(ProductColor, ProductColor.color_id == ProductSku.color_id)
        .join(Product, Product.product_id == ProductColor.product_id)
        .where(ProductSku.stock_quantity <= low_stock_threshold)
        .order_by(ProductSku.stock_quantity.asc())
        .limit(20)
    )
    result = await db.execute(stmt)
    items = []
    for row in result:
        items.append({
            "product_name": row[0],
            "color_name": row[1],
            "size": row[2],
            "sku_code": row[3],
            "stock_quantity": row[4]
        })
    return BaseResponse(data={"items": items})

@router.get("/best-sellers", response_model=BaseResponse)
async def get_best_sellers_report(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    from app.models.order_detail import OrderDetail
    from app.models.product_sku import ProductSku
    from app.models.product_color import ProductColor
    from app.models.product import Product
    from app.models.order import Order
    
    stmt = (
        select(
            Product.product_name,
            ProductColor.color_name,
            ProductSku.size,
            ProductSku.sku_code,
            func.sum(OrderDetail.quantity).label("sold"),
            ProductColor.price
        )
        .select_from(OrderDetail)
        .join(ProductSku, ProductSku.sku_id == OrderDetail.sku_id)
        .join(Order, Order.order_id == OrderDetail.order_id)
        .join(ProductColor, ProductColor.color_id == ProductSku.color_id)
        .join(Product, Product.product_id == ProductColor.product_id)
        .where(Order.order_status == "completed")
        .group_by(
            Product.product_name,
            ProductColor.color_name,
            ProductSku.size,
            ProductSku.sku_code,
            ProductColor.price
        )
        .order_by(func.sum(OrderDetail.quantity).desc())
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    items = []
    for row in result:
        items.append({
            "product_name": row[0],
            "color_name": row[1],
            "size": row[2],
            "sku_code": row[3],
            "sold": int(row[4]),
            "price": float(row[5])
        })
    return BaseResponse(data={"items": items})

@router.get("/vouchers", response_model=BaseResponse)
async def get_vouchers_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    from app.models.voucher import Voucher
    from app.models.voucher_usage import VoucherUsage
    from app.models.order import Order

    stmt = (
        select(
            Voucher.voucher_code.label("code"),
            Voucher.discount_type.label("type"),
            func.count(VoucherUsage.usage_id).label("used"),
            func.sum(Order.voucher_discount_amount).label("discount"),
            func.sum(Order.total_amount).label("sales")
        )
        .select_from(Voucher)
        .outerjoin(VoucherUsage, VoucherUsage.voucher_id == Voucher.voucher_id)
        .outerjoin(Order, Order.order_id == VoucherUsage.order_id)
        .group_by(Voucher.voucher_code, Voucher.discount_type)
        .order_by(func.count(VoucherUsage.usage_id).desc())
    )
    result = await db.execute(stmt)
    items = []
    for row in result:
        items.append({
            "code": row[0],
            "type": row[1],
            "used": int(row[2]),
            "discount": float(row[3] or 0),
            "sales": float(row[4] or 0)
        })
    return BaseResponse(data={"items": items})
