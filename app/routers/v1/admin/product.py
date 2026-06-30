from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductListThreeLevelResponse,
    ProductColorCreate,
    ProductColorUpdate,
    ProductPricingUpdate,
    ProductImageReorder,
    ProductSkuCreateList,
)
from app.models.user import User
from app.models.product_color import ProductColor
from app.models.product_sku import ProductSku
from app.models.product_image import ProductImage
from app.models.product import Product
from app.schemas.base import (
    PaginatedResponse,
    PaginationMeta,
    BaseResponse,
    StatusUpdate,
)
import uuid
import shutil
from pathlib import Path
from app.config import settings

router = APIRouter(prefix="/products", tags=["Admin - Products"])


@router.get("/", response_model=PaginatedResponse[ProductListThreeLevelResponse])
async def get_all_products_admin(
    skip: int = 0,
    limit: int = 100,
    keyword: str | None = None,
    brand_id: int | None = None,
    category_id: int | None = None,
    gender_target: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = ProductRepository(db)
    items, total = await repo.search_all_products(
        keyword=keyword,
        brand_id=brand_id,
        category_id=category_id,
        gender_target=gender_target,
        status=status,
        skip=skip,
        limit=limit,
    )
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page, limit=limit, total_items=total, total_pages=total_pages
        ),
    )


@router.post("/", response_model=BaseResponse[ProductResponse])
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = ProductRepository(db)
    existing = await repo.get_by_code(product_in.product_code)
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")

    product = await repo.create_with_relations(
        product_in.model_dump(), created_by=current_user.user_id
    )
    await db.commit()
    await db.refresh(product)
    return BaseResponse(data=product)


@router.put("/{product_id}", response_model=BaseResponse)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    await repo.update(product, product_in.model_dump(exclude_unset=True))
    await db.commit()
    return BaseResponse(data=None)


