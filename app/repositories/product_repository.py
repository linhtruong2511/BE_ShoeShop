from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.product import Product
from app.models.product_color import ProductColor, ProductColorStatus
from app.models.product_sku import ProductSku
from app.models.product_image import ProductImage
from sqlalchemy.orm import with_loader_criteria


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_code(self, product_code: str) -> Product | None:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.colors).selectinload(ProductColor.skus))
            .options(selectinload(Product.colors).selectinload(ProductColor.images))
            .where(Product.product_code == product_code)
        )
        return result.scalars().first()

    async def get_all_with_relations(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Product], int]:
        count_stmt = select(func.count()).select_from(Product)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.colors).selectinload(ProductColor.skus))
            .options(selectinload(Product.colors).selectinload(ProductColor.images))
            .options(selectinload(Product.brand))
            .options(selectinload(Product.category))
            .options(selectinload(Product.colors).selectinload(ProductColor.images))
            .order_by(Product.product_id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_with_details(self, product_id: int) -> Product | None:
        result = await self.db.execute(
            select(Product)
            .options(
                selectinload(Product.colors).selectinload(ProductColor.skus),
                selectinload(Product.colors).selectinload(ProductColor.images),
                selectinload(Product.brand),
                selectinload(Product.category),
                with_loader_criteria(
                    ProductColor, ProductColor.status == ProductColorStatus.active
                ),
            )
            .where(Product.product_id == product_id)
        )
        return result.scalars().first()

    async def search_products(
        self,
        keyword=None,
        brand_id=None,
        category_id=None,
        color_name=None,
        size=None,
        min_price=None,
        max_price=None,
        in_stock=None,
        on_sale=None,
        gender_target=None,
        status=None,
        skip=0,
        limit=20,
        sort_by="created_at",
        sort_order="desc",
    ) -> tuple[list[Product], int]:
        base_stmt = select(Product)

        if keyword:
            base_stmt = base_stmt.where(Product.product_name.ilike(f"%{keyword}%"))
        if brand_id:
            base_stmt = base_stmt.where(Product.brand_id == brand_id)
        if category_id:
            base_stmt = base_stmt.where(Product.category_id == category_id)
        if gender_target:
            base_stmt = base_stmt.where(Product.gender_target == gender_target)
        if status:
            base_stmt = base_stmt.where(Product.status == status)

        if (
            color_name
            or size
            or min_price
            or max_price
            or in_stock is not None
            or on_sale is not None
        ):
            base_stmt = base_stmt.join(
                ProductColor, Product.product_id == ProductColor.product_id
            )

            if color_name:
                base_stmt = base_stmt.where(
                    ProductColor.color_name.ilike(f"%{color_name}%")
                )
            if size or in_stock is not None:
                base_stmt = base_stmt.join(
                    ProductSku, ProductColor.color_id == ProductSku.color_id
                )
                if size:
                    base_stmt = base_stmt.where(ProductSku.size == size)
                if in_stock:
                    base_stmt = base_stmt.where(ProductSku.stock_quantity > 0)
            if min_price:
                base_stmt = base_stmt.where(
                    ProductColor.price >= min_price
                )  # simplified for now
            if max_price:
                base_stmt = base_stmt.where(ProductColor.price <= max_price)
            if on_sale:
                base_stmt = base_stmt.where(ProductColor.discount_value > 0)

        # Group by or distinct since joins might duplicate
        base_stmt = base_stmt.distinct()

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await self.db.execute(count_stmt)

        total = total_result.scalar() or 0

        stmt = base_stmt.options(
            selectinload(Product.colors).selectinload(ProductColor.skus),
            selectinload(Product.colors).selectinload(ProductColor.images),
            selectinload(Product.brand),
            selectinload(Product.category),
            with_loader_criteria(
                ProductColor,
                ProductColor.status == ProductColorStatus.active,
                include_aliases=True,
            ),
        )

        if sort_order == "desc":
            stmt = stmt.order_by(Product.created_at.desc())
        else:
            stmt = stmt.order_by(Product.created_at.asc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all()), total

    async def search_all_products(
        self,
        keyword=None,
        brand_id=None,
        category_id=None,
        color_name=None,
        size=None,
        min_price=None,
        max_price=None,
        in_stock=None,
        on_sale=None,
        gender_target=None,
        status=None,
        skip=0,
        limit=20,
        sort_by="created_at",
        sort_order="desc",
    ) -> tuple[list[Product], int]:
        base_stmt = select(Product)

        if keyword:
            base_stmt = base_stmt.where(Product.product_name.ilike(f"%{keyword}%"))
        if brand_id:
            base_stmt = base_stmt.where(Product.brand_id == brand_id)
        if category_id:
            base_stmt = base_stmt.where(Product.category_id == category_id)
        if gender_target:
            base_stmt = base_stmt.where(Product.gender_target == gender_target)
        if status:
            base_stmt = base_stmt.where(Product.status == status)

        if (
            color_name
            or size
            or min_price
            or max_price
            or in_stock is not None
            or on_sale is not None
        ):
            base_stmt = base_stmt.join(
                ProductColor, Product.product_id == ProductColor.product_id
            )
            if color_name:
                base_stmt = base_stmt.where(
                    ProductColor.color_name.ilike(f"%{color_name}%")
                )
            if size or in_stock is not None:
                base_stmt = base_stmt.join(
                    ProductSku, ProductColor.color_id == ProductSku.color_id
                )
                if size:
                    base_stmt = base_stmt.where(ProductSku.size == size)
                if in_stock:
                    base_stmt = base_stmt.where(ProductSku.stock_quantity > 0)
            if min_price:
                base_stmt = base_stmt.where(
                    ProductColor.price >= min_price
                )  # simplified for now
            if max_price:
                base_stmt = base_stmt.where(ProductColor.price <= max_price)
            if on_sale:
                base_stmt = base_stmt.where(ProductColor.discount_value > 0)

        # Group by or distinct since joins might duplicate
        base_stmt = base_stmt.distinct()

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = base_stmt.options(
            selectinload(Product.colors).selectinload(ProductColor.skus),
            selectinload(Product.colors).selectinload(ProductColor.images),
            selectinload(Product.brand),
            selectinload(Product.category),
        )

        if sort_order == "desc":
            stmt = stmt.order_by(Product.created_at.desc())
        else:
            stmt = stmt.order_by(Product.created_at.asc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all()), total

    async def create_with_relations(
        self, product_data: dict, created_by: int
    ) -> Product:
        colors_data = product_data.pop("colors", [])

        product = Product(**product_data, created_by=created_by)
        self.db.add(product)
        await self.db.flush()

        for color_data in colors_data:
            images_data = color_data.pop("images", [])
            skus_data = color_data.pop("skus", [])

            color = ProductColor(**color_data, product_id=product.product_id)
            self.db.add(color)
            await self.db.flush()

            for img_data in images_data:
                img = ProductImage(**img_data, color_id=color.color_id)
                self.db.add(img)

            for sku_data in skus_data:
                sku = ProductSku(**sku_data, color_id=color.color_id)
                self.db.add(sku)

        return product
