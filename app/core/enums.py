from enum import Enum


class VoucherStatus(str, Enum):
    active = "active"
    paused = "paused"
    hidden = "hidden"
    expired = "expired"


class BrandStatus(str, Enum):
    active = "active"
    hidden = "hidden"


class ShippingMethod(str, Enum):
    standard = "standard"
    express = "express"


class PaymentMethod(str, Enum):
    cod = "cod"
    bank_transfer = "bank_transfer"
    online = "online"


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    shipping = "shipping"
    completed = "completed"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    refunded = "refunded"


class GenderTarget(str, Enum):
    men = "men"
    women = "women"
    unisex = "unisex"
    kids = "kids"


class Status(str, Enum):
    active = "active"
    hidden = "hidden"
    discontinued = "discontinued"
    out_of_stock = "out_of_stock"


class DiscountType(str, Enum):
    none = "none"
    percent = "percent"
    fixed = "fixed"


class BaseStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class StockLogReferenceType(str, Enum):
    ORDER = "order"
    MANUAL = "manual"
    RETURN = "return"
    IMPORT = "import"
    EXPORT = "export"
