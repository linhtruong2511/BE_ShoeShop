from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.return_request import ReturnRequest
from app.models.return_item import ReturnItem

class ReturnRepository(BaseRepository[ReturnRequest]):
    def __init__(self, db: AsyncSession):
        super().__init__(ReturnRequest, db)

    async def create_return_request(self, return_data: dict, customer_id: int) -> ReturnRequest:
        items_data = return_data.pop("items", [])
        req = ReturnRequest(**return_data, customer_id=customer_id)
        self.db.add(req)
        await self.db.flush()

        for item_data in items_data:
            item = ReturnItem(**item_data, return_id=req.return_id)
            self.db.add(item)
            
        return req
