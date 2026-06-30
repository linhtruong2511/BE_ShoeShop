from sqlalchemy import BigInteger, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from app.models.base import TimestampMixin

class ReturnItem(Base, TimestampMixin):
    __tablename__ = "ReturnItem"

    return_item_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    return_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ReturnRequest.return_id"), nullable=False, index=True)
    order_detail_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("OrderDetail.order_detail_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    condition: Mapped[str] = mapped_column(Enum("intact", "defective", "wrong_item"), nullable=False)

    # Relationships
    return_request: Mapped["ReturnRequest"] = relationship("ReturnRequest", back_populates="items")
    order_detail: Mapped["OrderDetail"] = relationship("OrderDetail")
