from sqlalchemy import BigInteger, String, Text, Enum, ForeignKey, Unicode, UnicodeText
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "Product"

    product_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    product_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    product_name: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    brand_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("Brand.brand_id"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("Category.category_id"), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(UnicodeText, nullable=True)
    gender_target: Mapped[Optional[str]] = mapped_column(
        Enum("men", "women", "unisex", "kids"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "hidden", "discontinued"),
        nullable=False,
        server_default="active",
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("User.user_id"), nullable=True
    )

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    colors: Mapped[list["ProductColor"]] = relationship(
        "ProductColor", back_populates="product", lazy="selectin"
    )
