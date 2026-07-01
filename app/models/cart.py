from sqlalchemy import BigInteger, String, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.cart_item import CartItem
from app.models.customer import Customer
from app.models.user import User


class Cart(Base, TimestampMixin):
    __tablename__ = "Cart"

    cart_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("Customer.customer_id"), nullable=True, index=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("User.user_id"), nullable=True, index=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "checked_out", "abandoned"),
        nullable=False,
        server_default="active",
    )

    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    user: Mapped[Optional["User"]] = relationship("User")
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )

    applied_voucher_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )

    @property
    def summary(self) -> dict:

        if not self.items:
            return {"subtotal": 0, "item_count": 0}

        active_items = [item for item in self.items if item.is_active]
        subtotal = sum(item.line_total for item in active_items)
        return {"subtotal": subtotal, "item_count": len(active_items)}
