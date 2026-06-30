from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartResponse, CartItemCreate
from app.models.customer import Customer
from app.models.cart import Cart
from fastapi import HTTPException
from app.repositories.product_repository import ProductRepository
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductListDefaultColor, ProductListResponse


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)

    async def get_by_code(self, product_code: str) -> Product | None:
        return await self.repo.get_by_code(product_code)

    async def get_all_with_relations(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Product], int]:
        return await self.repo.get_all_with_relations(skip, limit)

    async def get_with_details(self, product_id: int) -> Product | None:
        return await self.repo.get_with_details(product_id)

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
    ):
        products, total = await self.repo.search_products(
            keyword=keyword,
            brand_id=brand_id,
            category_id=category_id,
            color_name=color_name,
            size=size,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            on_sale=on_sale,
            gender_target=gender_target,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        result_data = []
        for p in products:
            default_color = None
            has_stock = False
            if p.colors:
                d_color = next((c for c in p.colors if c.is_default), p.colors[0])
                main_image_url = None
                if d_color.images:
                    main_img = next(
                        (img for img in d_color.images if img.is_main),
                        d_color.images[0],
                    )
                    main_image_url = main_img.image_url

                default_color = ProductListDefaultColor(
                    color_id=d_color.color_id,
                    color_name=d_color.color_name,
                    price=d_color.price,
                    discount_type=d_color.discount_type,
                    discount_value=d_color.discount_value,
                    main_image_url=main_image_url,
                )
                for c in p.colors:
                    for sku in c.skus:
                        if sku.stock_quantity > 0:
                            has_stock = True
                            break
                    if has_stock:
                        break

            result_data.append(
                ProductListResponse(
                    product_id=p.product_id,
                    product_name=p.product_name,
                    brand_name=p.brand.brand_name if p.brand else None,
                    category_name=p.category.category_name if p.category else None,
                    gender_target=p.gender_target,
                    default_color=default_color,
                    has_stock=has_stock,
                )
            )

        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        return result_data, total, total_pages

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
        return await self.repo.search_all_products(
            keyword=keyword,
            brand_id=brand_id,
            category_id=category_id,
            color_name=color_name,
            size=size,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            on_sale=on_sale,
            gender_target=gender_target,
            status=status,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def create_with_relations(
        self, product_data: dict, created_by: int
    ) -> Product:
        return await self.repo.create_with_relations(product_data, created_by)
