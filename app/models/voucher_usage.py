from sqlalchemy import BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin

class VoucherUsage(Base, TimestampMixin):
    __tablename__ = "VoucherUsage"

    usage_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    voucher_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("Voucher.voucher_id"), nullable=False, index=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("Order.order_id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("Customer.customer_id"), nullable=False, index=True)
    discount_applied: Mapped[float] = mapped_column(Numeric(15, 0), nullable=False)

    # Relationships
    voucher: Mapped["Voucher"] = relationship("Voucher")
    order: Mapped["Order"] = relationship("Order")
    customer: Mapped["Customer"] = relationship("Customer")
