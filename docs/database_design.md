# THIẾT KẾ CƠ SỞ DỮ LIỆU - WEBSITE BÁN GIÀY

> Phiên bản: 1.0 | Ngày: 27/06/2026  
> Quy ước đặt tên: Tên bảng dùng **CamelCase**, tên thuộc tính dùng **snake_case**

---

## MỤC LỤC
- [1. QUY ƯỚC THIẾT KẾ](#1-quy-ước-thiết-kế)
- [2. SƠ ĐỒ QUAN HỆ (ERD - Tóm tắt)](#2-sơ-đồ-quan-hệ-erd---tóm-tắt)
- [3. THIẾT KẾ CHI TIẾT CÁC BẢNG](#3-thiết-kế-chi-tiết-các-bảng)
- [4. TỔNG HỢP BẢNG VÀ QUAN HỆ](#4-tổng-hợp-bảng-và-quan-hệ)
- [5. CHỈ MỤC VÀ HIỆU NĂNG](#5-chỉ-mục-và-hiệu-năng)
- [6. CÁC RÀNG BUỘC TOÀN VẸN DỮ LIỆU](#6-các-ràng-buộc-toàn-vẹn-dữ-liệu)

---

## 1. QUY ƯỚC THIẾT KẾ

| Hạng mục | Quy tắc |
|---|---|
| Tên bảng | CamelCase — ví dụ: `Product`, `ProductColor`, `OrderDetail` |
| Tên cột | snake_case — ví dụ: `product_id`, `color_name`, `created_at` |
| Khóa chính | `{ten_bang_viet_thuong}_id`, kiểu `BIGINT AUTO_INCREMENT` hoặc `UUID` |
| Khóa ngoại | Tên cột tham chiếu đến bảng nào thì theo tên `{ten_bang_viet_thuong}_id` |
| Trạng thái | Dùng `ENUM` hoặc `VARCHAR(50)` với các giá trị rõ ràng |
| Thời gian | `created_at DATETIME DEFAULT CURRENT_TIMESTAMP`, `updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP` |
| Soft delete | Dùng `status` hoặc `is_deleted TINYINT(1)`, không xóa vật lý khi có giao dịch |
| Tiền tệ | `DECIMAL(15, 0)` — đơn vị VNĐ, không dùng FLOAT |

---

## 2. SƠ ĐỒ QUAN HỆ (ERD - Tóm tắt)

```
Brand ──────────────────┐
Category ───────────────┤
                        ↓
                    Product ──────────────── ProductColor ──── ProductImage
                                                   │
                                             ProductSku
                                            ↗           ↘
                                      CartItem       OrderDetail
                                        ↑                 ↑
                                       Cart             Order ──── Voucher
                                        ↑                 ↑
                                     Customer ────────────┘

StockLog ←── ProductSku
AuditLog ←── (Product, ProductColor, Order, Voucher)
ReturnRequest ←── Order
```

---

## 3. THIẾT KẾ CHI TIẾT CÁC BẢNG

---

### 3.1 Brand — Thương hiệu

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `brand_id` | BIGINT | PK, AUTO_INCREMENT | Mã thương hiệu |
| `brand_name` | VARCHAR(100) | NOT NULL, UNIQUE | Tên thương hiệu |
| `brand_logo_url` | VARCHAR(500) | NULL | URL logo |
| `description` | TEXT | NULL | Mô tả thương hiệu |
| `status` | ENUM('active','inactive') | NOT NULL, DEFAULT 'active' | Trạng thái |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

---

### 3.2 Category — Danh mục sản phẩm

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `category_id` | BIGINT | PK, AUTO_INCREMENT | Mã danh mục |
| `parent_category_id` | BIGINT | FK → Category(category_id), NULL | Danh mục cha (hỗ trợ đa cấp) |
| `category_name` | VARCHAR(100) | NOT NULL | Tên danh mục |
| `category_slug` | VARCHAR(150) | UNIQUE, NOT NULL | Slug dùng cho URL |
| `display_order` | INT | DEFAULT 0 | Thứ tự hiển thị |
| `status` | ENUM('active','inactive') | NOT NULL, DEFAULT 'active' | Trạng thái |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

---

### 3.3 Product — Sản phẩm gốc

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `product_id` | BIGINT | PK, AUTO_INCREMENT | Mã sản phẩm |
| `product_code` | VARCHAR(50) | UNIQUE, NOT NULL | Mã sản phẩm (do hệ thống sinh hoặc admin nhập) |
| `product_name` | VARCHAR(255) | NOT NULL | Tên sản phẩm |
| `brand_id` | BIGINT | FK → Brand(brand_id), NOT NULL | Thương hiệu |
| `category_id` | BIGINT | FK → Category(category_id), NOT NULL | Danh mục |
| `description` | TEXT | NULL | Mô tả chung, dùng chung cho tất cả màu/size |
| `gender_target` | ENUM('men','women','unisex','kids') | NULL | Đối tượng sử dụng |
| `status` | ENUM('active','hidden','discontinued') | NOT NULL, DEFAULT 'active' | Trạng thái |
| `created_by` | BIGINT | FK → User(user_id), NULL | Người tạo |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

**Index:** `product_code` (UNIQUE), `brand_id`, `category_id`, `status`

---

### 3.4 ProductColor — Biến thể màu của sản phẩm

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `color_id` | BIGINT | PK, AUTO_INCREMENT | Mã biến thể màu |
| `product_id` | BIGINT | FK → Product(product_id), NOT NULL | Sản phẩm gốc |
| `color_code` | VARCHAR(50) | NOT NULL | Mã màu (không trùng trong cùng product_id) |
| `color_name` | VARCHAR(100) | NOT NULL | Tên màu hiển thị |
| `hex_code` | VARCHAR(10) | NULL | Mã màu hex (ví dụ: #FFFFFF) |
| `price` | DECIMAL(15,0) | NOT NULL, CHECK (price > 0) | Giá bán của màu này |
| `discount_type` | ENUM('none','percent','fixed') | NOT NULL, DEFAULT 'none' | Loại giảm giá |
| `discount_value` | DECIMAL(15,2) | NOT NULL, DEFAULT 0 | Giá trị giảm (% hoặc tiền cố định) |
| `is_default` | TINYINT(1) | NOT NULL, DEFAULT 0 | Màu mặc định hiển thị (1 màu/sản phẩm) |
| `status` | ENUM('active','hidden','discontinued') | NOT NULL, DEFAULT 'active' | Trạng thái bán |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

**Ràng buộc:**
- `UNIQUE (product_id, color_code)` — mã màu không trùng trong cùng sản phẩm
- `discount_value >= 0`
- Nếu `discount_type = 'percent'` thì `discount_value` trong khoảng 0–100

**Index:** `product_id`, `status`

---

### 3.5 ProductImage — Hình ảnh theo màu

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `image_id` | BIGINT | PK, AUTO_INCREMENT | Mã ảnh |
| `color_id` | BIGINT | FK → ProductColor(color_id), NOT NULL | Màu sản phẩm |
| `image_url` | VARCHAR(500) | NOT NULL | Đường dẫn ảnh |
| `alt_text` | VARCHAR(255) | NULL | Mô tả ảnh (SEO, accessibility) |
| `is_main` | TINYINT(1) | NOT NULL, DEFAULT 0 | Ảnh đại diện của màu |
| `display_order` | INT | NOT NULL, DEFAULT 0 | Thứ tự hiển thị |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |

**Index:** `color_id`, `(color_id, is_main)`

---

### 3.6 ProductSku — SKU theo size

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `sku_id` | BIGINT | PK, AUTO_INCREMENT | Mã SKU |
| `sku_code` | VARCHAR(100) | UNIQUE, NOT NULL | Mã SKU duy nhất toàn hệ thống |
| `color_id` | BIGINT | FK → ProductColor(color_id), NOT NULL | Màu sản phẩm |
| `size` | VARCHAR(20) | NOT NULL | Kích cỡ (ví dụ: 39, 40, 41...) |
| `stock_quantity` | INT | NOT NULL, DEFAULT 0, CHECK (stock_quantity >= 0) | Tồn kho hiện tại |
| `sold_quantity` | INT | NOT NULL, DEFAULT 0 | Số lượng đã bán (tăng khi đơn hoàn thành) |
| `status` | ENUM('active','out_of_stock','discontinued') | NOT NULL, DEFAULT 'active' | Trạng thái |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

**Ràng buộc:**
- `UNIQUE (color_id, size)` — mỗi màu chỉ có 1 SKU cho mỗi size
- `UNIQUE (sku_code)` — mã SKU không trùng toàn hệ thống

**Index:** `sku_code` (UNIQUE), `color_id`, `status`

---

### 3.7 StockLog — Lịch sử thay đổi tồn kho

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `log_id` | BIGINT | PK, AUTO_INCREMENT | Mã log |
| `sku_id` | BIGINT | FK → ProductSku(sku_id), NOT NULL | SKU liên quan |
| `change_quantity` | INT | NOT NULL | Số lượng thay đổi (dương = nhập, âm = xuất) |
| `stock_before` | INT | NOT NULL | Tồn kho trước khi thay đổi |
| `stock_after` | INT | NOT NULL | Tồn kho sau khi thay đổi |
| `reason` | ENUM('import','order_export','cancel_return','adjustment','exchange') | NOT NULL | Lý do thay đổi |
| `reason_note` | VARCHAR(500) | NULL | Ghi chú bổ sung |
| `reference_type` | ENUM('order','manual','return') | NULL | Loại tham chiếu |
| `reference_id` | BIGINT | NULL | ID đơn hàng hoặc ID yêu cầu liên quan |
| `created_by` | BIGINT | FK → User(user_id), NOT NULL | Người thực hiện |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm thay đổi |

**Index:** `sku_id`, `created_at`

---

### 3.8 Customer — Khách hàng

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `customer_id` | BIGINT | PK, AUTO_INCREMENT | Mã khách hàng |
| `full_name` | VARCHAR(150) | NOT NULL | Họ tên |
| `email` | VARCHAR(255) | UNIQUE, NULL | Email (NULL nếu mua không đăng ký) |
| `phone` | VARCHAR(20) | NOT NULL | Số điện thoại |
| `password_hash` | VARCHAR(255) | NULL | Mật khẩu đã hash (NULL nếu chưa đăng ký) |
| `default_address` | VARCHAR(500) | NULL | Địa chỉ mặc định |
| `status` | ENUM('active','blocked') | NOT NULL, DEFAULT 'active' | Trạng thái tài khoản |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày đăng ký |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

---

### 3.9 User — Tài khoản nội bộ (nhân viên, admin)

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `user_id` | BIGINT | PK, AUTO_INCREMENT | Mã người dùng nội bộ |
| `username` | VARCHAR(100) | UNIQUE, NOT NULL | Tên đăng nhập |
| `full_name` | VARCHAR(150) | NOT NULL | Họ tên |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Email |
| `password_hash` | VARCHAR(255) | NOT NULL | Mật khẩu đã hash |
| `role` | ENUM('admin','staff') | NOT NULL, DEFAULT 'staff' | Vai trò |
| `status` | ENUM('active','inactive') | NOT NULL, DEFAULT 'active' | Trạng thái |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

---

### 3.10 Cart — Giỏ hàng

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `cart_id` | BIGINT | PK, AUTO_INCREMENT | Mã giỏ hàng |
| `customer_id` | BIGINT | FK → Customer(customer_id), NULL | Khách có tài khoản |
| `session_id` | VARCHAR(255) | NULL | Session ID cho khách vãng lai |
| `status` | ENUM('active','checked_out','abandoned') | NOT NULL, DEFAULT 'active' | Trạng thái giỏ |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

**Ràng buộc:** `customer_id` và `session_id` không đồng thời NULL.

**Index:** `customer_id`, `session_id`, `status`

---

### 3.11 CartItem — Chi tiết giỏ hàng

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `cart_item_id` | BIGINT | PK, AUTO_INCREMENT | Mã dòng giỏ hàng |
| `cart_id` | BIGINT | FK → Cart(cart_id), NOT NULL | Giỏ hàng |
| `sku_id` | BIGINT | FK → ProductSku(sku_id), NOT NULL | SKU (xác định màu + size) |
| `quantity` | INT | NOT NULL, CHECK (quantity > 0) | Số lượng |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày thêm |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

**Ràng buộc:** `UNIQUE (cart_id, sku_id)` — mỗi SKU chỉ xuất hiện 1 lần trong 1 giỏ.

---

### 3.12 Voucher — Mã giảm giá

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `voucher_id` | BIGINT | PK, AUTO_INCREMENT | Mã voucher |
| `code` | VARCHAR(50) | UNIQUE, NOT NULL | Mã voucher (khách nhập) |
| `voucher_type` | ENUM('percent','fixed','free_shipping') | NOT NULL | Loại giảm giá |
| `discount_value` | DECIMAL(15,2) | NOT NULL | Giá trị giảm (% hoặc số tiền) |
| `max_discount_amount` | DECIMAL(15,0) | NULL | Giảm tối đa (chỉ dùng khi type = percent) |
| `min_order_amount` | DECIMAL(15,0) | NOT NULL, DEFAULT 0 | Đơn tối thiểu để áp dụng |
| `usage_limit` | INT | NULL | Tổng lượt sử dụng tối đa (NULL = không giới hạn) |
| `used_count` | INT | NOT NULL, DEFAULT 0 | Đã sử dụng bao nhiêu lượt |
| `max_usage_per_customer` | INT | NOT NULL, DEFAULT 1 | Lượt tối đa mỗi khách hàng |
| `start_date` | DATETIME | NOT NULL | Ngày bắt đầu hiệu lực |
| `end_date` | DATETIME | NOT NULL | Ngày kết thúc hiệu lực |
| `status` | ENUM('active','paused','expired') | NOT NULL, DEFAULT 'active' | Trạng thái |
| `created_by` | BIGINT | FK → User(user_id), NOT NULL | Admin tạo voucher |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

**Index:** `code` (UNIQUE), `status`, `end_date`

---

### 3.13 VoucherUsage — Lịch sử sử dụng voucher

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `usage_id` | BIGINT | PK, AUTO_INCREMENT | Mã bản ghi |
| `voucher_id` | BIGINT | FK → Voucher(voucher_id), NOT NULL | Voucher được dùng |
| `order_id` | BIGINT | FK → Order(order_id), NOT NULL | Đơn hàng áp dụng |
| `customer_id` | BIGINT | FK → Customer(customer_id), NULL | Khách hàng (NULL nếu khách vãng lai) |
| `discount_amount` | DECIMAL(15,0) | NOT NULL | Số tiền thực tế được giảm |
| `used_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm sử dụng |

**Ràng buộc:** `UNIQUE (voucher_id, order_id)`

---

### 3.14 Order — Đơn hàng

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `order_id` | BIGINT | PK, AUTO_INCREMENT | Mã đơn hàng |
| `order_code` | VARCHAR(50) | UNIQUE, NOT NULL | Mã đơn (hiển thị cho khách) |
| `customer_id` | BIGINT | FK → Customer(customer_id), NULL | Khách có tài khoản |
| `receiver_name` | VARCHAR(150) | NOT NULL | Họ tên người nhận |
| `receiver_phone` | VARCHAR(20) | NOT NULL | Số điện thoại nhận hàng |
| `shipping_address` | VARCHAR(500) | NOT NULL | Địa chỉ giao hàng |
| `note` | TEXT | NULL | Ghi chú của khách |
| `payment_method` | ENUM('cod','bank_transfer','online') | NOT NULL | Phương thức thanh toán |
| `payment_status` | ENUM('pending','paid','refunded') | NOT NULL, DEFAULT 'pending' | Trạng thái thanh toán |
| `voucher_id` | BIGINT | FK → Voucher(voucher_id), NULL | Voucher áp dụng |
| `voucher_code_snapshot` | VARCHAR(50) | NULL | Snapshot mã voucher tại thời điểm đặt |
| `subtotal_amount` | DECIMAL(15,0) | NOT NULL | Tổng tiền sau giảm giá sản phẩm |
| `voucher_discount_amount` | DECIMAL(15,0) | NOT NULL, DEFAULT 0 | Số tiền giảm từ voucher |
| `shipping_fee` | DECIMAL(15,0) | NOT NULL, DEFAULT 0 | Phí vận chuyển |
| `total_amount` | DECIMAL(15,0) | NOT NULL | Tổng thanh toán cuối cùng |
| `order_status` | ENUM('pending','confirmed','preparing','shipping','completed','cancelled') | NOT NULL, DEFAULT 'pending' | Trạng thái đơn hàng |
| `cancelled_reason` | VARCHAR(500) | NULL | Lý do hủy |
| `cancelled_by` | BIGINT | FK → User(user_id), NULL | Người hủy đơn (nếu nhân viên hủy) |
| `cancelled_at` | DATETIME | NULL | Thời điểm hủy |
| `completed_at` | DATETIME | NULL | Thời điểm hoàn thành |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày đặt hàng |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

**Công thức:** `total_amount = subtotal_amount - voucher_discount_amount + shipping_fee`

**Index:** `order_code` (UNIQUE), `customer_id`, `order_status`, `created_at`

---

### 3.15 OrderDetail — Chi tiết đơn hàng

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `order_detail_id` | BIGINT | PK, AUTO_INCREMENT | Mã dòng chi tiết |
| `order_id` | BIGINT | FK → Order(order_id), NOT NULL | Đơn hàng |
| `sku_id` | BIGINT | FK → ProductSku(sku_id), NOT NULL | SKU tại thời điểm mua |
| `sku_code_snapshot` | VARCHAR(100) | NOT NULL | Snapshot mã SKU |
| `product_name_snapshot` | VARCHAR(255) | NOT NULL | Snapshot tên sản phẩm |
| `color_name_snapshot` | VARCHAR(100) | NOT NULL | Snapshot tên màu |
| `size_snapshot` | VARCHAR(20) | NOT NULL | Snapshot size |
| `image_url_snapshot` | VARCHAR(500) | NULL | Snapshot URL ảnh |
| `quantity` | INT | NOT NULL, CHECK (quantity > 0) | Số lượng |
| `unit_price` | DECIMAL(15,0) | NOT NULL | Đơn giá tại thời điểm mua (giá gốc) |
| `discount_type_snapshot` | ENUM('none','percent','fixed') | NOT NULL | Loại giảm giá sản phẩm |
| `discount_value_snapshot` | DECIMAL(15,2) | NOT NULL, DEFAULT 0 | Giá trị giảm giá sản phẩm |
| `discounted_price` | DECIMAL(15,0) | NOT NULL | Đơn giá sau giảm sản phẩm |
| `line_total` | DECIMAL(15,0) | NOT NULL | Thành tiền dòng (discounted_price × quantity) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày tạo |

**Giải thích snapshot:** Lưu lại tên sản phẩm, màu, size, giá tại thời điểm mua để đảm bảo lịch sử đơn hàng không bị thay đổi khi admin cập nhật thông tin sản phẩm.

**Index:** `order_id`, `sku_id`

---

### 3.16 OrderStatusLog — Lịch sử thay đổi trạng thái đơn

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `status_log_id` | BIGINT | PK, AUTO_INCREMENT | Mã log |
| `order_id` | BIGINT | FK → Order(order_id), NOT NULL | Đơn hàng |
| `old_status` | VARCHAR(50) | NULL | Trạng thái trước |
| `new_status` | VARCHAR(50) | NOT NULL | Trạng thái mới |
| `note` | VARCHAR(500) | NULL | Ghi chú |
| `changed_by` | BIGINT | FK → User(user_id), NULL | Người thực hiện |
| `changed_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm thay đổi |

---

### 3.17 ReturnRequest — Yêu cầu đổi trả hàng

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `return_id` | BIGINT | PK, AUTO_INCREMENT | Mã yêu cầu |
| `order_id` | BIGINT | FK → Order(order_id), NOT NULL | Đơn hàng gốc |
| `request_type` | ENUM('exchange','refund') | NOT NULL | Loại yêu cầu: đổi hoặc hoàn |
| `reason` | ENUM('wrong_size','wrong_color','defective','wrong_item','other') | NOT NULL | Lý do đổi trả |
| `reason_note` | TEXT | NULL | Mô tả chi tiết |
| `status` | ENUM('pending','approved','rejected','completed') | NOT NULL, DEFAULT 'pending' | Trạng thái xử lý |
| `reviewed_by` | BIGINT | FK → User(user_id), NULL | Nhân viên duyệt |
| `reviewed_at` | DATETIME | NULL | Thời điểm duyệt |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ngày yêu cầu |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Ngày cập nhật |

---

### 3.18 ReturnItem — Chi tiết sản phẩm đổi trả

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `return_item_id` | BIGINT | PK, AUTO_INCREMENT | Mã dòng |
| `return_id` | BIGINT | FK → ReturnRequest(return_id), NOT NULL | Yêu cầu đổi trả |
| `original_sku_id` | BIGINT | FK → ProductSku(sku_id), NOT NULL | SKU trả về |
| `exchange_sku_id` | BIGINT | FK → ProductSku(sku_id), NULL | SKU đổi sang (nếu là đổi hàng) |
| `quantity` | INT | NOT NULL | Số lượng đổi/trả |

---

### 3.19 AuditLog — Nhật ký thay đổi quan trọng

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `audit_id` | BIGINT | PK, AUTO_INCREMENT | Mã log |
| `entity_type` | VARCHAR(50) | NOT NULL | Tên bảng/đối tượng bị thay đổi |
| `entity_id` | BIGINT | NOT NULL | ID bản ghi bị thay đổi |
| `action` | ENUM('create','update','delete','status_change') | NOT NULL | Loại hành động |
| `field_name` | VARCHAR(100) | NULL | Tên trường bị thay đổi |
| `old_value` | TEXT | NULL | Giá trị cũ |
| `new_value` | TEXT | NULL | Giá trị mới |
| `changed_by` | BIGINT | FK → User(user_id), NOT NULL | Người thực hiện |
| `ip_address` | VARCHAR(50) | NULL | IP thực hiện |
| `changed_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Thời điểm thay đổi |

**Áp dụng ghi log cho:** thay đổi giá, giảm giá, tồn kho, trạng thái đơn hàng, ẩn/ngừng sản phẩm, tạo/sửa/xóa voucher.

---

## 4. TỔNG HỢP BẢNG VÀ QUAN HỆ

| Bảng | Ý nghĩa | Quan hệ chính |
|---|---|---|
| `Brand` | Thương hiệu | 1–N với Product |
| `Category` | Danh mục (đa cấp) | 1–N với Product, tự tham chiếu |
| `Product` | Sản phẩm gốc | 1–N với ProductColor |
| `ProductColor` | Biến thể màu | N–1 với Product; 1–N với ProductImage, ProductSku |
| `ProductImage` | Hình ảnh theo màu | N–1 với ProductColor |
| `ProductSku` | SKU theo size | N–1 với ProductColor; 1–N với CartItem, OrderDetail, StockLog |
| `StockLog` | Lịch sử tồn kho | N–1 với ProductSku |
| `Customer` | Khách hàng | 1–N với Cart, Order |
| `User` | Nhân viên/Admin | Dùng trong StockLog, OrderStatusLog, AuditLog |
| `Cart` | Giỏ hàng | 1–N với CartItem; N–1 với Customer |
| `CartItem` | Dòng giỏ hàng | N–1 với Cart, ProductSku |
| `Voucher` | Mã giảm giá | 1–N với VoucherUsage; N–1 với Order |
| `VoucherUsage` | Lịch sử dùng voucher | N–1 với Voucher, Order, Customer |
| `Order` | Đơn hàng | 1–N với OrderDetail, OrderStatusLog; N–1 với Customer, Voucher |
| `OrderDetail` | Chi tiết đơn | N–1 với Order, ProductSku |
| `OrderStatusLog` | Log trạng thái đơn | N–1 với Order |
| `ReturnRequest` | Yêu cầu đổi/trả | N–1 với Order; 1–N với ReturnItem |
| `ReturnItem` | Chi tiết đổi trả | N–1 với ReturnRequest, ProductSku |
| `AuditLog` | Nhật ký hệ thống | Ghi nhận thay đổi mọi entity quan trọng |

---

## 5. CHỈ MỤC VÀ HIỆU NĂNG

### 5.1 Các index quan trọng

```sql
-- Tìm kiếm & lọc sản phẩm
CREATE INDEX idx_product_brand ON Product(brand_id);
CREATE INDEX idx_product_category ON Product(category_id);
CREATE INDEX idx_product_status ON Product(status);

-- Truy vấn biến thể theo sản phẩm
CREATE INDEX idx_product_color_product ON ProductColor(product_id, status);
CREATE INDEX idx_product_sku_color ON ProductSku(color_id, status);
CREATE INDEX idx_product_sku_code ON ProductSku(sku_code);

-- Tìm hình ảnh theo màu
CREATE INDEX idx_product_image_color ON ProductImage(color_id, is_main);

-- Giỏ hàng
CREATE INDEX idx_cart_customer ON Cart(customer_id, status);
CREATE INDEX idx_cart_session ON Cart(session_id, status);

-- Đơn hàng
CREATE INDEX idx_order_customer ON Order(customer_id);
CREATE INDEX idx_order_status ON Order(order_status);
CREATE INDEX idx_order_created ON Order(created_at);

-- Voucher
CREATE UNIQUE INDEX idx_voucher_code ON Voucher(code);
CREATE INDEX idx_voucher_status_date ON Voucher(status, end_date);

-- Tồn kho log
CREATE INDEX idx_stock_log_sku ON StockLog(sku_id, created_at);
```

### 5.2 Lưu ý hiệu năng

- Truy vấn danh sách sản phẩm nên JOIN tối đa: `Product → ProductColor (is_default=1) → ProductImage (is_main=1)` để lấy ảnh đại diện.
- Tìm kiếm theo màu/size nên đi qua `ProductSku → ProductColor → Product`.
- Số lượng đã bán (`sold_quantity`) nên được denormalize tại `ProductSku` để tránh COUNT đắt tiền.
- `StockLog` và `AuditLog` là bảng ghi log — nên cân nhắc phân vùng (partition) theo tháng khi dữ liệu lớn.

---

## 6. CÁC RÀNG BUỘC TOÀN VẸN DỮ LIỆU

```sql
-- Không cho tồn kho âm
ALTER TABLE ProductSku ADD CONSTRAINT chk_stock_non_negative
  CHECK (stock_quantity >= 0);

-- Giá bán phải > 0
ALTER TABLE ProductColor ADD CONSTRAINT chk_price_positive
  CHECK (price > 0);

-- Giảm giá không âm
ALTER TABLE ProductColor ADD CONSTRAINT chk_discount_non_negative
  CHECK (discount_value >= 0);

-- Số lượng đặt hàng > 0
ALTER TABLE OrderDetail ADD CONSTRAINT chk_order_qty_positive
  CHECK (quantity > 0);

-- Tổng tiền không âm
ALTER TABLE Order ADD CONSTRAINT chk_total_non_negative
  CHECK (total_amount >= 0);

-- Mã màu không trùng trong cùng sản phẩm
ALTER TABLE ProductColor ADD CONSTRAINT uq_product_color_code
  UNIQUE (product_id, color_code);

-- Mỗi màu chỉ có 1 SKU cho mỗi size
ALTER TABLE ProductSku ADD CONSTRAINT uq_color_size
  UNIQUE (color_id, size);
```
