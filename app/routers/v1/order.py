from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_customer
from app.core.enums import OrderStatus
from app.models.order_status_log import OrderStatusLog
from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.schemas.order import OrderCreate, OrderDetailResponse, OrderResponse
from app.models.customer import Customer
from app.schemas.base import PaginatedResponse, PaginationMeta, BaseResponse

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def get_my_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    repo = OrderRepository(db)
    items, total = await repo.get_all_by_customer(
        current_customer.customer_id, skip=skip, limit=limit
    )
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page, limit=limit, total_items=total, total_pages=total_pages
        ),
    )


@router.get("/{order_id}", response_model=BaseResponse[OrderDetailResponse])
async def get_my_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    repo = OrderRepository(db)
    order = await repo.get_with_details(order_id)
    if not order or order.customer_id != current_customer.customer_id:
        raise HTTPException(status_code=404, detail="Order not found")
    return BaseResponse(data=order)


@router.post("/", response_model=BaseResponse[OrderResponse])
async def create_my_order(
    order_in: OrderCreate,
    x_session_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    if not x_session_id and not current_customer:
        raise HTTPException(
            status_code=400,
            detail="X-Session-ID header and customer authentication are required",
        )

    repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    try:
        cart = await cart_repo.get_or_create_cart(
            session_id=x_session_id, customer_id=current_customer.customer_id
        )
        cart.items = [i for i in cart.items if i.is_active]
        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        order_data = order_in.model_dump()
        order_data["customer_id"] = current_customer.customer_id

        # Populate details from cart
        order_data["details"] = [
            {
                "sku_id": item.sku_id,
                "quantity": item.quantity,
            }
            for item in cart.items
        ]

        order = await repo.create_order(order_data)
        await cart_repo.clear_cart(cart.cart_id)
        await db.commit()
        await db.refresh(order)

        result = await repo.get_with_details(order.order_id)
        return BaseResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{order_id}/cancel", response_model=BaseResponse)
async def cancel_my_order(
    order_id: int,
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    repo = OrderRepository(db)
    order = await repo.get_by_id(order_id)
    if not order or order.customer_id != current_customer.customer_id:
        raise HTTPException(404, "Order not found")
    if order.order_status != "pending":
        raise HTTPException(400, "Cannot cancel this order")
    order.order_status = OrderStatus.cancelled
    # Ideally revert stock and log
    order_status_log = OrderStatusLog(
        order_id=order_id,
        new_status="cancelled",
        note=f"Customer cancelled: {reason}",
    )
    db.add(order_status_log)
    await db.commit()
    return BaseResponse(data=None)


@router.post("/{order_id}/returns", response_model=BaseResponse)
async def return_my_order(
    order_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    repo = OrderRepository(db)
    order = await repo.get_by_id(order_id)
    if not order or order.customer_id != current_customer.customer_id:
        raise HTTPException(404, "Order not found")
    if order.order_status != "completed":
        raise HTTPException(400, "Can only return completed orders")
    # Add return logic here
    return BaseResponse(data=None)
