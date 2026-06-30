from sqlalchemy import BigInteger, String, Text, Enum, ForeignKey, Unicode, UnicodeText
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin

class Category(Base, TimestampMixin):
    __tablename__ = "Category"

    category_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("Category.category_id"), nullable=True)
    category_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    category_name: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(UnicodeText, nullable=True)
    status: Mapped[str] = mapped_column(Enum("active", "hidden"), nullable=False, server_default="active")

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[category_id], backref="children")
