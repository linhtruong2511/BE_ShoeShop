from sqlalchemy import BigInteger, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from app.models.base import TimestampMixin

class ProductImage(Base, TimestampMixin):
    __tablename__ = "ProductImage"

    image_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    color_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ProductColor.color_id"), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    # Relationships
    color: Mapped["ProductColor"] = relationship("ProductColor", back_populates="images")
