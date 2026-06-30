from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, inspect, func
from app.core.database import Base

from app.models.product import Product
from app.models.product_color import ProductColor

from sqlalchemy.orm import selectinload

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        return await self.db.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[ModelType], int]:
        pk = inspect(self.model).primary_key[0]
        
        count_stmt = select(func.count()).select_from(self.model)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        result = await self.db.execute(select(self.model)
                                    .order_by(pk)
                                    .offset(skip)
                                    .limit(limit))
        items = list(result.scalars().all())
        
        return items, total

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        return db_obj

    async def delete(self, id: Any) -> bool:
        obj = await self.db.get(self.model, id)
        if obj:
            await self.db.delete(obj)
            return True
        return False
