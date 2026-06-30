from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.voucher import Voucher

class VoucherRepository(BaseRepository[Voucher]):
    def __init__(self, db: AsyncSession):
        super().__init__(Voucher, db)

    async def get_by_code(self, voucher_code: str) -> Voucher | None:
        result = await self.db.execute(select(Voucher).where(Voucher.voucher_code == voucher_code))
        return result.scalars().first()
