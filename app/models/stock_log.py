from sqlalchemy import BigInteger, Enum, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.core.enums import StockLogReferenceType
from app.models.base import TimestampMixin


class StockLog(Base, TimestampMixin):
    __tablename__ = "StockLog"

    log_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    sku_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ProductSku.sku_id"), nullable=False, index=True
    )
    change_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_before: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    reason_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference_type: Mapped[Optional[StockLogReferenceType]] = mapped_column(
        Enum(StockLogReferenceType),
        nullable=True,
        server_default=StockLogReferenceType.ORDER.value,
    )
    reference_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("User.user_id"), nullable=True
    )

    # Relationships
    sku: Mapped["ProductSku"] = relationship("ProductSku")
    user: Mapped[Optional["User"]] = relationship("User")
