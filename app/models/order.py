from sqlalchemy import BigInteger, String, Text, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from datetime import datetime
from app.core.database import Base
from app.core.enums import OrderStatus, PaymentStatus, ShippingMethod
from app.models.base import TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "Order"

    order_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    order_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("Customer.customer_id"), nullable=True
    )
    receiver_name: Mapped[str] = mapped_column(String(150), nullable=False)
    receiver_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    shipping_address: Mapped[str] = mapped_column(String(500), nullable=False)
    shipping_method: Mapped[ShippingMethod] = mapped_column(
        Enum(ShippingMethod), nullable=True, default=ShippingMethod.standard
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_method: Mapped[str] = mapped_column(
        Enum("cod", "bank_transfer", "online"), nullable=False
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), nullable=False, server_default="pending"
    )
    voucher_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("Voucher.voucher_id"), nullable=True
    )
    voucher_code_snapshot: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    subtotal_amount: Mapped[float] = mapped_column(Numeric(15, 0), nullable=False)
    voucher_discount_amount: Mapped[float] = mapped_column(
        Numeric(15, 0), nullable=False, server_default="0"
    )
    shipping_fee: Mapped[float] = mapped_column(
        Numeric(15, 0), nullable=False, server_default="0"
    )
    total_amount: Mapped[float] = mapped_column(Numeric(15, 0), nullable=False)
    order_status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        nullable=False,
        server_default="pending",
        index=True,
    )
    cancelled_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    details: Mapped[list["OrderDetail"]] = relationship(
        "OrderDetail", back_populates="order"
    )
    status_logs: Mapped[list["OrderStatusLog"]] = relationship(
        "OrderStatusLog", back_populates="order", order_by="OrderStatusLog.changed_at"
    )
    voucher: Mapped[Optional["Voucher"]] = relationship("Voucher")
