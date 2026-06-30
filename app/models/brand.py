from sqlalchemy import BigInteger, String, Text, Enum, Unicode, UnicodeText
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.core.database import Base
from app.core.enums import BrandStatus
from app.models.base import TimestampMixin


class Brand(Base, TimestampMixin):
    __tablename__ = "Brand"

    brand_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    brand_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    brand_name: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(UnicodeText, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[BrandStatus] = mapped_column(
        Enum(BrandStatus), nullable=False, server_default="active"
    )

    products: Mapped[list["Product"]] = relationship("Product", back_populates="brand")
