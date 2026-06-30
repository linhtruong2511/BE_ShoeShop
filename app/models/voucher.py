from sqlalchemy import BigInteger, String, Text, Numeric, Integer, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime
from app.core.database import Base
from app.core.enums import VoucherStatus
from app.models.base import TimestampMixin


class Voucher(Base, TimestampMixin):
    __tablename__ = "Voucher"

    voucher_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    voucher_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    voucher_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    discount_type: Mapped[str] = mapped_column(
        Enum("percent", "fixed", "amount"), nullable=False
    )
    discount_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    min_order_amount: Mapped[float] = mapped_column(
        Numeric(15, 0), nullable=False, server_default="0"
    )
    max_usage_per_customer: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    max_discount: Mapped[Optional[float]] = mapped_column(Numeric(15, 0), nullable=True)
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[VoucherStatus] = mapped_column(
        Enum(VoucherStatus),
        nullable=False,
        server_default="active",
    )
