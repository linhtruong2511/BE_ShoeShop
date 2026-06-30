# THIẾT KẾ KIẾN TRÚC HỆ THỐNG BACKEND - WEBSITE BÁN GIÀY

> Phiên bản: 2.0 | Ngày: 28/06/2026  
> Tài liệu tham chiếu: [database_design.md](./database_design.md) | [api_design.md](./api_design.md)  
> Ngôn ngữ: Python 3.12 | Framework: FastAPI | CSDL: SQL Server 2022

---

## MỤC LỤC
- [1. TỔNG QUAN KIẾN TRÚC](#1-tổng-quan-kiến-trúc)
- [2. CẤU TRÚC THƯ MỤC DỰ ÁN](#2-cấu-trúc-thư-mục-dự-án)
- [3. KHỞI TẠO ỨNG DỤNG](#3-khởi-tạo-ứng-dụng)
- [4. CẤU HÌNH VÀ KẾT NỐI CƠ SỞ DỮ LIỆU](#4-cấu-hình-và-kết-nối-cơ-sở-dữ-liệu)
- [5. THIẾT KẾ MODELS (SQLAlchemy)](#5-thiết-kế-models-sqlalchemy)
- [6. THIẾT KẾ SCHEMAS (Pydantic v2)](#6-thiết-kế-schemas-pydantic-v2)
- [7. THIẾT KẾ ROUTERS (FastAPI)](#7-thiết-kế-routers-fastapi)
- [8. THIẾT KẾ DEPENDENCIES (Phân quyền)](#8-thiết-kế-dependencies-phân-quyền)
- [9. THIẾT KẾ SERVICES (Business Logic)](#9-thiết-kế-services-business-logic)
- [10. XỬ LÝ EXCEPTION](#10-xử-lý-exception)
- [11. CHIẾN LƯỢC CACHE (Redis)](#11-chiến-lược-cache-redis)
- [12. DATABASE MIGRATIONS (Alembic)](#12-database-migrations-alembic)
- [13. XỬ LÝ FILE VÀ UPLOAD ẢNH](#13-xử-lý-file-và-upload-ảnh)
- [14. BẢO MẬT](#14-bảo-mật)
- [15. LOGGING](#15-logging)
- [16. BIẾN MÔI TRƯỜNG](#16-biến-môi-trường)
- [17. DEPENDENCIES & PACKAGE MANAGER (Poetry)](#17-dependencies--package-manager-poetry)
- [18. LUỒNG TRIỂN KHAI (Deployment)](#18-luồng-triển-khai-deployment)
- [19. KẾ HOẠCH PHÁT TRIỂN (Phân chia giai đoạn)](#19-kế-hoạch-phát-triển-phân-chia-giai-đoạn)
- [20. TÀI LIỆU THAM CHIẾU](#20-tài-liệu-tham-chiếu)

---

## 1. TỔNG QUAN KIẾN TRÚC

### 1.1 Kiến trúc tổng thể

Hệ thống backend được xây dựng theo mô hình **Layered Architecture** (Kiến trúc phân lớp) với **FastAPI** làm framework chính, phù hợp với quy mô SME của một website bán giày. Kiến trúc theo hướng **Repository Pattern** tách biệt rõ tầng truy cập dữ liệu khỏi tầng nghiệp vụ.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│          Trình duyệt (FE Vue.js) / Mobile / Public API          │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS / REST
┌────────────────────────▼────────────────────────────────────────┐
│                       API GATEWAY / NGINX                       │
│        (Reverse Proxy, SSL Termination, Rate Limiting)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     FASTAPI APPLICATION                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Presentation Layer                     │  │
│  │      Routers │ Dependencies │ Middleware │ Exception      │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │                   Application Layer                      │  │
│  │         Services │ Schemas (Pydantic) │ Validators       │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │                   Domain/Business Layer                  │  │
│  │         Models │ Business Rules │ Constants              │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │                 Infrastructure Layer                     │  │
│  │   SQLAlchemy Repositories │ Redis │ Storage │ Mailer     │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────────┐
          │                  │                      │
┌─────────▼──────────┐  ┌────▼────────────┐  ┌────▼────────────────┐
│   SQL Server 2022  │  │  Redis 7.x      │  │  Server Storage     │
│   (Primary DB)     │  │ (Session/Cache) │  │    (Images)         │
└────────────────────┘  └─────────────────┘  └─────────────────────┘
```

### 1.2 Lựa chọn công nghệ

| Thành phần | Công nghệ | Lý do lựa chọn |
|---|---|---|
| Runtime | **Python 3.12** | Ngôn ngữ phổ biến, hệ sinh thái AI/Data phong phú |
| Framework | **FastAPI 0.115.x** | Async-native, auto Swagger, hiệu suất cao, type hints |
| ORM | **SQLAlchemy 2.x** | Mature ORM cho Python, hỗ trợ async, SQL Server tốt |
| DB Driver | **pyodbc + aioodbc** | Driver async cho SQL Server (ODBC) |
| Database | **SQL Server 2022** | Enterprise-grade, ACID, JSON support, tích hợp Microsoft |
| Schema Validation | **Pydantic v2** | Type-safe, tích hợp native FastAPI, hiệu năng cao |
| Cache | **Redis 7.x + redis-py** | In-memory, hỗ trợ session, cache, rate limiting |
| File Storage | **Azure Blob Storage / Cloudflare R2** | Scalable, CDN-ready cho ảnh sản phẩm |
| Auth | **python-jose + passlib** | JWT encoding/decoding, bcrypt password hashing |
| Migration | **Alembic** | Database schema migration cho SQLAlchemy |
| Dependency Manager | **Poetry** | Quản lý dependencies và virtual env chuyên nghiệp |
| API Docs | **Swagger UI / ReDoc** | Tự động sinh từ Pydantic schemas (tích hợp FastAPI) |
| Mailer | **fastapi-mail** | Gửi email bất đồng bộ, hỗ trợ template |
| Process Manager | **Uvicorn + Gunicorn** | ASGI server cho FastAPI, hỗ trợ worker processes |
| Testing | **pytest + httpx** | Unit test, integration test, async test support |
| Logging | **Loguru** | Structured logging, rotation, dễ cấu hình |

---

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN

```
BE_ShoeShop/
├── app/
│   ├── main.py                         # Entry point, khởi tạo FastAPI app
│   ├── config.py                       # Pydantic Settings, đọc .env
│   │
│   ├── core/                           # Hạ tầng cốt lõi, dùng chung toàn hệ thống
│   │   ├── database.py                 # SQLAlchemy engine, async session
│   │   ├── redis.py                    # Redis client
│   │   ├── security.py                 # JWT encode/decode, password hashing
│   │   ├── dependencies.py             # FastAPI Depends() tái sử dụng
│   │   ├── exceptions.py               # BusinessException, HTTPException handlers
│   │   ├── middleware.py               # CORS, logging, request ID middleware
│   │   └── enums.py                    # Các Enum toàn hệ thống
│   │
│   ├── models/                         # SQLAlchemy ORM Models (ánh xạ bảng CSDL)
│   │   ├── base.py                     # DeclarativeBase + TimestampMixin
│   │   ├── brand.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── product_color.py
│   │   ├── product_image.py
│   │   ├── product_sku.py
│   │   ├── stock_log.py
│   │   ├── customer.py
│   │   ├── user.py
│   │   ├── cart.py
│   │   ├── cart_item.py
│   │   ├── voucher.py
│   │   ├── voucher_usage.py
│   │   ├── order.py
│   │   ├── order_detail.py
│   │   ├── order_status_log.py
│   │   ├── return_request.py
│   │   ├── return_item.py
│   │   └── audit_log.py
│   │
│   ├── schemas/                        # Pydantic Schemas (Request/Response DTOs)
│   │   ├── common.py                   # PaginationResponse, ApiResponse, PaginationParams
│   │   ├── auth.py
│   │   ├── brand.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── product_color.py
│   │   ├── product_image.py
│   │   ├── product_sku.py
│   │   ├── stock.py
│   │   ├── cart.py
│   │   ├── voucher.py
│   │   ├── order.py
│   │   └── return_request.py
│   │
│   ├── repositories/                   # Tầng truy cập CSDL (Repository Pattern)
│   │   ├── base_repository.py          # BaseRepository với CRUD chung
│   │   ├── brand_repository.py
│   │   ├── category_repository.py
│   │   ├── product_repository.py
│   │   ├── product_color_repository.py
│   │   ├── product_sku_repository.py
│   │   ├── stock_log_repository.py
│   │   ├── customer_repository.py
│   │   ├── cart_repository.py
│   │   ├── voucher_repository.py
│   │   ├── order_repository.py
│   │   └── return_repository.py
│   │
│   ├── services/                       # Tầng nghiệp vụ (Business Logic)
│   │   ├── auth_service.py
│   │   ├── brand_service.py
│   │   ├── category_service.py
│   │   ├── product_service.py
│   │   ├── product_color_service.py
│   │   ├── product_image_service.py
│   │   ├── product_sku_service.py
│   │   ├── stock_service.py
│   │   ├── cart_service.py
│   │   ├── voucher_service.py
│   │   ├── order_service.py
│   │   ├── return_service.py
│   │   ├── report_service.py
│   │   ├── audit_service.py
│   │   ├── storage_service.py          # Upload file lên Azure/R2
│   │   └── email_service.py
│   │
│   ├── routers/                        # FastAPI APIRouter (Controllers)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # /v1/auth/*
│   │   │   ├── brands.py               # /v1/brands
│   │   │   ├── categories.py           # /v1/categories
│   │   │   ├── products.py             # /v1/products
│   │   │   ├── cart.py                 # /v1/cart
│   │   │   ├── orders.py               # /v1/orders
│   │   │   └── admin/
│   │   │       ├── products.py         # /v1/admin/products
│   │   │       ├── skus.py             # /v1/admin/skus
│   │   │       ├── orders.py           # /v1/admin/orders
│   │   │       ├── returns.py          # /v1/admin/returns
│   │   │       ├── vouchers.py         # /v1/admin/vouchers
│   │   │       └── reports.py          # /v1/admin/reports
│   │
│   └── utils/
│       ├── price_calculator.py         # Tính discounted_price, line_total
│       ├── code_generator.py           # Sinh order_code, sku_code
│       ├── pagination.py               # Helper phân trang
│       └── validators.py               # Custom validators
│
├── alembic/                            # Database Migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial_schema.py
│
├── docs/
│   ├── database_design.md
│   ├── api_design.md
│   └── backend_design.md              # File này
│
├── tests/
│   ├── conftest.py                     # Fixtures, test DB setup
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_order_service.py
│   │   └── test_voucher_service.py
│   └── e2e/
│       ├── test_auth_api.py
│       ├── test_product_api.py
│       └── test_order_api.py
│
├── .env                                # Biến môi trường (không commit)
├── .env.example
├── alembic.ini
├── pyproject.toml                      # Poetry config
└── Dockerfile
```

---

## 3. KHỞI TẠO ỨNG DỤNG

### 3.1 Entry Point — `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.core.middleware import RequestLoggingMiddleware
from app.core.exceptions import register_exception_handlers
from app.routers.v1 import auth, brands, categories, products, cart, orders
from app.routers.v1.admin import products as admin_products, orders as admin_orders
from app.routers.v1.admin import vouchers, reports, returns, skus
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (cleanup nếu cần)


app = FastAPI(
    title="ShoeShop API",
    description="RESTful API cho Website Bán Giày",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
register_exception_handlers(app)

# Routers — Public
app.include_router(auth.router,       prefix="/v1/auth",        tags=["Auth"])
app.include_router(brands.router,     prefix="/v1/brands",      tags=["Brands"])
app.include_router(categories.router, prefix="/v1/categories",  tags=["Categories"])
app.include_router(products.router,   prefix="/v1/products",    tags=["Products"])
app.include_router(cart.router,       prefix="/v1/cart",        tags=["Cart"])
app.include_router(orders.router,     prefix="/v1/orders",      tags=["Orders"])

# Routers — Admin
app.include_router(admin_products.router, prefix="/v1/admin/products", tags=["Admin - Products"])
app.include_router(skus.router,           prefix="/v1/admin/skus",     tags=["Admin - SKUs"])
app.include_router(admin_orders.router,   prefix="/v1/admin/orders",   tags=["Admin - Orders"])
app.include_router(returns.router,        prefix="/v1/admin/returns",  tags=["Admin - Returns"])
app.include_router(vouchers.router,       prefix="/v1/admin/vouchers", tags=["Admin - Vouchers"])
app.include_router(reports.router,        prefix="/v1/admin/reports",  tags=["Admin - Reports"])
```

---

## 4. CẤU HÌNH VÀ KẾT NỐI CƠ SỞ DỮ LIỆU

### 4.1 Pydantic Settings — `app/config.py`

```python
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:8000"

    # SQL Server
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"
    DB_HOST: str = "localhost"
    DB_PORT: int = 1433
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mssql+aioodbc://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver={self.DB_DRIVER.replace(' ', '+')}"
            f"&TrustServerCertificate=yes"
        )

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 1440     # 24h - Customer
    JWT_STAFF_EXPIRE_MINUTES: int = 480       # 8h  - Staff/Admin
    JWT_REFRESH_EXPIRE_DAYS: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage (Local Server)
    UPLOAD_DIR: str = "static/uploads"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASS: str

    class Config:
        env_file = ".env"


settings = Settings()
```

### 4.2 Database Engine — `app/core/database.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.APP_ENV == "development"),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,         # Kiểm tra connection còn sống trước khi dùng
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI Dependency — inject async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Chạy khi startup — kiểm tra kết nối DB."""
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: c.execute("SELECT 1"))
```

---

## 5. THIẾT KẾ MODELS (SQLAlchemy)

### 5.1 Base Model với Timestamp

```python
# app/models/base.py
from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_mixin
from app.core.database import Base


@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
```

### 5.2 Ví dụ Model: Product

```python
# app/models/product.py
from sqlalchemy import Column, BigInteger, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "Product"

    product_id   = Column(BigInteger, primary_key=True, autoincrement=True)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    brand_id     = Column(BigInteger, ForeignKey("Brand.brand_id"), nullable=False)
    category_id  = Column(BigInteger, ForeignKey("Category.category_id"), nullable=False)
    description  = Column(Text, nullable=True)
    gender_target = Column(Enum("men", "women", "unisex", "kids"), nullable=True)
    status       = Column(
        Enum("active", "hidden", "discontinued"),
        nullable=False,
        server_default="active",
    )
    created_by   = Column(BigInteger, ForeignKey("User.user_id"), nullable=True)

    # Relationships
    brand    = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    colors   = relationship("ProductColor", back_populates="product", lazy="selectin")
```

### 5.3 Ví dụ Model: ProductColor

```python
# app/models/product_color.py
from sqlalchemy import Column, BigInteger, String, Numeric, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class ProductColor(Base, TimestampMixin):
    __tablename__ = "ProductColor"

    color_id       = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id     = Column(BigInteger, ForeignKey("Product.product_id"), nullable=False, index=True)
    color_code     = Column(String(50), nullable=False)
    color_name     = Column(String(100), nullable=False)
    hex_code       = Column(String(10), nullable=True)
    price          = Column(Numeric(15, 0), nullable=False)
    discount_type  = Column(Enum("none", "percent", "fixed"), nullable=False, server_default="none")
    discount_value = Column(Numeric(15, 2), nullable=False, server_default="0")
    is_default     = Column(Boolean, nullable=False, server_default="0")
    status         = Column(Enum("active", "hidden", "discontinued"), nullable=False, server_default="active")

    # Relationships
    product = relationship("Product", back_populates="colors")
    images  = relationship("ProductImage", back_populates="color", order_by="ProductImage.display_order")
    skus    = relationship("ProductSku", back_populates="color")
```

### 5.4 Ví dụ Model: Order

```python
# app/models/order.py
from sqlalchemy import Column, BigInteger, String, Text, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "Order"

    order_id                = Column(BigInteger, primary_key=True, autoincrement=True)
    order_code              = Column(String(50), unique=True, nullable=False, index=True)
    customer_id             = Column(BigInteger, ForeignKey("Customer.customer_id"), nullable=True)
    receiver_name           = Column(String(150), nullable=False)
    receiver_phone          = Column(String(20), nullable=False)
    shipping_address        = Column(String(500), nullable=False)
    note                    = Column(Text, nullable=True)
    payment_method          = Column(Enum("cod", "bank_transfer", "online"), nullable=False)
    payment_status          = Column(Enum("pending", "paid", "refunded"), nullable=False, server_default="pending")
    voucher_id              = Column(BigInteger, ForeignKey("Voucher.voucher_id"), nullable=True)
    voucher_code_snapshot   = Column(String(50), nullable=True)
    subtotal_amount         = Column(Numeric(15, 0), nullable=False)
    voucher_discount_amount = Column(Numeric(15, 0), nullable=False, server_default="0")
    shipping_fee            = Column(Numeric(15, 0), nullable=False, server_default="0")
    total_amount            = Column(Numeric(15, 0), nullable=False)
    order_status            = Column(
        Enum("pending", "confirmed", "preparing", "shipping", "completed", "cancelled"),
        nullable=False,
        server_default="pending",
        index=True,
    )
    cancelled_reason = Column(String(500), nullable=True)
    cancelled_at     = Column(DateTime, nullable=True)
    completed_at     = Column(DateTime, nullable=True)

    # Relationships
    customer      = relationship("Customer")
    details       = relationship("OrderDetail", back_populates="order")
    status_logs   = relationship("OrderStatusLog", back_populates="order", order_by="OrderStatusLog.changed_at")
    voucher       = relationship("Voucher")
```

---

## 6. THIẾT KẾ SCHEMAS (Pydantic v2)

### 6.1 Common Schemas

```python
# app/schemas/common.py
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "Thao tác thành công"


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    pagination: PaginationMeta


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"
```

### 6.2 Ví dụ Schema: Order

```python
# app/schemas/order.py
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from app.core.enums import PaymentMethod, OrderStatus


class CreateOrderRequest(BaseModel):
    receiver_name:    str           = Field(..., max_length=150)
    receiver_phone:   str           = Field(..., max_length=20)
    shipping_address: str           = Field(..., max_length=500)
    note:             Optional[str] = Field(None, max_length=1000)
    payment_method:   PaymentMethod
    shipping_method:  str           = "standard"
    voucher_code:     Optional[str] = Field(None, max_length=50)


class OrderDetailResponse(BaseModel):
    order_detail_id:         int
    product_name_snapshot:   str
    color_name_snapshot:     str
    size_snapshot:           str
    image_url_snapshot:      Optional[str]
    quantity:                int
    unit_price:              Decimal
    discount_type_snapshot:  str
    discount_value_snapshot: Decimal
    discounted_price:        Decimal
    line_total:              Decimal

    model_config = {"from_attributes": True}


class StatusHistoryItem(BaseModel):
    old_status:  Optional[str]
    new_status:  str
    note:        Optional[str]
    changed_at:  datetime


class OrderDetailFullResponse(BaseModel):
    order_id:                int
    order_code:              str
    order_status:            OrderStatus
    receiver_name:           str
    receiver_phone:          str
    shipping_address:        str
    note:                    Optional[str]
    payment_method:          PaymentMethod
    payment_status:          str
    voucher_code_snapshot:   Optional[str]
    subtotal_amount:         Decimal
    voucher_discount_amount: Decimal
    shipping_fee:            Decimal
    total_amount:            Decimal
    items:                   List[OrderDetailResponse]
    status_history:          List[StatusHistoryItem]
    created_at:              datetime

    model_config = {"from_attributes": True}
```

---

## 7. THIẾT KẾ ROUTERS (FastAPI)

### 7.1 Ví dụ Router: Products (Public)

```python
# app/routers/v1/products.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductListItemResponse, ProductDetailResponse, ProductQueryParams
from app.services.product_service import ProductService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ProductListItemResponse])
async def list_products(
    keyword:       Optional[str]  = Query(None),
    brand_id:      Optional[int]  = Query(None),
    category_id:   Optional[int]  = Query(None),
    size:          Optional[str]  = Query(None),
    min_price:     Optional[int]  = Query(None),
    max_price:     Optional[int]  = Query(None),
    in_stock:      Optional[bool] = Query(None),
    on_sale:       Optional[bool] = Query(None),
    gender_target: Optional[str]  = Query(None),
    page:          int            = Query(1, ge=1),
    limit:         int            = Query(20, ge=1, le=100),
    sort_by:       str            = Query("created_at"),
    sort_order:    str            = Query("desc"),
    db: AsyncSession              = Depends(get_db),
):
    service = ProductService(db)
    return await service.get_product_list(
        keyword=keyword, brand_id=brand_id, category_id=category_id,
        size=size, min_price=min_price, max_price=max_price,
        in_stock=in_stock, on_sale=on_sale, gender_target=gender_target,
        page=page, limit=limit, sort_by=sort_by, sort_order=sort_order,
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product_detail(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return await service.get_product_detail(product_id)
```

### 7.2 Ví dụ Router: Orders (Customer)

```python
# app/routers/v1/orders.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_customer
from app.models.customer import Customer
from app.schemas.order import CreateOrderRequest, OrderDetailFullResponse
from app.schemas.common import ApiResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.post("", response_model=ApiResponse[OrderDetailFullResponse], status_code=status.HTTP_201_CREATED)
async def create_order(
    body: CreateOrderRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    order = await service.create_order(customer_id=current_customer.customer_id, data=body)
    return ApiResponse(data=order, message="Đặt hàng thành công")


@router.get("/{order_id}", response_model=ApiResponse[OrderDetailFullResponse])
async def get_order_detail(
    order_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    order = await service.get_order_detail(order_id=order_id, customer_id=current_customer.customer_id)
    return ApiResponse(data=order)
```

---

## 8. THIẾT KẾ DEPENDENCIES (Phân quyền)

### 8.1 JWT Security — `app/core/security.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: int, token_type: str, role: Optional[str] = None, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES))
    payload = {
        "sub": str(subject),
        "type": token_type,         # "customer" | "staff"
        "exp": expire,
    }
    if role:
        payload["role"] = role      # "admin" | "staff"
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
```

### 8.2 Dependencies phân quyền — `app/core/dependencies.py`

```python
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories.customer_repository import CustomerRepository
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """🔒 Yêu cầu đăng nhập là Customer."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Chưa xác thực")
    payload = decode_access_token(credentials.credentials)
    if not payload or payload.get("type") != "customer":
        raise HTTPException(status_code=401, detail="Token không hợp lệ")
    customer = await CustomerRepository(db).get_by_id(int(payload["sub"]))
    if not customer or customer.status != "active":
        raise HTTPException(status_code=403, detail="Tài khoản bị khoá")
    return customer


async def get_current_staff(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """🔒 Yêu cầu đăng nhập là Staff hoặc Admin."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Chưa xác thực")
    payload = decode_access_token(credentials.credentials)
    if not payload or payload.get("type") != "staff":
        raise HTTPException(status_code=401, detail="Token không hợp lệ")
    user = await UserRepository(db).get_by_id(int(payload["sub"]))
    if not user or user.status != "active":
        raise HTTPException(status_code=403, detail="Tài khoản bị khoá")
    return user


def require_admin(current_user=Depends(get_current_staff)):
    """🔒 Chỉ Admin mới được truy cập."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền Admin")
    return current_user


async def get_optional_customer(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    x_session_id: Optional[str] = Header(None, alias="X-Session-Id"),
    db: AsyncSession = Depends(get_db),
):
    """🌐 Cho phép cả khách đã đăng nhập lẫn khách vãng lai (dùng session_id)."""
    if credentials:
        payload = decode_access_token(credentials.credentials)
        if payload and payload.get("type") == "customer":
            customer = await CustomerRepository(db).get_by_id(int(payload["sub"]))
            return {"customer": customer, "session_id": None}
    return {"customer": None, "session_id": x_session_id}
```

---

## 9. THIẾT KẾ SERVICES (Business Logic)

### 9.1 OrderService — Luồng tạo đơn hàng

```python
# app/services/order_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime

from app.models.order import Order
from app.models.order_detail import OrderDetail
from app.models.order_status_log import OrderStatusLog
from app.models.product_sku import ProductSku
from app.schemas.order import CreateOrderRequest
from app.services.stock_service import StockService
from app.services.voucher_service import VoucherService
from app.services.cart_service import CartService
from app.services.email_service import EmailService
from app.utils.code_generator import generate_order_code
from app.utils.price_calculator import calculate_discounted_price
from app.core.exceptions import BusinessException


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stock_svc  = StockService(db)
        self.voucher_svc = VoucherService(db)
        self.cart_svc   = CartService(db)

    async def create_order(self, customer_id: int, data: CreateOrderRequest) -> Order:
        async with self.db.begin():                        # ← Transaction bao quanh toàn bộ
            # ① Lấy giỏ hàng
            cart = await self.cart_svc.get_active_cart(customer_id=customer_id)
            if not cart or not cart.items:
                raise BusinessException("CART_EMPTY", "Giỏ hàng trống", 422)

            # ② Khoá SKU và kiểm tra tồn kho (SELECT ... WITH (UPDLOCK))
            subtotal = 0
            order_details_data = []
            for item in cart.items:
                sku = await self.db.execute(
                    select(ProductSku)
                    .where(ProductSku.sku_id == item.sku_id)
                    .with_for_update()                     # ← UPDLOCK tương đương
                )
                sku = sku.scalar_one_or_none()
                if not sku or sku.status != "active":
                    raise BusinessException("OUT_OF_STOCK", f"SKU {item.sku_id} không còn hàng", 422)
                if sku.stock_quantity < item.quantity:
                    raise BusinessException("QUANTITY_EXCEEDS_STOCK", f"Không đủ hàng cho SKU {sku.sku_code}", 422)

                discounted = calculate_discounted_price(sku.color.price, sku.color.discount_type, sku.color.discount_value)
                line_total = discounted * item.quantity
                subtotal  += line_total
                order_details_data.append((sku, item.quantity, discounted, line_total))

            # ③ Validate voucher
            voucher, voucher_discount = None, 0
            if data.voucher_code:
                voucher, voucher_discount = await self.voucher_svc.validate_voucher(
                    code=data.voucher_code, subtotal=subtotal, customer_id=customer_id
                )

            # ④ Tính phí vận chuyển
            shipping_fee = self._calc_shipping(data.shipping_method, subtotal - voucher_discount)
            total_amount = subtotal - voucher_discount + shipping_fee

            # ⑤ Tạo bản ghi Order
            order = Order(
                order_code=generate_order_code(),
                customer_id=customer_id,
                receiver_name=data.receiver_name,
                receiver_phone=data.receiver_phone,
                shipping_address=data.shipping_address,
                note=data.note,
                payment_method=data.payment_method,
                voucher_id=voucher.voucher_id if voucher else None,
                voucher_code_snapshot=data.voucher_code,
                subtotal_amount=subtotal,
                voucher_discount_amount=voucher_discount,
                shipping_fee=shipping_fee,
                total_amount=total_amount,
                order_status="pending",
            )
            self.db.add(order)
            await self.db.flush()                          # Lấy order_id

            # ⑥ Tạo OrderDetail + trừ kho
            for sku, qty, disc_price, line_total in order_details_data:
                detail = OrderDetail(
                    order_id=order.order_id,
                    sku_id=sku.sku_id,
                    sku_code_snapshot=sku.sku_code,
                    product_name_snapshot=sku.color.product.product_name,
                    color_name_snapshot=sku.color.color_name,
                    size_snapshot=sku.size,
                    image_url_snapshot=next((i.image_url for i in sku.color.images if i.is_main), None),
                    quantity=qty,
                    unit_price=sku.color.price,
                    discount_type_snapshot=sku.color.discount_type,
                    discount_value_snapshot=sku.color.discount_value,
                    discounted_price=disc_price,
                    line_total=line_total,
                )
                self.db.add(detail)
                await self.stock_svc.adjust_stock(
                    sku_id=sku.sku_id, change_quantity=-qty,
                    reason="order_export", reference_id=order.order_id
                )

            # ⑦ Ghi VoucherUsage + OrderStatusLog
            if voucher:
                await self.voucher_svc.record_usage(voucher.voucher_id, order.order_id, customer_id, voucher_discount)

            self.db.add(OrderStatusLog(order_id=order.order_id, new_status="pending"))

            # ⑧ Đánh dấu Cart: checked_out
            await self.cart_svc.mark_checked_out(cart.cart_id)
        # Commit tự động khi ra khỏi async with begin()

        # ⑨ Gửi email xác nhận (bất đồng bộ, không block)
        EmailService().send_order_confirmation(order)
        return order

    def _calc_shipping(self, method: str, total_after_discount: float) -> int:
        if method == "standard":
            return 0 if total_after_discount >= 500_000 else 30_000
        return 50_000   # express
```

### 9.2 StockService — Điều chỉnh tồn kho (Transaction an toàn)

```python
# app/services/stock_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product_sku import ProductSku
from app.models.stock_log import StockLog
from app.core.exceptions import BusinessException


class StockService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def adjust_stock(
        self,
        sku_id: int,
        change_quantity: int,
        reason: str,
        reason_note: str = None,
        reference_type: str = None,
        reference_id: int = None,
        created_by: int = None,
    ):
        sku = await self.db.get(ProductSku, sku_id)
        if not sku:
            raise BusinessException("SKU_NOT_FOUND", f"SKU {sku_id} không tồn tại", 404)

        stock_before = sku.stock_quantity
        stock_after  = stock_before + change_quantity

        if stock_after < 0:
            raise BusinessException("STOCK_CANNOT_BE_NEGATIVE", "Tồn kho không được âm", 422)

        sku.stock_quantity = stock_after
        if stock_after == 0:
            sku.status = "out_of_stock"
        elif stock_before == 0 and stock_after > 0:
            sku.status = "active"

        log = StockLog(
            sku_id=sku_id,
            change_quantity=change_quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            reason=reason,
            reason_note=reason_note,
            reference_type=reference_type,
            reference_id=reference_id,
            created_by=created_by,
        )
        self.db.add(log)
        return stock_after
```

---

## 10. XỬ LÝ EXCEPTION

### 10.1 BusinessException và Handler

```python
# app/core/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class BusinessException(Exception):
    def __init__(self, code: str, message: str, http_status: int = 422, details: dict = None):
        self.code       = code
        self.message    = message
        self.http_status = http_status
        self.details    = details or {}


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(status_code=404, content={"success": False, "error": {"code": "NOT_FOUND", "message": "Không tìm thấy tài nguyên"}})
```

---

## 11. CHIẾN LƯỢC CACHE (Redis)

### 11.1 Cấu hình Redis — `app/core/redis.py`

```python
import redis.asyncio as aioredis
from app.config import settings

redis_client: aioredis.Redis = None


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client
```

### 11.2 Các dữ liệu được cache

| Key Pattern | TTL | Dữ liệu | Khi invalidate |
|---|---|---|---|
| `brands:all` | 30 phút | Danh sách thương hiệu | Admin CRUD brand |
| `categories:tree` | 30 phút | Cây danh mục | Admin CRUD category |
| `product:{id}:detail` | 15 phút | Chi tiết sản phẩm (3 cấp) | Admin cập nhật product/color/sku |
| `session:{sid}:cart_id` | 7 ngày | Cart ID của khách vãng lai | Checkout |
| `refresh:{sub}:{type}` | 30 ngày | Hash refresh token | Logout / Refresh |
| `rate:{ip}:count` | 60 giây | Số request của IP | TTL tự hết |

---

## 12. DATABASE MIGRATIONS (Alembic)

### 12.1 Cấu hình `alembic/env.py`

```python
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.config import settings
from app.core.database import Base
from app.models import *    # Import tất cả models để Alembic nhận biết

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+aioodbc", "+pyodbc"))
target_metadata = Base.metadata
```

### 12.2 Workflow Migration

```bash
# Tạo migration mới (auto-generate từ model)
alembic revision --autogenerate -m "create_initial_schema"

# Áp dụng migration lên DB
alembic upgrade head

# Rollback migration gần nhất
alembic downgrade -1

# Kiểm tra lịch sử migration
alembic history --verbose
```

---

## 13. XỬ LÝ FILE VÀ UPLOAD ẢNH

### 13.1 Luồng upload ảnh sản phẩm

```
POST /v1/admin/products/{id}/colors/{cid}/images
Content-Type: multipart/form-data
  ↓
FastAPI UploadFile:
  - Validate Content-Type: image/jpeg | image/png | image/webp
  - Validate kích thước: tối đa 5MB / ảnh
  - Tối đa 10 ảnh / request
  ↓
Pillow (Python Image Library):
  - Resize tối đa 1200×1200px (giữ tỉ lệ)
  - Convert sang WebP để tối ưu dung lượng
  ↓
Lưu trên ổ cứng Local Server:
  - Tên file: static/uploads/products/{product_id}/{color_id}/{timestamp}-{uuid}.webp
  - Lấy URL static công khai (ví dụ: /static/products/...)
  ↓
INSERT ProductImage vào SQL Server với image_url = URL tĩnh
```

### 13.2 StorageService (Local Storage)

```python
# app/services/storage_service.py
import os
import uuid
from datetime import datetime
from app.config import settings


class StorageService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_image(self, file_bytes: bytes, product_id: int, color_id: int) -> str:
        relative_path = f"products/{product_id}/{color_id}"
        target_dir = os.path.join(self.upload_dir, relative_path)
        os.makedirs(target_dir, exist_ok=True)
        
        filename = f"{int(datetime.utcnow().timestamp())}-{uuid.uuid4().hex}.webp"
        file_path = os.path.join(target_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(file_bytes)
            
        return f"{settings.APP_URL}/static/{relative_path}/{filename}"
```

---

## 14. BẢO MẬT

| Biện pháp | Triển khai |
|---|---|
| **Password hashing** | `passlib[bcrypt]` với `rounds=12` |
| **JWT** | `python-jose` — HS256, secret từ biến môi trường |
| **Rate Limiting** | `slowapi` (Starlette) — 100 req/phút/IP cho Public APIs |
| **CORS** | `CORSMiddleware` — chỉ cho phép origin FE đã cấu hình |
| **Input Validation** | Pydantic v2 — tự động validate kiểu dữ liệu, độ dài |
| **SQL Injection** | SQLAlchemy parameterized queries — không bao giờ dùng raw string |
| **HTTPS** | Bắt buộc qua Nginx reverse proxy (TLS termination) |
| **Sensitive Data** | Không log password, token; AuditLog ghi IP |
| **SQL Server Auth** | Sử dụng SQL Login có quyền tối thiểu (không dùng `sa`) |

---

## 15. LOGGING

### 15.1 Cấu hình Loguru

```python
from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DDTHH:mm:ssZ} | {level} | {extra[request_id]} | {message}",
    level="DEBUG" if settings.APP_ENV == "development" else "INFO",
    serialize=True,     # JSON output cho production
)
logger.add(
    "logs/shoeshop_{time:YYYY-MM-DD}.log",
    rotation="00:00",   # Xoay log mỗi ngày
    retention="30 days",
    compression="zip",
    level="INFO",
)
```

### 15.2 Request Logging Middleware

```python
# app/core/middleware.py
import uuid, time
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)
            duration = round((time.time() - start_time) * 1000, 2)
            logger.info(f"{request.method} {request.url.path} {response.status_code} {duration}ms")
        response.headers["X-Request-Id"] = request_id
        return response
```

---

## 16. BIẾN MÔI TRƯỜNG

```env
# .env.example

# App
APP_ENV=development
APP_URL=https://api.shoeshop.com

# SQL Server
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_HOST=localhost
DB_PORT=1433
DB_USER=shoeshop_user
DB_PASS=StrongPassword123!
DB_NAME=ShoeShopDB

# JWT
JWT_SECRET_KEY=your_very_long_random_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=1440
JWT_STAFF_EXPIRE_MINUTES=480
JWT_REFRESH_EXPIRE_DAYS=30

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage Local
UPLOAD_DIR=static/uploads

# CORS
CORS_ORIGINS=["https://shoeshop.com","http://localhost:5173"]

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@shoeshop.com
SMTP_PASS=your_app_password
```

---

## 17. DEPENDENCIES & PACKAGE MANAGER (Poetry)

### 17.1 `pyproject.toml`

```toml
[tool.poetry]
name = "be-shoeshop"
version = "1.0.0"
description = "ShoeShop Backend API"
python = "^3.12"

[tool.poetry.dependencies]
fastapi            = "^0.115.0"
uvicorn            = { version = "^0.32.0", extras = ["standard"] }
gunicorn           = "^23.0.0"
sqlalchemy         = "^2.0.0"
aioodbc            = "^0.5.0"
pyodbc             = "^5.0.0"
alembic            = "^1.14.0"
pydantic           = "^2.10.0"
pydantic-settings  = "^2.7.0"
python-jose        = { version = "^3.3.0", extras = ["cryptography"] }
passlib            = { version = "^1.7.4", extras = ["bcrypt"] }
redis              = { version = "^5.2.0", extras = ["asyncio"] }
python-multipart   = "^0.0.20"
pillow             = "^11.0.0"
azure-storage-blob = "^12.23.0"
fastapi-mail       = "^1.4.1"
loguru             = "^0.7.0"
slowapi            = "^0.1.9"

[tool.poetry.dev-dependencies]
pytest         = "^8.0.0"
pytest-asyncio = "^0.24.0"
httpx          = "^0.27.0"
black          = "^24.0.0"
ruff           = "^0.8.0"
mypy           = "^1.13.0"
```

### 17.2 Scripts quan trọng

```bash
# Chạy ứng dụng (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Chạy ứng dụng (production — 4 workers)
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000

# Migrations
alembic revision --autogenerate -m "migration_name"
alembic upgrade head

# Testing
pytest tests/ -v --asyncio-mode=auto

# Linting & Formatting
ruff check app/
black app/
```

---

## 18. LUỒNG TRIỂN KHAI (Deployment)

### 18.1 Infrastructure Production

```
Internet
    │
    ▼
Nginx (Reverse Proxy + SSL/TLS)
    │
    ├──► FastAPI App (Gunicorn + Uvicorn Workers, 4 processes)
    │         │
    │         ├──► SQL Server 2022 (Primary DB)
    │         ├──► Redis 7.x (Cache + Session + Rate Limit)
    │         └──► Azure Blob Storage (File Storage + CDN)
    │
    └──► Static / FE (nếu self-host)
```

### 18.2 Dockerfile

```dockerfile
FROM python:3.12-slim

# Install SQL Server ODBC Driver
RUN apt-get update && apt-get install -y curl gnupg unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.0
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction

COPY . .

EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000"]
```

---

## 19. KẾ HOẠCH PHÁT TRIỂN (Phân chia giai đoạn)

### Giai đoạn 1 — Foundation (Tuần 1–2)
- [ ] Khởi tạo dự án FastAPI + Poetry + Python 3.12
- [ ] Cài đặt SQL Server, cấu hình ODBC Driver 18
- [ ] Định nghĩa SQLAlchemy Models toàn bộ bảng CSDL
- [ ] Tạo Alembic migrations và chạy lên SQL Server
- [ ] Cấu hình Redis
- [ ] AuthModule (JWT Customer + Staff/Admin, bcrypt)
- [ ] BrandModule + CategoryModule (CRUD cơ bản)

### Giai đoạn 2 — Core Business (Tuần 3–4)
- [ ] ProductModule (3 cấp: Product → Color → SKU)
- [ ] ProductImage upload (Pillow + Azure Blob Storage)
- [ ] StockModule (cập nhật tồn kho + StockLog trong transaction)
- [ ] CartModule (session + authenticated, merge cart)
- [ ] VoucherModule (validate toàn diện + CRUD Admin)

### Giai đoạn 3 — Order Flow (Tuần 5–6)
- [ ] OrderModule (tạo đơn trong transaction, vòng đời trạng thái)
- [ ] ReturnModule (yêu cầu đổi/trả, duyệt, hoàn tất kho)
- [ ] AuditModule (ghi nhật ký tự động)
- [ ] Email notification (xác nhận đơn hàng, trạng thái đơn)

### Giai đoạn 4 — Reporting & Polish (Tuần 7–8)
- [ ] ReportModule (doanh thu, tồn kho, best-sellers, voucher)
- [ ] Rate limiting (slowapi) + Security hardening
- [ ] Swagger documentation hoàn chỉnh (từ Pydantic schemas)
- [ ] Unit tests (pytest) + E2E tests (httpx)
- [ ] Performance tuning + Redis caching

---

## 20. TÀI LIỆU THAM CHIẾU

- [database_design.md](./database_design.md) — Thiết kế cơ sở dữ liệu
- [api_design.md](./api_design.md) — Thiết kế API (RESTful)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy 2.x Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
