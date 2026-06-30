from fastapi import APIRouter
from app.routers.v1.admin import brand, category, product, voucher, stock, order, return_request, report, upload, audit, user, customer

admin_router = APIRouter()
admin_router.include_router(brand.router)
admin_router.include_router(category.router)
admin_router.include_router(product.router)
admin_router.include_router(voucher.router)
admin_router.include_router(stock.router)
admin_router.include_router(order.router)
admin_router.include_router(return_request.router)
admin_router.include_router(report.router)
admin_router.include_router(upload.router)
admin_router.include_router(audit.router)
admin_router.include_router(user.router)
admin_router.include_router(customer.router)
