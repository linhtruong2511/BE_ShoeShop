# Kế Hoạch Triển Khai Backend (ShoeShop)

Tài liệu này cung cấp kế hoạch triển khai chi tiết cho hệ thống backend dựa trên các tài liệu thiết kế kiến trúc (`backend_design.md`, `database_design.md`, `api_design.md`). Kế hoạch được chia thành các giai đoạn cụ thể với checklist rõ ràng để dễ dàng theo dõi tiến độ.

## User Review Required

> [!IMPORTANT]
> Vui lòng xem xét các quyết định sau:
> - Kiến trúc đã được chốt sử dụng **Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2, và SQL Server 2022**. Đảm bảo môi trường phát triển đã sẵn sàng SQL Server 2022.
> - Yêu cầu thiết lập các dịch vụ đám mây: **Azure Blob Storage** (cho lưu trữ hình ảnh) và **Redis** (cho cache, session). Cần có account Azure để bắt đầu giai đoạn 2. (User: Tạm thời chưa cần thiết lập azure và redis)
> - Kế hoạch này tập trung vào backend. Việc tích hợp với Frontend (qua file `fe_be_contract.md`) sẽ diễn ra song song khi các API cơ bản (Giai đoạn 1 & 2) hoàn thiện. 

## Open Questions

> [!WARNING]
> - Có cần thiết lập môi trường CI/CD (GitHub Actions/GitLab CI) ngay từ Giai đoạn 1 hay đợi sau khi có Core Business?
> - Việc cấp quyền Admin/Staff sẽ được tạo sẵn (seed data) khi chạy database migration, hay có luồng đăng ký riêng cho nội bộ?
> - Các dịch vụ gửi mail (SMTP) sẽ dùng dịch vụ nào (SendGrid, Mailgun, hay Gmail SMTP) trong môi trường staging/production?

## Proposed Changes

### Giai đoạn 1 — Foundation (Thiết lập nền tảng & Kiến trúc cơ bản)

Giai đoạn này tập trung vào việc tạo cấu trúc dự án, kết nối CSDL và các module cơ bản nhất (Auth, Brand, Category).

- [ ] Khởi tạo dự án
  - [ ] Thiết lập `pyproject.toml` với Poetry.
  - [ ] Cài đặt các thư viện: FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic, v.v.
  - [ ] Thiết lập cấu trúc thư mục (app/models, app/routers, app/schemas, app/services, app/core...).
- [ ] Cấu hình cốt lõi (`app/core` & `app/config.py`)
  - [ ] Tạo file `.env` và `config.py` đọc biến môi trường.
  - [ ] Cấu hình kết nối SQL Server (pyodbc/aioodbc) trong `database.py`.
  - [ ] Cấu hình Redis client (`redis.py`).
  - [ ] Thiết lập Base Exception, BusinessException và error handlers.
  - [ ] Thiết lập Logging (Loguru) và Request Middleware (CORS, X-Request-Id).
- [ ] Models & Database Migrations (Alembic)
  - [ ] Định nghĩa `Base` model và `TimestampMixin`.
  - [ ] Khởi tạo Alembic, cấu hình `alembic/env.py`.
  - [ ] Viết toàn bộ SQLAlchemy models (`User`, `Customer`, `Brand`, `Category`, v.v.).
  - [ ] Chạy initial migration (`alembic revision --autogenerate` & `alembic upgrade head`).
- [ ] Auth Module
  - [ ] Viết hàm mã hoá/giải mã password (`passlib`).
  - [ ] Viết hàm tạo và giải mã JWT token (`python-jose`).
  - [ ] Xây dựng Dependencies phân quyền: `get_current_customer`, `get_current_staff`, `require_admin`, `get_optional_customer`.
  - [ ] Tạo Auth API routers (Login, Register cho Customer; Login cho Staff).
- [ ] Brand & Category Modules
  - [ ] Xây dựng Schemas, Repositories, Services cho Brand và Category.
  - [ ] Xây dựng Routers CRUD cho Admin và Public list (có Redis caching).

---

### Giai đoạn 2 — Core Business (Sản phẩm, Kho & Giỏ hàng)

Xây dựng logic nghiệp vụ lõi về sản phẩm, biến thể (SKU), quản lý hình ảnh và giỏ hàng.

- [ ] Product Module (Kiến trúc 3 cấp)
  - [ ] Xây dựng logic cho `Product` (thông tin chung).
  - [ ] Xây dựng logic cho `ProductColor` (màu sắc, giá, giảm giá).
  - [ ] Xây dựng logic cho `ProductSku` (kích cỡ, số lượng tồn, barcode).
  - [ ] Tạo Public APIs (tìm kiếm, lọc, chi tiết sản phẩm).
  - [ ] Tạo Admin APIs (CRUD toàn diện sản phẩm).
