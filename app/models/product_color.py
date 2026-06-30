from sqlalchemy import BigInteger, String, Numeric, Enum as SAEnum, ForeignKey, Boolean, Unicode
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin
from enum import Enum as PyEnum

class ProductColorStatus(str, PyEnum):
    active = 'active'
    hidden = 'hidden'
    discontinued = 'discontinued'

class DiscountType(str, PyEnum):
    none = "none"
    percent = "percent"
    fixed = "fixed"
    amount = "amount"

class ProductColor(Base, TimestampMixin):
    __tablename__ = "ProductColor"

    color_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("Product.product_id"), nullable=False, index=True)
    color_code: Mapped[str] = mapped_column(String(50), nullable=False)
    color_name: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    hex_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(15, 0), nullable=False)
    discount_type: Mapped[DiscountType] = mapped_column(SAEnum(DiscountType), nullable=False, server_default=DiscountType.none.value)
    discount_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, server_default="0")
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    status: Mapped[PyEnum] = mapped_column(SAEnum(ProductColorStatus), nullable=False, server_default=ProductColorStatus.active.value)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="colors")
    images: Mapped[list["ProductImage"]] = relationship("ProductImage", back_populates="color", order_by="ProductImage.display_order")
    skus: Mapped[list["ProductSku"]] = relationship("ProductSku", back_populates="color")
