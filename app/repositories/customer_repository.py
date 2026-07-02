from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.customer import Customer

class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: AsyncSession):
        super().__init__(Customer, db)

    async def get_by_email(self, email: str) -> Customer | None:
        result = await self.db.execute(select(Customer).where(Customer.email == email))
        return result.scalars().first()

    async def get_by_phone(self, phone: str) -> Customer | None:
        result = await self.db.execute(select(Customer).where(Customer.phone == phone))
        return result.scalars().first()

    async def get_customers_paginated(
        self, page: int, limit: int, search: str | None = None, status: str | None = None
    ) -> tuple[list[Customer], int]:
        from sqlalchemy import func, or_
        query = select(Customer)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Customer.email.ilike(search_term),
                    Customer.full_name.ilike(search_term),
                    Customer.phone.ilike(search_term)
                )
            )
            
        if status:
            query = query.where(Customer.status == status)
            
        total_stmt = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        query = query.order_by(Customer.created_at.desc()).offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        
        return items, total

    async def update_status(self, customer_id: int, status: str) -> Customer | None:
        customer = await self.get_by_id(customer_id)
        if customer:
            customer.status = status
            await self.db.commit()
            await self.db.refresh(customer)
        return customer

    async def update_customer(self, customer_id: int, update_data: dict) -> Customer | None:
        customer = await self.get_by_id(customer_id)
        if customer:
            for key, value in update_data.items():
                setattr(customer, key, value)
            await self.db.commit()
            await self.db.refresh(customer)
        return customer
        
    async def get_customer_with_stats(self, customer_id: int):
        from sqlalchemy import func
        from app.models.order import Order
        customer = await self.get_by_id(customer_id)
        if not customer:
            return None
            
        # Get stats
        stats_query = select(
            func.count(Order.order_id).label("total_orders"),
            func.sum(Order.total_amount).label("total_spent")
        ).where(Order.customer_id == customer_id, Order.order_status == 'completed')
        
        result = await self.db.execute(stats_query)
        stats = result.first()
        
        return {
            "customer": customer,
            "stats": {
                "total_orders": stats.total_orders or 0,
                "total_spent": float(stats.total_spent or 0)
            }
        }
