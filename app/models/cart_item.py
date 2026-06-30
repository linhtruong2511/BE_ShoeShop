from sqlalchemy import BigInteger, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from app.models.base import TimestampMixin
class CartItem(Base, TimestampMixin):
    __tablename__ = "CartItem"

    cart_item_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("Cart.cart_id"), nullable=False, index=True)
    sku_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ProductSku.sku_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")


    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    sku: Mapped["ProductSku"] = relationship("ProductSku")

    @property
    def sku_code(self) -> str:
        return self.sku.sku_code if self.sku else ""

    @property
    def product_name(self) -> str:
        return self.sku.color.product.product_name if (self.sku and self.sku.color and self.sku.color.product) else ""

    @property
    def brand_name(self) -> str:
        return self.sku.color.product.brand.brand_name if (self.sku and self.sku.color and self.sku.color.product and self.sku.color.product.brand) else ""


    @property
    def color_name(self) -> str:
        return self.sku.color.color_name if (self.sku and self.sku.color) else ""

    @property
    def size(self) -> str:
        return self.sku.size if self.sku else ""

    @property
    def image_url(self) -> str:
        if self.sku and self.sku.color and self.sku.color.images:
            for img in self.sku.color.images:
                if img.is_main:
                    return img.image_url
            return self.sku.color.images[0].image_url
        return ""

    @property
    def unit_price(self) -> float:
        return float(self.sku.color.price) if (self.sku and self.sku.color) else 0.0

    @property
    def discount_type(self) -> str:
        return self.sku.color.discount_type if (self.sku and self.sku.color) else "none"

    @property
    def discount_value(self) -> float:
        return float(self.sku.color.discount_value) if (self.sku and self.sku.color) else 0.0

    @property
    def discounted_price(self) -> float:
        price = self.unit_price
        dtype = self.discount_type
        val = self.discount_value
        if dtype == "percent":
            return price * (1.0 - val / 100.0)
        elif dtype in ("fixed", "amount"):
            return max(0.0, price - val)
        return price

    @property
    def line_total(self) -> float:
        return self.discounted_price * self.quantity

    @property
    def stock_quantity(self) -> int:
        return self.sku.stock_quantity if self.sku else 0

    @property
    def product_id(self) -> int:
        return self.sku.color.product_id if (self.sku and self.sku.color) else 0

    @property
    def is_available(self) -> bool:
        return (self.sku.status == "active" and self.sku.stock_quantity > 0) if self.sku else False


