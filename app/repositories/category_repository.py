from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.category import Category

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def get_by_code(self, category_code: str) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.category_code == category_code))
        return result.scalars().first()
