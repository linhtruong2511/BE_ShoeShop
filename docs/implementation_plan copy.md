# Triển khai Toàn bộ Tính năng Quản trị ShoeShop

## Bối cảnh

Sau khi phân tích kỹ cả hai tài liệu [fe_be_contract.md](file:///d:/Work/ShoeShop/BE_ShoeShop/docs/fe_be_contract.md) và [business_design.md](file:///d:/Work/ShoeShop/BE_ShoeShop/docs/business_design.md), kết hợp khảo sát chi tiết **từng file** trong cả hai codebase, kết quả cho thấy phần lớn tính năng quản trị **đã được triển khai**. Kế hoạch này tập trung vào:
1. Các module **hoàn toàn chưa có**
2. Các tính năng **đã có nhưng chưa hoàn chỉnh** (bugs, TODO, mock, thiếu validation)
3. **UX polish** cần thiết cho admin frontend

### ✅ Tình trạng hiện tại — Đã triển khai

| Module | Backend (API) | Frontend (UI) | Chi tiết |
|--------|:---:|:---:|----------|
| Quản lý sản phẩm (CRUD 3 cấp) | ✅ 13 endpoints | ✅ Full UI | Product → Color → Image → SKU |
| Quản lý đơn hàng | ✅ 4 endpoints | ✅ Full UI | Status transitions + cancel |
| Quản lý đổi/trả hàng | ✅ 3 endpoints | ✅ Tab trong Order view | Review + complete (restock TODO) |
| Quản lý voucher | ✅ 5 endpoints | ✅ Full UI | CRUD + toggle status |
| Quản lý tồn kho | ✅ 2 endpoints | ✅ Modal trong Product view | Adjust stock + view logs |
| Dashboard & Báo cáo | ✅ 4 endpoints | ✅ Dashboard view | Revenue, inventory, best-sellers, voucher stats |
| Quản lý danh mục | ✅ 3 endpoints | ❌ Chưa có view riêng | BE có POST/PUT/PATCH status |
| Quản lý thương hiệu | ✅ 3 endpoints | ❌ Chưa có view riêng | BE có POST/PUT/PATCH status |
| Audit Log | ✅ 1 endpoint (GET) | ❌ Chưa có view riêng | Model + schema + repo đã có |
| Auth (Login/Register) | ✅ Full | ✅ Có UI | LoginView, RegisterView, AdminLoginView |
| Admin Layout | N/A | ✅ Sidebar 4 mục | AdminLayout.vue với 4 menu items |

### ❌ Còn thiếu & cần hoàn thiện

| Module | Backend | Frontend | Mức độ |
|--------|---------|----------|--------|
| **Quản lý người dùng (Admin/Staff)** | ❌ Hoàn toàn thiếu | ❌ Hoàn toàn thiếu | 🔴 Cần xây mới |
| **Quản lý khách hàng** | ❌ Hoàn toàn thiếu | ❌ Hoàn toàn thiếu | 🔴 Cần xây mới |
| **FE Category view** | N/A (BE có) | ❌ Thiếu | 🟡 Chỉ cần FE |
| **FE Brand view** | N/A (BE có) | ❌ Thiếu | 🟡 Chỉ cần FE |
| **FE Audit Log view** | N/A (BE có) | ❌ Thiếu | 🟡 Chỉ cần FE |
| **Voucher update — validation** | ⚠️ Nhận raw dict, không validate | — | 🟠 Bug fix |
| **Upload auth** | ⚠️ Auth bị comment out | — | 🟠 Security fix |
| **Return complete — restock** | ⚠️ TODO | — | 🟠 Logic thiếu |
| **Voucher usages** | ⚠️ Mock (trả `[]`) | ⚠️ Service có, UI không dùng | 🟠 Chưa hoàn thiện |
| **Order detail modal (Admin)** | ✅ API có | ❌ UI chưa có | 🟡 Chỉ cần FE |
| **Pagination (Admin lists)** | ✅ BE có | ❌ FE load hết 1 lần | 🟡 Chỉ cần FE |
| **Search/Filter sản phẩm (Admin)** | ✅ BE có | ❌ FE không có search bar | 🟡 Chỉ cần FE |
| **Product edit/update UI** | ✅ API có | ❌ Service có nhưng UI thiếu | 🟡 Chỉ cần FE |
| **Image management (delete/reorder)** | ✅ API có reorder | ❌ Chỉ upload | 🟡 Chỉ cần FE |
| **Toast notifications** | — | ❌ Dùng `alert()` | 🟡 UX polish |
| **Confirm dialogs** | — | ❌ Dùng `window.confirm()` | 🟡 UX polish |
| **JWT token type validation** | ⚠️ Không phân biệt customer/staff token | — | 🟠 Security |
| **Admin sidebar navigation** | — | ⚠️ Chỉ có 4 mục (thiếu category, brand, user, audit) | 🟡 Update |
| **`useApiState` composable** | — | ⚠️ Có nhưng không view nào dùng | 🟡 Refactor |
| **`max_usage_per_customer`** | ⚠️ Schema có nhưng model thiếu | — | 🟠 Bug fix |

---

## User Review Required

> [!IMPORTANT]
> **Scope quản lý người dùng**: Hệ thống có 2 bảng tách biệt — `User` (admin/staff) và `Customer`. Plan thiết kế:
> - **Tab 1 "Nhân viên"**: Quản lý User (admin/staff) — tạo, sửa, khóa/mở khóa
> - **Tab 2 "Khách hàng"**: Xem danh sách customer, khóa/mở khóa tài khoản
> - Chỉ **Admin** có quyền truy cập module này

> [!WARNING]
> **Phát hiện lỗ hổng bảo mật**: JWT `get_current_user` hiện không validate `token.type` (customer/staff). Nghĩa là customer token có thể được dùng trên admin endpoints nếu chỉ check `get_current_user` mà không qua `get_current_admin`. Plan sẽ fix vấn đề này.

> [!WARNING]
> **Voucher update**: Endpoint `PUT /admin/vouchers/{id}` hiện nhận `dict` thay vì schema → không có validation nào. Cần tạo `VoucherUpdate` schema.

---

## Open Questions

> [!IMPORTANT]
> 1. **Admin quản lý customer scope**: Admin cần thấy được lịch sử đơn hàng + tổng chi tiêu của từng customer không? Hay chỉ cần xem thông tin cơ bản + khóa/mở khóa?
> 2. **Toast notification library**: Bạn muốn dùng thư viện nào cho toast? (vue-toastification, vue-sonner, hoặc tự build component đơn giản?)
> 3. **Mức ưu tiên**: Bạn muốn triển khai đầy đủ tất cả 4 phases hay ưu tiên Phase 1 (User management) + Phase 2 (Bug fixes) trước?

---

## Proposed Changes

Kế hoạch chia thành **4 Phase**, sắp xếp theo mức ưu tiên và dependency.

---

### Phase 1: Admin User & Customer Management (Backend + Frontend)
> 🔴 **Ưu tiên cao** — Module hoàn toàn chưa có. Theo business_design §1.3, Admin cần quản lý tài khoản.

#### Backend

##### [NEW] [admin_user_router.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/routers/v1/admin/user.py)
- `GET /admin/users` — Danh sách staff users (pagination, search theo tên/username, filter theo role + status)
- `GET /admin/users/{id}` — Chi tiết staff user
- `POST /admin/users` — Tạo tài khoản staff/admin (`{ username, password, full_name, role }`)
- `PUT /admin/users/{id}` — Cập nhật thông tin staff
- `PATCH /admin/users/{id}/status` — Khóa/mở khóa tài khoản (`{ status: "active"/"locked" }`)
- Tất cả yêu cầu `get_current_admin` dependency

##### [NEW] [admin_customer_router.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/routers/v1/admin/customer.py)
- `GET /admin/customers` — Danh sách customers (pagination, search theo tên/email/SĐT, filter theo status)
- `GET /admin/customers/{id}` — Chi tiết customer (thông tin + thống kê đơn hàng)
- `PATCH /admin/customers/{id}/status` — Khóa/mở khóa tài khoản (`{ status: "active"/"locked" }`)
- Yêu cầu `get_current_admin`

##### [MODIFY] [user_repository.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/repositories/user_repository.py)
- Thêm methods: `get_users_paginated(page, limit, search, role, status)`, `update_user()`, `update_status()`

##### [MODIFY] [customer_repository.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/repositories/customer_repository.py)
- Thêm methods: `get_customers_paginated(page, limit, search, status)`, `get_customer_with_stats()`, `update_status()`

##### [NEW] [admin_user schemas](file:///d:/Work/ShoeShop/BE_ShoeShop/app/schemas/user.py)
- Bổ sung: `UserAdminCreate`, `UserAdminUpdate`, `UserAdminListResponse`, `UserAdminDetailResponse`

##### [NEW] [admin_customer schemas](file:///d:/Work/ShoeShop/BE_ShoeShop/app/schemas/customer.py)
- Bổ sung: `CustomerAdminListResponse`, `CustomerAdminDetailResponse`, `CustomerStatsResponse`

##### [MODIFY] [admin/__init__.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/routers/v1/admin/__init__.py)
- Đăng ký `user_router` và `customer_router`

#### Frontend

##### [NEW] [user.service.ts](file:///d:/Work/ShoeShop/FE_ShoeShop/src/services/admin/user.service.ts)
- `getUsers(params)`, `getUserDetail(id)`, `createUser(data)`, `updateUser(id, data)`, `toggleUserStatus(id, data)`

##### [NEW] [customer.service.ts](file:///d:/Work/ShoeShop/FE_ShoeShop/src/services/admin/customer.service.ts)
- `getCustomers(params)`, `getCustomerDetail(id)`, `toggleCustomerStatus(id, data)`

##### [NEW] [AdminUserListView.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/views/admin/AdminUserListView.vue)
- **Tab "Nhân viên"**: Bảng staff users — username, tên, role (badge), status, ngày tạo
  - Modal tạo staff (form: username, password, tên, role)
  - Toggle khóa/mở khóa
  - Tìm kiếm + filter theo role/status
- **Tab "Khách hàng"**: Bảng customers — tên, email, SĐT, status, ngày đăng ký
  - Toggle khóa/mở khóa
  - Tìm kiếm + filter theo status

##### [MODIFY] [router/index.ts](file:///d:/Work/ShoeShop/FE_ShoeShop/src/router/index.ts)
- Thêm route `/admin/users` → `AdminUserListView.vue` với `requiresAdmin: true`

##### [MODIFY] [AdminLayout.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/components/layout/AdminLayout.vue)
- Thêm menu item "👥 Người dùng" vào sidebar (chỉ hiển thị khi `isAdmin`)

##### [MODIFY] [types/index.ts](file:///d:/Work/ShoeShop/FE_ShoeShop/src/types/index.ts)
- Thêm interfaces: `AdminUser`, `AdminUserCreate`, `AdminCustomer`, `CustomerStats`

---

### Phase 2: Khắc phục lỗi & Hoàn thiện Backend (Backend-heavy)
> 🟠 **Ưu tiên cao** — Sửa lỗi bảo mật, bugs, và logic chưa hoàn thiện.

#### Security Fixes

##### [MODIFY] [security.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/core/security.py) hoặc [dependencies.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/core/dependencies.py)
- **JWT token type validation**: `get_current_user` phải kiểm tra `token.type` và từ chối customer token trên admin endpoints
- Đảm bảo `get_current_admin` và `get_current_staff` validate token type = `staff`

##### [MODIFY] [admin/upload.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/routers/v1/admin/upload.py)
- Uncomment `Depends(get_current_admin)` — khôi phục auth cho upload endpoint

#### Bug Fixes

##### [MODIFY] [admin/voucher.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/routers/v1/admin/voucher.py)
- `PUT /admin/vouchers/{id}`: Thay `dict` bằng `VoucherUpdate` schema với full validation
- `GET /admin/vouchers/{id}/usages`: Implement logic thực (query `VoucherUsage` table) thay vì return `[]`

##### [NEW hoặc MODIFY] [VoucherUpdate schema](file:///d:/Work/ShoeShop/BE_ShoeShop/app/schemas/voucher.py)
- Thêm `VoucherUpdate` schema: `code?`, `voucher_type?`, `discount_value?`, `max_discount_amount?`, `min_order_amount?`, `usage_limit?`, `max_usage_per_customer?`, `start_date?`, `end_date?`

##### [MODIFY] [voucher model](file:///d:/Work/ShoeShop/BE_ShoeShop/app/models/voucher.py)
- Thêm field `max_usage_per_customer` nếu chưa có trong model (schema đã khai báo)
- Tạo Alembic migration nếu cần

##### [MODIFY] [admin/return_request.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/routers/v1/admin/return_request.py) hoặc [return_repository.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/repositories/return_repository.py)
- **Complete return restock logic**: Khi hoàn tất đổi trả:
  - Tăng `stock_quantity` SKU trả về
  - Giảm `stock_quantity` SKU đổi sang (nếu exchange)
  - Ghi `StockLog` cho cả hai SKU
  - Theo đúng business_design §4.4

##### [MODIFY] [admin/order.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/routers/v1/admin/order.py)
- Kiểm tra và sửa: order status update nên nhận `new_status` qua request body (schema `StatusUpdate`) thay vì query param — nhất quán với contract §3.10

#### Audit Log Integration

##### [MODIFY] [product_repository.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/repositories/product_repository.py) hoặc [admin/product.py](file:///d:/Work/ShoeShop/BE_ShoeShop/app/routers/v1/admin/product.py)
- Khi `update_pricing()`: ghi `AuditLog` với old/new price + discount values (model + repository đã có)
- Theo business_design §2.4 + NFR-08

---

### Phase 3: Hoàn thiện FE Admin Views & UX (Frontend-heavy)
> 🟡 **Ưu tiên trung bình** — Xây dựng các view còn thiếu và polish UX toàn bộ admin.

#### Các view mới cần tạo

##### [NEW] [AdminCategoryListView.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/views/admin/AdminCategoryListView.vue)
- Bảng danh sách danh mục (tên, mô tả, số SP liên kết, trạng thái)
- Modal tạo/sửa danh mục
- Toggle trạng thái active/inactive
- Search + pagination
- Gọi APIs: `POST /admin/categories`, `PUT /admin/categories/{id}`, `PATCH /admin/categories/{id}/status`

##### [NEW] [AdminBrandListView.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/views/admin/AdminBrandListView.vue)
- Bảng thương hiệu (logo, tên, số SP liên kết, trạng thái)
- Modal tạo/sửa
- Toggle trạng thái
- Search + pagination

##### [NEW] [AdminAuditLogView.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/views/admin/AdminAuditLogView.vue)
- Bảng audit logs: thời gian, người thực hiện, loại thao tác, entity, giá trị cũ → mới
- Filter theo entity_type, date range
- Pagination

##### [NEW] [category.service.ts (admin)](file:///d:/Work/ShoeShop/FE_ShoeShop/src/services/admin/category.service.ts)
- `createCategory(data)`, `updateCategory(id, data)`, `toggleCategoryStatus(id, data)`

##### [NEW] [brand.service.ts (admin)](file:///d:/Work/ShoeShop/FE_ShoeShop/src/services/admin/brand.service.ts)
- `createBrand(data)`, `updateBrand(id, data)`, `toggleBrandStatus(id, data)`

##### [NEW] [audit.service.ts](file:///d:/Work/ShoeShop/FE_ShoeShop/src/services/admin/audit.service.ts)
- `getAuditLogs(params)`

#### Hoàn thiện các view hiện có

##### [MODIFY] [AdminProductListView.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/views/admin/AdminProductListView.vue)
- Thêm **search bar** + **filter** (theo brand, category, status) — dùng API params có sẵn từ BE
- Thêm **product edit/update form** — service method `updateProduct()` đã có nhưng UI chưa có
- Thêm **image gallery management** (xem, xóa, reorder) — API reorder đã có
- Thêm **pagination component** thay vì load tất cả
- Tích hợp `useApiState` composable thay cho loading/error manual

##### [MODIFY] [AdminOrderListView.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/views/admin/AdminOrderListView.vue)
- Thêm **Order Detail modal/drawer** — API `getOrderDetail()` đã có trong service nhưng chưa dùng trong UI
- Thêm **pagination component**
- Thêm **search by order_code / phone**

##### [MODIFY] [AdminVoucherListView.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/views/admin/AdminVoucherListView.vue)
- Thêm **Edit voucher modal** — hiện chỉ tạo mới + toggle status
- Thêm **Voucher usage history modal** — service `getUsages()` có nhưng không dùng trong UI
- Thêm **pagination**

#### UX Polish toàn bộ Admin

##### [NEW] [ToastNotification.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/components/common/ToastNotification.vue)
- Component toast notification (success, error, warning, info)
- Thay thế tất cả `alert()` và `window.confirm()` trong admin views

##### [NEW] [ConfirmDialog.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/components/common/ConfirmDialog.vue)
- Confirm dialog component tái sử dụng
- Thay thế `window.confirm()` và `window.prompt()`

##### [NEW] [PaginationBar.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/components/common/PaginationBar.vue)
- Component pagination tái sử dụng cho tất cả admin tables
- Props: `page`, `totalPages`, `totalItems`, `limit`

#### Router & Layout Updates

##### [MODIFY] [router/index.ts](file:///d:/Work/ShoeShop/FE_ShoeShop/src/router/index.ts)
- Thêm routes: `/admin/categories`, `/admin/brands`, `/admin/audit-logs`, `/admin/users`

##### [MODIFY] [AdminLayout.vue](file:///d:/Work/ShoeShop/FE_ShoeShop/src/components/layout/AdminLayout.vue)
- Thêm sidebar items: Danh mục, Thương hiệu, Audit Log
- Thêm responsive hamburger menu cho mobile
- Highlight active route

---

### Phase 4: Security Hardening (Nếu cần)
> Tùy vào đánh giá rủi ro, có thể gộp vào Phase 2.

- Đã bao gồm trong Phase 2 (JWT token type validation, upload auth)
- Thêm kiểm tra: customer bị lock không thể đăng nhập
- Rate limiting cho admin login endpoint

---

## Tổng hợp File Changes

### Backend

| Loại | Số file | Danh sách |
|------|:---:|----------|
| **Mới** | 2 | `admin/user.py`, `admin/customer.py` (routers) |
| **Sửa** | ~10 | `dependencies.py`, `admin/__init__.py`, `admin/voucher.py`, `admin/upload.py`, `admin/order.py`, `admin/return_request.py`, `admin/product.py`, `user_repository.py`, `customer_repository.py`, `schemas/voucher.py`, `schemas/user.py`, `schemas/customer.py`, `models/voucher.py` |

### Frontend

| Loại | Số file | Danh sách |
|------|:---:|----------|
| **Mới** | ~10 | 3 admin views (Category, Brand, AuditLog, User), 4 admin services, 3 common components (Toast, Confirm, Pagination) |
| **Sửa** | ~7 | `router/index.ts`, `AdminLayout.vue`, `AdminProductListView.vue`, `AdminOrderListView.vue`, `AdminVoucherListView.vue`, `types/index.ts` |

---

## Verification Plan

### Automated Tests

```bash
# Backend — khởi động và verify tất cả endpoints
cd d:\Work\ShoeShop\BE_ShoeShop
python -m uvicorn app.main:app --reload
# Swagger docs: http://localhost:8000/docs
# Kiểm tra:
#   - Tất cả /admin/users + /admin/customers endpoints hoạt động
#   - Voucher update validation
#   - Return complete restock logic
#   - JWT security: customer token bị từ chối trên admin routes
```

```bash
# Frontend — khởi động dev server
cd d:\Work\ShoeShop\FE_ShoeShop
npm run dev
# http://localhost:5173
# Kiểm tra tất cả admin views mới + existing views đã được nâng cấp
```

### Manual Verification

| Phase | Kiểm tra |
|-------|----------|
| 1 | Staff management: list → create → edit → lock/unlock. Customer management: list → view → lock/unlock |
| 2 | Voucher update validation works. Return complete restocks correctly. Upload requires auth. Customer token rejected on admin APIs |
| 3 | Category/Brand views: CRUD + toggle status. AuditLog view: filter + pagination. Product search/filter. Order detail modal. Toast thay alert. Confirm dialog thay window.confirm |

### Nghiệp vụ cần verify (theo business_design.md)

| Quy tắc | Kiểm tra |
|---------|----------|
| §1.3 Vai trò | Admin toàn quyền; Staff xem đơn + xác nhận; Customer không truy cập admin |
| §2.4 Audit | Sửa giá → ghi audit log. Xem được trong Audit Log view |
| §4.3 Hủy đơn | Hoàn tồn kho + hoàn lượt voucher (đã có, verify lại) |
| §4.4 Đổi trả | Complete return → tăng stock SKU cũ, giảm stock SKU mới, ghi StockLog |
| NFR-03 | Phân quyền 3 cấp hoạt động đúng (customer token ≠ staff token) |
| NFR-08 | Audit log ghi đầy đủ: sửa giá, điều chỉnh kho, hủy đơn |
| BR-PRO-07 | Không xóa vật lý — chỉ toggle status |