@router.patch("/{product_id}/status", response_model=BaseResponse)
async def update_product_status(
    product_id: int,
    status_data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    await repo.update(product, {"status": status_data.status})
    await db.commit()
    return BaseResponse(data=None)


@router.delete("/{product_id}", response_model=BaseResponse)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    await repo.delete(product_id)
    await db.commit()
    return BaseResponse(data=None)


@router.post("/{product_id}/colors", response_model=BaseResponse)
async def add_product_color(
    product_id: int,
    color_in: ProductColorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    color = ProductColor(
        **color_in.model_dump(exclude={"images", "skus"}), product_id=product_id
    )
    db.add(color)
    await db.commit()
    # Handle images and skus here if needed, omitted for brevity
    return BaseResponse(data={"color_id": color.color_id})


@router.put("/{product_id}/colors/{color_id}", response_model=BaseResponse)
async def update_product_color(
    product_id: int,
    color_id: int,
    color_in: ProductColorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    color = await db.get(ProductColor, color_id)
    if not color or color.product_id != product_id:
        raise HTTPException(404, "Color not found")
    for k, v in color_in.model_dump(exclude_unset=True).items():
        setattr(color, k, v)
    await db.commit()
    return BaseResponse(data=None)


@router.patch("/{product_id}/colors/{color_id}/pricing", response_model=BaseResponse)
async def update_product_color_pricing(
    product_id: int,
    color_id: int,
    pricing: ProductPricingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    from app.models.audit_log import AuditLog

    color = await db.get(ProductColor, color_id)
    if not color or color.product_id != product_id:
        raise HTTPException(404, "Color not found")

    old_pricing = {
        "price": float(color.price),
        "discount_type": color.discount_type,
        "discount_value": float(color.discount_value),
    }

    is_changed = False

    for k, v in pricing.model_dump(exclude_unset=True).items():
        if getattr(color, k) != old_pricing.get(k):
            is_changed = True
        setattr(color, k, v)

    if is_changed:
        log = AuditLog(
            user_id=current_user.user_id,
            action="UPDATE_PRICING",
            resource="ProductColor",
            resource_id=str(color_id),
            details=f"Old: {old_pricing}, New: {pricing.model_dump(exclude_unset=True)}",
        )
        db.add(log)
    await db.commit()
    return BaseResponse(data=None)


@router.patch("/{product_id}/colors/{color_id}/status", response_model=BaseResponse)
async def update_product_color_status(
    product_id: int,
    color_id: int,
    status_data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    color = await db.get(ProductColor, color_id)

    if not color or color.product_id != product_id:
        raise HTTPException(404, "Color not found")
    color.status = status_data.status
    await db.commit()
    return BaseResponse(data=None)


@router.patch("/{product_id}/colors/{color_id}/default", response_model=BaseResponse)
async def set_default_product_color(
    product_id: int,
    color_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    color = await db.get(ProductColor, color_id)
    if not color or color.product_id != product_id:
        raise HTTPException(404, "Color not found")

    from sqlalchemy import update

    # Đặt tất cả các màu khác của sản phẩm này về is_default = False
    await db.execute(
        update(ProductColor)
        .where(ProductColor.product_id == product_id)
        .values(is_default=False)
    )

    # Đặt màu hiện tại làm mặc định
    color.is_default = True
    await db.commit()
    return BaseResponse(data=None)


@router.post("/{product_id}/colors/{color_id}/images", response_model=BaseResponse)
async def add_product_color_images(
    product_id: int,
    color_id: int,
    is_main: bool = False,
    images: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):

    # Tạo thư mục lưu trữ nếu chưa có
    upload_path = Path(settings.UPLOAD_DIR) / "products"
    upload_path.mkdir(parents=True, exist_ok=True)

    for i, img in enumerate(images):
        ext = Path(img.filename).suffix if img.filename else ".jpg"
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = upload_path / unique_filename

        # Lưu file thật xuống server
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)

        # URL tương đối để frontend truy cập qua StaticFiles
        image_url = f"/static/uploads/products/{unique_filename}"

        p_img = ProductImage(
            color_id=color_id,
            image_url=image_url,
            is_main=(is_main and i == 0),
            display_order=i,
        )
        db.add(p_img)

    await db.commit()
    return BaseResponse(data=None)


@router.patch(
    "/{product_id}/colors/{color_id}/images/reorder", response_model=BaseResponse
)
async def reorder_product_color_images(
    product_id: int,
    color_id: int,
    order_data: ProductImageReorder,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    for order in order_data.images:
        img = await db.get(ProductImage, order.image_id)
        if img and img.color_id == color_id:
            img.display_order = order.display_order
            img.is_main = order.is_main
    await db.commit()
    return BaseResponse(data=None)


@router.delete(
    "/{product_id}/colors/{color_id}/images/{image_id}", response_model=BaseResponse
)
async def delete_product_color_image(
    product_id: int,
    color_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    img = await db.get(ProductImage, image_id)
    if not img or img.color_id != color_id:
        raise HTTPException(404, "Image not found")
    await db.delete(img)
    await db.commit()
    return BaseResponse(data=None)


@router.post("/{product_id}/colors/{color_id}/skus", response_model=BaseResponse)
async def add_product_color_skus(
    product_id: int,
    color_id: int,
    skus_data: ProductSkuCreateList,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    color = await db.get(ProductColor, color_id)
    product = await db.get(Product, product_id)
    for sku_in in skus_data.skus:
        sku_data = sku_in.model_dump()
        if not sku_data.get("sku_code"):
            sku_data["sku_code"] = (
                f"{product.product_code}-{color.color_code}-{sku_in.size}"
            )
        sku = ProductSku(**sku_data, color_id=color_id)
        db.add(sku)
    await db.commit()
    return BaseResponse(data=None)


@router.patch(
    "/{product_id}/colors/{color_id}/skus/{sku_id}/status", response_model=BaseResponse
)
async def update_product_sku_status(
    product_id: int,
    color_id: int,
    sku_id: int,
    status_data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    sku = await db.get(ProductSku, sku_id)
    if not sku or sku.color_id != color_id:
        raise HTTPException(404, "SKU not found")
    sku.status = status_data.status
    await db.commit()
    return BaseResponse(data=None)
