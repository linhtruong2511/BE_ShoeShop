from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProductImageBase(BaseModel):
    image_id: int
    image_url: str
    is_main: bool = False
    display_order: int = 0


class ProductSkuBase(BaseModel):
    sku_id: int
    sku_code: Optional[str] = None
    size: str
    stock_quantity: int = 0
    barcode: Optional[str] = None
    status: str = "active"


class ProductColorBase(BaseModel):
    color_code: str
    color_name: str
    hex_code: Optional[str] = None
    price: float
    discount_type: str = "none"
    discount_value: float = 0.0
    is_default: bool = False
    status: str = "active"


class ProductColorCreate(ProductColorBase):
    images: List[ProductImageBase] = []
    skus: List[ProductSkuBase] = []


class ProductBase(BaseModel):
    product_code: str
    product_name: str
    brand_id: int
    category_id: int
    description: Optional[str] = None
    gender_target: Optional[str] = None
    status: str = "active"


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    product_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    gender_target: Optional[str] = None


class ProductColorUpdate(BaseModel):
    color_name: Optional[str] = None
    hex_code: Optional[str] = None
    is_default: Optional[bool] = None


class ProductPricingUpdate(BaseModel):
    price: Optional[float] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None


class ImageOrder(BaseModel):
    image_id: int
    display_order: int
    is_main: bool = False


class ProductImageReorder(BaseModel):
    images: List[ImageOrder]


class ProductSkuCreateList(BaseModel):
    skus: List[ProductSkuBase]


from pydantic import computed_field


class ProductListDefaultColor(BaseModel):
    color_id: int
    color_name: str
    price: float
    discount_type: str
    discount_value: float
    main_image_url: Optional[str] = None

    @computed_field
    @property
    def discounted_price(self) -> float:
        p = float(self.price)
        v = float(self.discount_value)
        if self.discount_type == "percent":
            return p * (1 - v / 100)
        elif self.discount_type in ("amount", "fixed"):
            return max(0, p - v)
        return p


class ProductColorWithProductSKU(ProductColorBase):
    color_id: int
    skus: List[ProductSkuBase]
    images: List[ProductImageBase]


class ProductListThreeLevelResponse(ProductBase):
    product_id: int
    brand: Optional["ProductDetailBrand"] = None
    category: Optional["ProductDetailCategory"] = None
    colors: List[ProductColorWithProductSKU]


class ProductListResponse(BaseModel):
    product_id: int
    product_name: str
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    gender_target: Optional[str] = None
    default_color: Optional[ProductListDefaultColor] = None
    has_stock: bool = False


class ProductDetailBrand(BaseModel):
    brand_id: int
    brand_name: str

    class Config:
        from_attributes = True


class ProductDetailCategory(BaseModel):
    category_id: int
    category_name: str

    class Config:
        from_attributes = True


class ProductDetailImage(BaseModel):
    image_id: int
    image_url: str
    is_main: bool
    display_order: int

    class Config:
        from_attributes = True


class ProductDetailSku(BaseModel):
    sku_id: int
    size: str
    stock_quantity: int
    status: str

    class Config:
        from_attributes = True


class ProductDetailColor(BaseModel):
    color_id: int
    color_code: str
    color_name: str
    hex_code: Optional[str] = None
    price: float
    discount_type: str
    discount_value: float
    is_default: bool
    images: List[ProductDetailImage] = []
    skus: List[ProductDetailSku] = []

    @computed_field
    @property
    def discounted_price(self) -> float:
        p = float(self.price)
        v = float(self.discount_value)
        if self.discount_type == "percent":
            return p * (1 - v / 100)
        elif self.discount_type in ("amount", "fixed"):
            return max(0, p - v)
        return p

    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    product_id: int
    product_code: str
    product_name: str
    brand: Optional[ProductDetailBrand] = None
    category: Optional[ProductDetailCategory] = None
    description: Optional[str] = None
    gender_target: Optional[str] = None
    colors: List[ProductDetailColor] = []

    class Config:
        from_attributes = True


class ProductSkuUpdateStock(BaseModel):
    stock_quantity: int
    reason: str
    reason_note: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
