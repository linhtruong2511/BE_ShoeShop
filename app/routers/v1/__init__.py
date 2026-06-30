from fastapi import APIRouter
from app.routers.v1 import auth, brand, category, product, cart, order, voucher
from app.routers.v1.admin import admin_router

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(brand.router)
api_router.include_router(category.router)
api_router.include_router(product.router)
api_router.include_router(cart.router)
api_router.include_router(order.router)
api_router.include_router(voucher.router)

# Include Admin routes with prefix
api_router.include_router(admin_router, prefix="/admin")
