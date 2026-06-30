from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.stock_log import StockLog
from app.models.product_sku import ProductSku

class StockRepository(BaseRepository[StockLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(StockLog, db)

    async def update_stock(self, sku_id: int, change_quantity: int, reason: str, reason_note: str = None, user_id: int = None, reference_type: str = None, reference_id: int = None) -> StockLog:
        sku = await self.db.get(ProductSku, sku_id)
        if not sku:
            raise ValueError("SKU not found")

        stock_before = sku.stock_quantity
        stock_after = stock_before + change_quantity

        if stock_after < 0:
            raise ValueError("Insufficient stock")

        sku.stock_quantity = stock_after
        self.db.add(sku)

        log = StockLog(
            sku_id=sku_id,
            change_quantity=change_quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            reason=reason,
            reason_note=reason_note,
            reference_type=reference_type,
            reference_id=reference_id,
            created_by=user_id
        )
        self.db.add(log)
        return log
