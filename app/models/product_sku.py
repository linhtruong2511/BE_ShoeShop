from sqlalchemy import BigInteger, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin

class ProductSku(Base, TimestampMixin):
    __tablename__ = "ProductSku"

    sku_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    color_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ProductColor.color_id"), nullable=False, index=True)
    sku_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(Enum("active", "out_of_stock", "discontinued"), nullable=False, server_default="active")

    # Relationships
    color: Mapped["ProductColor"] = relationship("ProductColor", back_populates="skus")