- [ ] Product Image Upload & Storage
  - [ ] Tích hợp Azure Blob Storage client (`StorageService`).
  - [ ] Xử lý ảnh bằng `Pillow` (resize, convert to WebP, compress).
  - [ ] Tạo API upload ảnh gắn với từng ProductColor.
- [ ] Stock Module
  - [ ] Xây dựng `StockService` xử lý điều chỉnh kho an toàn (cộng/trừ kho).
  - [ ] Lưu vết lịch sử xuất/nhập kho (`StockLog`).
- [ ] Cart Module
  - [ ] Quản lý giỏ hàng Guest (lưu bằng session_id trong Redis/DB) và Customer (liên kết account).
  - [ ] Merge giỏ hàng khi Guest đăng nhập thành Customer.
  - [ ] APIs thêm/sửa/xoá sản phẩm khỏi giỏ hàng.
- [ ] Voucher Module
  - [ ] Admin CRUD voucher (loại giảm giá, điều kiện áp dụng, số lượng).
  - [ ] Xây dựng logic validate voucher khi khách hàng thêm vào giỏ hàng.

---

### Giai đoạn 3 — Order Flow (Luồng đặt hàng & Đổi trả)

Xử lý luồng đặt hàng phức tạp, giao dịch cơ sở dữ liệu và thanh toán.

- [ ] Order Module (Checkout & Transaction)
  - [ ] Viết `OrderService.create_order` thực hiện trong 1 Database Transaction:
    - Khoá SKU (`WITH UPDLOCK` / `with_for_update()`).
    - Tính toán giá tiền (discount, shipping_fee, voucher_discount).
    - Tạo `Order` và các `OrderDetail`.
    - Trừ tồn kho qua `StockService`.
    - Ghi nhận sử dụng voucher (`VoucherUsage`).
    - Đánh dấu Cart đã checkout.
  - [ ] Customer Order APIs (Xem lịch sử đơn, chi tiết đơn, hủy đơn).
  - [ ] Admin Order APIs (Xử lý đơn hàng, cập nhật trạng thái đơn).
  - [ ] Xây dựng luồng lịch sử trạng thái đơn hàng (`OrderStatusLog`).
- [ ] Return Module (Yêu cầu đổi trả)
  - [ ] Customer API tạo yêu cầu đổi/trả hàng.
  - [ ] Admin API duyệt/từ chối yêu cầu, xử lý nhập kho lại (return to stock).
- [ ] Audit Logging
  - [ ] Viết background task / interceptor ghi nhận các thao tác quan trọng của Admin vào `AuditLog`.
- [ ] Email Notification
  - [ ] Thiết lập `fastapi-mail`.
  - [ ] Xây dựng template gửi email xác nhận đơn hàng, thay đổi trạng thái (chạy bất đồng bộ).

---

### Giai đoạn 4 — Reporting, Polish & Deployment (Báo cáo, Tối ưu & Triển khai)

Hoàn thiện hệ thống, chuẩn bị đưa lên môi trường thật.

- [ ] Report & Analytics Module (Cho Admin)
  - [ ] API thống kê doanh thu theo thời gian.
  - [ ] API thống kê sản phẩm bán chạy (best-sellers).
  - [ ] API báo cáo tồn kho tổng quan.
- [ ] Security & Performance Tuning
  - [ ] Thêm Rate limiting (slowapi) cho các endpoint nhạy cảm (login, register).
  - [ ] Áp dụng Redis caching triệt để cho các query lấy danh sách danh mục, cấu hình, chi tiết sản phẩm.
  - [ ] Review các câu query `SQLAlchemy` để tránh N+1 problem (`selectinload`, `joinedload`).
- [ ] Documentation & Testing
  - [ ] Tinh chỉnh Pydantic models để sinh Swagger UI/ReDoc đẹp và rõ ràng.
  - [ ] Cấu hình `pytest`. Viết Unit test cho các services lõi (`OrderService`, `StockService`, `VoucherService`).
  - [ ] Viết E2E test cho luồng Authentication và Checkout.
- [ ] Deployment
  - [ ] Viết Dockerfile tối ưu (đa stage, MS ODBC driver, Uvicorn/Gunicorn workers).
  - [ ] Viết `docker-compose.yml` (bao gồm SQL Server, Redis, Backend app) cho môi trường dev/staging.
  - [ ] Test toàn bộ luồng trên môi trường staging trước khi nối với Frontend.

## Verification Plan

- **Automated Tests**: Chạy toàn bộ pytest suite sau mỗi giai đoạn:
  `pytest tests/ -v --asyncio-mode=auto`
- **Linter & Formatter**: Chạy ruff và black để đảm bảo chuẩn code:
  `ruff check app/ && black app/`
- **Manual Verification**:
  - Dev sẽ cung cấp Swagger URL (`http://localhost:8000/docs`) để Frontend test các APIs.
  - Sử dụng công cụ (Postman/Bruno) chạy file collection test luồng từ đầu (Đăng ký -> Tạo giỏ hàng -> Thêm Voucher -> Đặt hàng -> Admin duyệt).
