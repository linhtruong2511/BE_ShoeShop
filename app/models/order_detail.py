from sqlalchemy import BigInteger, String, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin

class OrderDetail(Base, TimestampMixin):
    __tablename__ = "OrderDetail"

    order_detail_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("Order.order_id"), nullable=False, index=True)
    sku_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ProductSku.sku_id"), nullable=False)
    sku_code_snapshot: Mapped[str] = mapped_column(String(50), nullable=False)
    product_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    color_name_snapshot: Mapped[str] = mapped_column(String(100), nullable=False)
    size_snapshot: Mapped[str] = mapped_column(String(20), nullable=False)
    image_url_snapshot: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 0), nullable=False)
    discount_type_snapshot: Mapped[str] = mapped_column(String(20), nullable=False)
    discount_value_snapshot: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    discounted_price: Mapped[float] = mapped_column(Numeric(15, 0), nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(15, 0), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="details")
    sku: Mapped["ProductSku"] = relationship("ProductSku")
