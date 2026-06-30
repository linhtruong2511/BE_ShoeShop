from sqlalchemy import BigInteger, String, Text, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from datetime import datetime
from app.core.database import Base
from app.models.base import TimestampMixin

class ReturnRequest(Base, TimestampMixin):
    __tablename__ = "ReturnRequest"

    return_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("Order.order_id"), nullable=False, unique=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("Customer.customer_id"), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Enum("pending", "approved", "rejected", "completed"), nullable=False, server_default="pending")
    refund_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 0), nullable=True)
    processed_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("User.user_id"), nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    order: Mapped["Order"] = relationship("Order")
    customer: Mapped["Customer"] = relationship("Customer")
    processor: Mapped[Optional["User"]] = relationship("User")
    items: Mapped[list["ReturnItem"]] = relationship("ReturnItem", back_populates="return_request")
