from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import VoucherStatus
from app.repositories.base_repository import BaseRepository
from app.models.voucher import Voucher


class VoucherRepository(BaseRepository[Voucher]):
    def __init__(self, db: AsyncSession):
        super().__init__(Voucher, db)

    async def get_by_code(self, voucher_code: str) -> Voucher | None:
        result = await self.db.execute(
            select(Voucher).where(Voucher.voucher_code == voucher_code)
        )
        return result.scalars().first()

    async def get_active_vouchers(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Voucher], int]:
        stmt = select(Voucher).where(Voucher.status == VoucherStatus.active)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(Voucher)
            .where(Voucher.status == "active")
            .order_by(Voucher.voucher_id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total
