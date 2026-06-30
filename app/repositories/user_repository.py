from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_users_paginated(
        self, page: int, limit: int, search: str | None = None, role: str | None = None, status: str | None = None
    ) -> tuple[list[User], int]:
        from sqlalchemy import func, or_
        query = select(User)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term),
                    User.phone.ilike(search_term)
                )
            )
        
        if role:
            query = query.where(User.role == role)
            
        if status:
            query = query.where(User.status == status)
            
        total_stmt = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        query = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        
        return items, total

    async def update_status(self, user_id: int, status: str) -> User | None:
        user = await self.get_by_id(user_id)
        if user:
            user.status = status
            await self.db.commit()
            await self.db.refresh(user)
        return user
