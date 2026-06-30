# THIẾT KẾ API - WEBSITE BÁN GIÀY

> Phiên bản: 1.0 | Ngày: 27/06/2026  
> Base URL: `https://api.shoeshop.com/api/v1`  
> Kiến trúc: RESTful API | Định dạng: JSON  
> Xác thực: JWT Bearer Token

---

## MỤC LỤC
- [1. QUY ƯỚC CHUNG](#1-quy-ước-chung)
- [2. XÁC THỰC (Authentication)](#2-xác-thực-authentication)
- [3. THƯƠNG HIỆU (Brand)](#3-thương-hiệu-brand)
- [4. DANH MỤC (Category)](#4-danh-mục-category)
- [5. SẢN PHẨM (Product)](#5-sản-phẩm-product)
- [6. BIẾN THỂ MÀU SẮC (ProductColor)](#6-biến-thể-màu-sắc-productcolor)
- [7. HÌNH ẢNH (ProductImage)](#7-hình-ảnh-productimage)
- [8. SKU VÀ SIZE (ProductSku)](#8-sku-và-size-productsku)
- [9. GIỎ HÀNG (Cart)](#9-giỏ-hàng-cart)
- [10. ĐẶT HÀNG (Order - Phía Khách)](#10-đặt-hàng-order---phía-khách)
- [11. QUẢN LÝ ĐƠN HÀNG (Admin/Staff)](#11-quản-lý-đơn-hàng-adminstaff)
- [12. VOUCHER (Admin)](#12-voucher-admin)
- [13. BÁO CÁO (Admin)](#13-báo-cáo-admin)
- [14. MÃ LỖI NGHIỆP VỤ (Error Codes)](#14-mã-lỗi-nghiệp-vụ-error-codes)
- [15. TỔNG HỢP ENDPOINTS](#15-tổng-hợp-endpoints)

---

## 1. QUY ƯỚC CHUNG

### 1.1 Cấu trúc URL

```
/v1/{resource}              → danh sách hoặc tạo mới
/v1/{resource}/{id}         → chi tiết, cập nhật, xóa
/v1/{resource}/{id}/{sub}   → tài nguyên con
```

### 1.2 HTTP Methods

| Method | Ý nghĩa |
|---|---|
| `GET` | Lấy dữ liệu, không thay đổi trạng thái |
| `POST` | Tạo mới tài nguyên |
| `PUT` | Cập nhật toàn bộ tài nguyên |
| `PATCH` | Cập nhật một phần tài nguyên |
| `DELETE` | Xóa (soft delete — chuyển trạng thái) |

### 1.3 Cấu trúc Response chuẩn

**Thành công:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Thao tác thành công"
}
```

**Thành công — có phân trang:**
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 150,
    "total_pages": 8
  }
}
```

**Lỗi:**
```json
{
  "success": false,
  "error": {
    "code": "OUT_OF_STOCK",
    "message": "Sản phẩm đã hết hàng",
    "details": { "sku_id": 123, "stock_quantity": 0 }
  }
}
```

### 1.4 HTTP Status Codes

| Code | Ý nghĩa |
|---|---|
| `200` | OK — thành công |
| `201` | Created — tạo mới thành công |
| `400` | Bad Request — dữ liệu đầu vào không hợp lệ |
| `401` | Unauthorized — chưa xác thực |
| `403` | Forbidden — không có quyền |
| `404` | Not Found — không tìm thấy tài nguyên |
| `409` | Conflict — xung đột dữ liệu (ví dụ: trùng mã SKU) |
| `422` | Unprocessable Entity — vi phạm quy tắc nghiệp vụ |
| `500` | Internal Server Error |

### 1.5 Phân quyền

| Ký hiệu | Vai trò được phép |
|---|---|
| 🌐 Public | Không cần đăng nhập |
| 👤 Customer | Khách hàng đã đăng nhập |
| 👷 Staff | Nhân viên (bao gồm Admin) |
| 🔑 Admin | Chỉ Quản trị viên |

### 1.6 Query Parameters phân trang (dùng chung)

| Param | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `page` | integer | 1 | Số trang |
| `limit` | integer | 20 | Số bản ghi/trang (tối đa 100) |
| `sort_by` | string | `created_at` | Trường sắp xếp |
| `sort_order` | string | `desc` | `asc` hoặc `desc` |

---

## 2. XÁC THỰC (Authentication)

### 2.1 Đăng ký khách hàng

**POST** `/v1/auth/register` 🌐

**Request Body:**
```json
{
  "full_name": "Nguyễn Văn A",
  "email": "nguyenvana@email.com",
  "phone": "0901234567",
  "password": "Password@123"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "customer_id": 1,
    "full_name": "Nguyễn Văn A",
    "email": "nguyenvana@email.com",
    "phone": "0901234567"
  },
  "message": "Đăng ký thành công"
}
```

**Lỗi thường gặp:**
- `400` — Email hoặc số điện thoại đã tồn tại
- `400` — Dữ liệu không hợp lệ (email sai format, mật khẩu quá yếu)

---

### 2.2 Đăng nhập khách hàng

**POST** `/v1/auth/login` 🌐

**Request Body:**
```json
{
  "email": "nguyenvana@email.com",
  "password": "Password@123"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "customer": {
      "full_name": "Truong Khánh Linh",
      "email": "linhtk251104@gmail.com",
      "phone": "0397594866",
      "gender": "male",
      "date_of_birth": "2004-11-25T00:00:00",
      "default_address": "Tân Long - Tuyên Quang"
    }
  }
}
```

---

### 2.3 Đăng nhập nội bộ (Staff/Admin)

**POST** `/v1/auth/admin/login` 🌐

**Request Body:**
```json
{
  "username": "staff01",
  "password": "StaffPass@123"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 28800,
    "user": {
      "user_id": 5,
      "full_name": "Trần Thị B",
      "role": "staff"
    }
  }
}
```

---

### 2.4 Làm mới token

**POST** `/v1/auth/refresh` 👤

**Request Body:**
```json
{ "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..." }
```

---

### 2.5 Đăng xuất

**POST** `/v1/auth/logout` 👤

---

## 3. THƯƠNG HIỆU (Brand)

### 3.1 Lấy danh sách thương hiệu

**GET** `/v1/brands` 🌐

**Query Params:** `status` (active/inactive)

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "brand_id": 1,
      "brand_name": "Nike",
      "logo_url": "https://cdn.shoeshop.com/brands/nike.png",
      "status": "active"
    }
  ]
}
```

---

### 3.2 Tạo thương hiệu

**POST** `/v1/admin/brands` 🔑

**Request Body:**
```json
{
  "brand_name": "Adidas",
  "brand_logo_url": "https://cdn.shoeshop.com/brands/adidas.png",
  "description": "Thương hiệu thể thao từ Đức"
}
```

---

### 3.3 Cập nhật thương hiệu

**PUT** `/v1/admin/brands/{brand_id}` 🔑

---

### 3.4 Xóa / Ẩn thương hiệu

**PATCH** `/v1/admin/brands/{brand_id}/status` 🔑

**Request Body:** `{ "status": "inactive" }`

---

## 4. DANH MỤC (Category)

### 4.1 Lấy danh sách danh mục

**GET** `/v1/categories` 🌐

**Query Params:** `status`, `parent_id` (lọc theo danh mục cha)

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "category_id": 1,
      "category_name": "Giày thể thao",
      "category_slug": "giay-the-thao",
      "parent_id": null,
      "display_order": 1,
    }
  ]
}
```

---

### 4.2 Tạo danh mục

**POST** `/v1/admin/categories` 🔑

**Request Body:**
```json
{
  "category_name": "Giày thể thao",
  "category_slug": "giay-the-thao",
  "parent_category_id": null,
  "display_order": 1
}
```

---

### 4.3 Cập nhật danh mục

**PUT** `/v1/admin/categories/{category_id}` 🔑

---

### 4.4 Thay đổi trạng thái danh mục

**PATCH** `/v1/admin/categories/{category_id}/status` 🔑

**Request Body:** `{ "status": "inactive" }`

---

## 5. SẢN PHẨM (Product)

### 5.1 Lấy danh sách sản phẩm (Public)

**GET** `/v1/products` 🌐

**Query Params:**

| Param | Kiểu | Mô tả |
|---|---|---|
| `keyword` | string | Tìm theo tên sản phẩm |
| `brand_id` | integer | Lọc theo thương hiệu |
| `category_id` | integer | Lọc theo danh mục |
| `color_name` | string | Lọc theo tên màu |
| `size` | string | Lọc theo size (ví dụ: 40, 41) |
| `min_price` | integer | Giá từ (VNĐ) |
| `max_price` | integer | Giá đến (VNĐ) |
| `in_stock` | boolean | Chỉ lấy sản phẩm còn hàng |
| `on_sale` | boolean | Chỉ lấy sản phẩm đang giảm giá |
| `gender_target` | string | men / women / unisex / kids |
| `page` | integer | Trang số |
| `limit` | integer | Số bản ghi/trang |
| `sort_by` | string | price / created_at / sold_quantity |
| `sort_order` | string | asc / desc |

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "product_id": 1,
      "product_name": "Nike Air Force 1",
      "brand_name": "Nike",
      "category_name": "Giày thể thao",
      "gender_target": "unisex",
      "default_color": {
        "color_id": 3,
        "color_name": "Trắng",
        "price": 2500000,
        "discount_type": "percent",
        "discount_value": 10,
        "discounted_price": 2250000,
        "main_image_url": "https://cdn.shoeshop.com/img/af1-white.jpg"
      },
      "has_stock": true
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 85,
    "total_pages": 5
  }
}
```

---

### 5.2 Xem chi tiết sản phẩm (Public)

**GET** `/v1/products/{product_id}` 🌐

**Response 200:**
```json
{
  "success": true,
  "data": {
    "product_id": 1,
    "product_code": "SP001",
    "product_name": "Nike Air Force 1",
    "brand": { "brand_id": 1, "brand_name": "Nike" },
    "category": { "category_id": 3, "category_name": "Giày thể thao" },
    "description": "Mô tả chung của sản phẩm...",
    "gender_target": "unisex",
    "colors": [
      {
        "color_id": 3,
        "color_code": "WHITE-001",
        "color_name": "Trắng",
        "hex_code": "#FFFFFF",
        "price": 2500000,
        "discount_type": "percent",
        "discount_value": 10,
        "discounted_price": 2250000,
        "is_default": true,
        "images": [
          {
            "image_id": 1,
            "image_url": "https://cdn.shoeshop.com/img/af1-white-1.jpg",
            "is_main": true,
            "display_order": 1
          }
        ],
        "skus": [
          { "sku_id": 10, "size": "39", "stock_quantity": 5, "status": "active" },
          { "sku_id": 11, "size": "40", "stock_quantity": 0, "status": "out_of_stock" },
          { "sku_id": 12, "size": "41", "stock_quantity": 3, "status": "active" }
        ]
      },
      {
        "color_id": 4,
        "color_code": "BLACK-001",
        "color_name": "Đen",
        "hex_code": "#000000",
        "price": 2700000,
        "discount_type": "none",
        "discount_value": 0,
        "discounted_price": 2700000,
        "is_default": false,
        "images": [ ... ],
        "skus": [ ... ]
      }
    ]
  }
}
```

---

### 5.3 Lấy danh sách sản phẩm (Admin)

**GET** `/v1/admin/products` 👷

Query mở rộng hơn public, thêm: `status` (active/hidden/discontinued), `created_by`.

---

### 5.4 Tạo sản phẩm gốc

**POST** `/v1/admin/products` 🔑

**Request Body:**
```json
{
  "product_name": "Nike Air Force 1",
  "product_code": "SP001",
  "brand_id": 1,
  "category_id": 3,
  "description": "Mô tả chung...",
  "gender_target": "unisex",
  "status": "active"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": { "product_id": 1, "product_name": "Nike Air Force 1", ... },
  "message": "Tạo sản phẩm thành công"
}
```

**Lỗi thường gặp:**
- `400` — Tên sản phẩm trống (BR-PRO-01)
- `409` — Mã sản phẩm đã tồn tại

---

### 5.5 Cập nhật sản phẩm gốc

**PUT** `/v1/admin/products/{product_id}` 🔑

**Request Body:** Tương tự tạo mới, gửi các trường cần cập nhật.

---

### 5.6 Thay đổi trạng thái sản phẩm

**PATCH** `/v1/admin/products/{product_id}/status` 🔑

**Request Body:**
```json
{ "status": "hidden" }
```

**Lỗi:** `422` nếu cố xóa vật lý sản phẩm đã có đơn hàng (BR-PRO-07).

---

## 6. BIẾN THỂ MÀU SẮC (ProductColor)

### 6.1 Thêm màu vào sản phẩm

**POST** `/v1/admin/products/{product_id}/colors` 🔑

**Request Body:**
```json
{
  "color_code": "WHITE-001",
  "color_name": "Trắng",
  "hex_code": "#FFFFFF",
  "price": 2500000,
  "discount_type": "percent",
  "discount_value": 10,
  "is_default": true,
  "status": "active"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": { "color_id": 3, "color_name": "Trắng", "price": 2500000, ... },
  "message": "Thêm màu thành công"
}
```

**Lỗi thường gặp:**
- `400` — Giá không hợp lệ (BR-PRI-01)
- `400` — Giảm giá âm hoặc % > 100 (BR-PRI-02, BR-PRI-03)
- `409` — Mã màu đã tồn tại trong sản phẩm (BR-PRO-05)

---

### 6.2 Cập nhật màu

**PUT** `/v1/admin/products/{product_id}/colors/{color_id}` 🔑

**Request Body:** Các trường cần cập nhật.

---

### 6.3 Cập nhật giá và giảm giá

**PATCH** `/v1/admin/products/{product_id}/colors/{color_id}/pricing` 🔑

**Request Body:**
```json
{
  "price": 2600000,
  "discount_type": "percent",
  "discount_value": 15
}
```

> Ghi AuditLog tự động với giá trị cũ → mới.

---

### 6.4 Thay đổi trạng thái màu

**PATCH** `/v1/admin/products/{product_id}/colors/{color_id}/status` 🔑

**Request Body:** `{ "status": "hidden" }`

---

## 7. HÌNH ẢNH (ProductImage)

### 7.1 Upload hình ảnh cho màu

**POST** `/v1/admin/products/{product_id}/colors/{color_id}/images` 🔑

**Content-Type:** `multipart/form-data`

**Form fields:**
- `images` (file[]) — Một hoặc nhiều file ảnh
- `is_main` (boolean) — Ảnh đầu tiên là ảnh đại diện

**Response 201:**
```json
{
  "success": true,
  "data": [
    { "image_id": 1, "image_url": "...", "is_main": true, "display_order": 1 },
    { "image_id": 2, "image_url": "...", "is_main": false, "display_order": 2 }
  ]
}
```

---

### 7.2 Cập nhật thứ tự và ảnh đại diện

**PATCH** `/v1/admin/products/{product_id}/colors/{color_id}/images/reorder` 🔑

**Request Body:**
```json
{
  "images": [
    { "image_id": 2, "display_order": 1, "is_main": true },
    { "image_id": 1, "display_order": 2, "is_main": false }
  ]
}
```

---

### 7.3 Xóa hình ảnh

**DELETE** `/v1/admin/products/{product_id}/colors/{color_id}/images/{image_id}` 🔑

---

## 8. SKU VÀ SIZE (ProductSku)

### 8.1 Thêm size vào màu

**POST** `/v1/admin/products/{product_id}/colors/{color_id}/skus` 🔑

**Request Body:**
```json
{
  "skus": [
    { "size": "39", "stock_quantity": 10 },
    { "size": "40", "stock_quantity": 15 },
    { "size": "41", "stock_quantity": 8 }
  ]
}
```

> Hệ thống tự sinh `sku_code` theo quy tắc: `{product_code}-{color_code}-{size}`.

**Response 201:**
```json
{
  "success": true,
  "data": [
    { "sku_id": 10, "sku_code": "SP001-WHITE-001-39", "size": "39", "stock_quantity": 10 },
    { "sku_id": 11, "sku_code": "SP001-WHITE-001-40", "size": "40", "stock_quantity": 15 }
  ]
}
```

**Lỗi thường gặp:**
- `409` — Size đã tồn tại trong màu (BR-PRO-06)

---

### 8.2 Cập nhật trạng thái SKU

**PATCH** `/v1/admin/products/{product_id}/colors/{color_id}/skus/{sku_id}/status` 🔑

**Request Body:** `{ "status": "discontinued" }`

---

### 8.3 Cập nhật tồn kho (nhập hàng / điều chỉnh)

**PATCH** `/v1/admin/skus/{sku_id}/stock` 👷

**Request Body:**
```json
{
  "change_quantity": 50,
  "reason": "import",
  "reason_note": "Nhập hàng tháng 6/2026"
}
```

> `change_quantity` dương = nhập thêm, âm = điều chỉnh giảm.  
> Ghi StockLog tự động.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "sku_id": 10,
    "sku_code": "SP001-WHITE-001-39",
    "stock_before": 5,
    "stock_after": 55,
    "change_quantity": 50
  }
}
```

**Lỗi thường gặp:**
- `422` — Tồn kho sau điều chỉnh < 0 (BR-STK-02)

---

### 8.4 Lấy lịch sử tồn kho

**GET** `/v1/admin/skus/{sku_id}/stock-logs` 👷

**Query Params:** `page`, `limit`, `reason`, `from_date`, `to_date`

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "log_id": 101,
      "change_quantity": 50,
      "stock_before": 5,
      "stock_after": 55,
      "reason": "import",
      "reason_note": "Nhập hàng tháng 6/2026",
      "created_by": { "user_id": 2, "full_name": "Trần Thị B" },
      "created_at": "2026-06-27T09:00:00Z"
    }
  ]
}
```

---

## 9. GIỎ HÀNG (Cart)

### 9.1 Lấy giỏ hàng hiện tại

**GET** `/v1/cart` 🌐 *(kèm session_id header nếu chưa đăng nhập)*

**Headers (khách vãng lai):** `X-Session-Id: {session_id}`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "cart_id": 55,
    "items": [
      {
        "cart_item_id": 201,
        "sku_id": 10,
        "sku_code": "SP001-WHITE-001-39",
        "product_name": "Nike Air Force 1",
        "color_name": "Trắng",
        "size": "39",
        "image_url": "https://cdn.shoeshop.com/img/af1-white-1.jpg",
        "quantity": 2,
        "unit_price": 2500000,
        "discount_type": "percent",
        "discount_value": 10,
        "discounted_price": 2250000,
        "line_total": 4500000,
        "stock_quantity": 5,
        "is_available": true,
        "is_active": true
      }
    ],
    "summary": {
      "subtotal": 4500000,
      "item_count": 1
    }
  }
}
```

> `is_available`: false nếu SKU đã hết hàng hoặc bị ngừng bán sau khi thêm giỏ.  
> `unit_price` và `discounted_price` luôn lấy từ `ProductColor` mới nhất khi gọi API này.

---

### 9.2 Thêm sản phẩm vào giỏ

**POST** `/v1/cart/items` 🌐

**Request Body:**
```json
{
  "sku_id": 10,
  "quantity": 2
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "cart_item_id": 201,
    "sku_id": 10,
    "quantity": 2,
    "discounted_price": 2250000,
    "line_total": 4500000
  },
  "message": "Đã thêm vào giỏ hàng"
}
```

**Lỗi thường gặp:**
- `422` — SKU hết hàng (BR-STK-03)
- `422` — Số lượng vượt tồn kho (BR-STK-04)
- `404` — SKU không tồn tại hoặc đã ngừng bán

---

### 9.3 Cập nhật số lượng trong giỏ

**PATCH** `/v1/cart/items/{cart_item_id}` 🌐

**Request Body:**
```json
{ "quantity": 3 }
```

> Nếu `quantity = 0` → tự động xóa dòng đó khỏi giỏ.

**Lỗi thường gặp:**
- `422` — Số lượng vượt tồn kho (BR-STK-04)

---

### 9.4 Xóa sản phẩm khỏi giỏ

**DELETE** `/v1/cart/items/{cart_item_id}` 🌐

---

### 9.5 Xóa toàn bộ giỏ hàng

**DELETE** `/v1/cart` 🌐

---

### 9.6 Kiểm tra và áp dụng voucher

**POST** `/v1/cart/voucher` 🌐

**Request Body:**
```json
{ "voucher_code": "SALE10" }
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "voucher_code": "SALE10",
    "voucher_type": "percent",
    "discount_value": 10,
    "max_discount_amount": 200000,
    "discount_amount": 200000,
    "subtotal_before": 4500000,
    "subtotal_after": 4300000
  }
}
```

**Lỗi thường gặp:**
- `404` — Mã voucher không tồn tại
- `422` — Voucher hết hạn / hết lượt / đơn chưa đạt tối thiểu (BR-VOU-02, BR-VOU-03, BR-VOU-04)

---

### 9.7 Hủy voucher đang áp dụng

**DELETE** `/v1/cart/voucher` 🌐

---

### 9.8 Tính tổng thanh toán (preview)

**POST** `/v1/cart/checkout-preview` 🌐

**Request Body:**
```json
{
  "voucher_code": "SALE10",
  "shipping_method": "standard"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "subtotal": 4500000,
    "voucher_discount": 200000,
    "shipping_fee": 30000,
    "total_amount": 4330000
  }
}
```

---

## 10. ĐẶT HÀNG (Order - Phía Khách)

### 10.1 Tạo đơn hàng

**POST** `/v1/orders` 🌐

**Request Body:**
```json
{
  "receiver_name": "Nguyễn Văn A",
  "receiver_phone": "0901234567",
  "shipping_address": "123 Đường Láng, Đống Đa, Hà Nội",
  "note": "Giao giờ hành chính",
  "payment_method": "cod",
  "shipping_method": "standard",
  "voucher_code": "SALE10"
}
```

> Hệ thống tự lấy giỏ hàng từ `customer_id` hoặc `session_id`.

**Response 201:**
```json
{
  "success": true,
  "data": {
    "order_id": 1001,
    "order_code": "ORD-20260627-1001",
    "order_status": "pending",
    "receiver_name": "Nguyễn Văn A",
    "receiver_phone": "0901234567",
    "shipping_address": "123 Đường Láng, Đống Đa, Hà Nội",
    "subtotal_amount": 4500000,
    "voucher_discount_amount": 200000,
    "shipping_fee": 30000,
    "total_amount": 4330000,
    "payment_method": "cod",
    "created_at": "2026-06-27T10:30:00Z"
  },
  "message": "Đặt hàng thành công"
}
```

**Lỗi thường gặp:**
- `400` — Thiếu thông tin nhận hàng (BR-ORD-01)
- `422` — SKU hết hàng tại thời điểm đặt (BR-STK-03, BR-ORD-04)
- `422` — Voucher không còn hợp lệ tại thời điểm đặt (BR-ORD-04)

---

### 10.2 Xem danh sách đơn hàng của tôi

**GET** `/v1/orders` 👤

**Query Params:** `status`, `page`, `limit`

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "order_id": 1001,
      "order_code": "ORD-20260627-1001",
      "order_status": "pending",
      "total_amount": 4330000,
      "item_count": 1,
      "created_at": "2026-06-27T10:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### 10.3 Xem chi tiết đơn hàng của tôi

**GET** `/v1/orders/{order_id}` 👤

**Response 200:**
```json
{
  "success": true,
  "data": {
    "order_id": 1001,
    "order_code": "ORD-20260627-1001",
    "order_status": "pending",
    "receiver_name": "Nguyễn Văn A",
    "receiver_phone": "0901234567",
    "shipping_address": "123 Đường Láng, Đống Đa, Hà Nội",
    "note": "Giao giờ hành chính",
    "payment_method": "cod",
    "payment_status": "pending",
    "voucher_code_snapshot": "SALE10",
    "subtotal_amount": 4500000,
    "voucher_discount_amount": 200000,
    "shipping_fee": 30000,
    "total_amount": 4330000,
    "items": [
      {
        "order_detail_id": 5001,
        "product_name_snapshot": "Nike Air Force 1",
        "color_name_snapshot": "Trắng",
        "size_snapshot": "39",
        "image_url_snapshot": "https://cdn.shoeshop.com/img/af1-white-1.jpg",
        "quantity": 2,
        "unit_price": 2500000,
        "discount_type_snapshot": "percent",
        "discount_value_snapshot": 10,
        "discounted_price": 2250000,
        "line_total": 4500000
      }
    ],
    "status_history": [
      { "status": "pending", "changed_at": "2026-06-27T10:30:00Z" }
    ],
    "created_at": "2026-06-27T10:30:00Z"
  }
}
```

---

### 10.4 Khách hủy đơn hàng

**PATCH** `/v1/orders/{order_id}/cancel` 👤

**Request Body:**
```json
{ "reason": "Tôi muốn đổi địa chỉ giao hàng" }
```

**Lỗi thường gặp:**
- `422` — Đơn đang giao hoặc đã hoàn thành, không được hủy (BR-ORD-03)

---

### 10.5 Yêu cầu đổi trả hàng

**POST** `/v1/orders/{order_id}/returns` 👤

**Request Body:**
```json
{
  "request_type": "exchange",
  "reason": "wrong_size",
  "reason_note": "Đặt nhầm size 39 thay vì 40",
  "items": [
    {
      "original_sku_id": 10,
      "exchange_sku_id": 11,
      "quantity": 2
    }
  ]
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "return_id": 301,
    "request_type": "exchange",
    "status": "pending",
    "created_at": "2026-06-27T14:00:00Z"
  },
  "message": "Yêu cầu đổi trả đã được ghi nhận"
}
```

---

## 11. QUẢN LÝ ĐƠN HÀNG (Admin/Staff)

### 11.1 Lấy danh sách đơn hàng

**GET** `/v1/admin/orders` 👷

**Query Params:**

| Param | Kiểu | Mô tả |
|---|---|---|
| `order_code` | string | Tìm theo mã đơn |
| `phone` | string | Tìm theo số điện thoại |
| `status` | string | Lọc theo trạng thái đơn |
| `payment_method` | string | Lọc theo phương thức thanh toán |
| `from_date` | date | Từ ngày đặt hàng |
| `to_date` | date | Đến ngày đặt hàng |
| `min_total` | integer | Tổng tiền từ |
| `max_total` | integer | Tổng tiền đến |

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "order_id": 1001,
      "order_code": "ORD-20260627-1001",
      "receiver_name": "Nguyễn Văn A",
      "receiver_phone": "0901234567",
      "order_status": "pending",
      "payment_method": "cod",
      "total_amount": 4330000,
      "item_count": 1,
      "created_at": "2026-06-27T10:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### 11.2 Xem chi tiết đơn hàng (Admin)

**GET** `/v1/admin/orders/{order_id}` 👷

> Tương tự `/v1/orders/{order_id}` nhưng hiển thị thêm: `customer_id`, thông tin nội bộ, đầy đủ lịch sử trạng thái.

---

### 11.3 Cập nhật trạng thái đơn hàng

**PATCH** `/v1/admin/orders/{order_id}/status` 👷

**Request Body:**
```json
{
  "new_status": "confirmed",
  "note": "Đã kiểm tra thông tin, xác nhận đơn"
}
```

**Các chuyển trạng thái hợp lệ:**

| Từ | Sang | Quyền |
|---|---|---|
| `pending` | `confirmed` | 👷 Staff |
| `confirmed` | `preparing` | 👷 Staff |
| `preparing` | `shipping` | 👷 Staff |
| `shipping` | `completed` | 👷 Staff |
| `pending / confirmed / preparing` | `cancelled` | 👷 Staff |

> Khi chuyển sang `completed`: hệ thống tự tăng `sold_quantity`.  
> Khi chuyển sang `cancelled`: hệ thống tự hoàn kho và ghi StockLog.

**Lỗi thường gặp:**
- `422` — Chuyển trạng thái không hợp lệ

---

### 11.4 Nhân viên hủy đơn hàng

**PATCH** `/v1/admin/orders/{order_id}/cancel` 👷

**Request Body:**
```json
{ "reason": "Khách yêu cầu hủy qua điện thoại" }
```

---

### 11.5 Xem danh sách yêu cầu đổi trả

**GET** `/v1/admin/returns` 👷

**Query Params:** `status`, `request_type`, `order_id`, `page`, `limit`

---

### 11.6 Duyệt / Từ chối yêu cầu đổi trả

**PATCH** `/v1/admin/returns/{return_id}/review` 👷

**Request Body:**
```json
{
  "status": "approved",
  "note": "Hàng còn mới, chấp nhận đổi"
}
```

---

### 11.7 Hoàn tất đổi trả (cập nhật kho)

**PATCH** `/v1/admin/returns/{return_id}/complete` 👷

> Hệ thống tự động:
> - Tăng `stock_quantity` SKU trả về
> - Giảm `stock_quantity` SKU đổi sang (nếu là exchange)
> - Ghi StockLog cho cả hai SKU

---

## 12. VOUCHER (Admin)

### 12.1 Lấy danh sách voucher

**GET** `/v1/admin/vouchers` 🔑

**Query Params:** `status`, `voucher_type`, `from_date`, `to_date`, `page`, `limit`

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "voucher_id": 1,
      "code": "SALE10",
      "voucher_type": "percent",
      "discount_value": 10,
      "max_discount_amount": 200000,
      "min_order_amount": 500000,
      "usage_limit": 100,
      "used_count": 23,
      "max_usage_per_customer": 1,
      "start_date": "2026-06-01T00:00:00Z",
      "end_date": "2026-06-30T23:59:59Z",
      "status": "active"
    }
  ]
}
```

---

### 12.2 Tạo voucher

**POST** `/v1/admin/vouchers` 🔑

**Request Body:**
```json
{
  "code": "FREESHIP",
  "voucher_type": "free_shipping",
  "discount_value": 0,
  "min_order_amount": 300000,
  "usage_limit": 200,
  "max_usage_per_customer": 1,
  "start_date": "2026-07-01T00:00:00Z",
  "end_date": "2026-07-31T23:59:59Z",
  "status": "active"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": { "voucher_id": 5, "code": "FREESHIP", ... },
  "message": "Tạo voucher thành công"
}
```

**Lỗi thường gặp:**
- `409` — Mã voucher đã tồn tại

---

### 12.3 Cập nhật voucher

**PUT** `/v1/admin/vouchers/{voucher_id}` 🔑

---

### 12.4 Thay đổi trạng thái voucher

**PATCH** `/v1/admin/vouchers/{voucher_id}/status` 🔑

**Request Body:** `{ "status": "paused" }`

---

### 12.5 Lịch sử sử dụng voucher

**GET** `/v1/admin/vouchers/{voucher_id}/usages` 🔑

**Query Params:** `page`, `limit`, `from_date`, `to_date`

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "usage_id": 1,
      "order_id": 1001,
      "order_code": "ORD-20260627-1001",
      "customer_name": "Nguyễn Văn A",
      "discount_amount": 200000,
      "used_at": "2026-06-27T10:30:00Z"
    }
  ]
}
```

---

## 13. BÁO CÁO (Admin)

### 13.1 Báo cáo tồn kho

**GET** `/v1/admin/reports/inventory` 👷

**Query Params:** `product_id`, `color_id`, `status`, `low_stock_threshold` (số tồn kho cảnh báo thấp)

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "product_name": "Nike Air Force 1",
      "color_name": "Trắng",
      "sku_code": "SP001-WHITE-001-39",
      "size": "39",
      "stock_quantity": 5,
      "sold_quantity": 120,
      "status": "active"
    }
  ]
}
```

---

### 13.2 Báo cáo doanh thu

**GET** `/v1/admin/reports/revenue` 🔑

**Query Params:** `from_date`, `to_date`, `group_by` (day/month), `order_status`, `payment_method`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_orders": 250,
      "total_revenue": 625000000,
      "average_order_value": 2500000
    },
    "by_period": [
      { "period": "2026-06-27", "order_count": 15, "revenue": 37500000 }
    ]
  }
}
```

---

### 13.3 Báo cáo sản phẩm bán chạy

**GET** `/v1/admin/reports/best-sellers` 👷

**Query Params:** `from_date`, `to_date`, `limit` (top N), `group_by` (product/color/sku)

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "product_name": "Nike Air Force 1",
      "color_name": "Trắng",
      "size": "39",
      "sku_code": "SP001-WHITE-001-39",
      "sold_quantity": 120,
      "revenue": 270000000
    }
  ]
}
```

---

### 13.4 Báo cáo hiệu quả voucher

**GET** `/v1/admin/reports/vouchers` 🔑

**Query Params:** `from_date`, `to_date`, `voucher_id`

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "voucher_code": "SALE10",
      "voucher_type": "percent",
      "used_count": 23,
      "total_discount_amount": 4600000,
      "total_order_value": 105800000
    }
  ]
}
```

---

## 14. MÃ LỖI NGHIỆP VỤ (Error Codes)

| Code | HTTP | Mô tả | Ràng buộc |
|---|---|---|---|
| `PRODUCT_NAME_REQUIRED` | 400 | Tên sản phẩm không được để trống | BR-PRO-01 |
| `DUPLICATE_COLOR_CODE` | 409 | Mã màu đã tồn tại trong sản phẩm | BR-PRO-05 |
| `DUPLICATE_SKU_CODE` | 409 | Mã SKU đã tồn tại trong hệ thống | BR-PRO-06 |
| `CANNOT_DELETE_PRODUCT` | 422 | Không xóa được sản phẩm đã có đơn hàng | BR-PRO-07 |
| `INVALID_PRICE` | 400 | Giá bán phải lớn hơn 0 | BR-PRI-01 |
| `INVALID_DISCOUNT` | 400 | Giảm giá không hợp lệ | BR-PRI-02, BR-PRI-03 |
| `OUT_OF_STOCK` | 422 | SKU đã hết hàng | BR-STK-03 |
| `QUANTITY_EXCEEDS_STOCK` | 422 | Số lượng vượt tồn kho | BR-STK-04 |
| `STOCK_CANNOT_BE_NEGATIVE` | 422 | Tồn kho không được âm | BR-STK-02 |
| `VOUCHER_NOT_FOUND` | 404 | Mã voucher không tồn tại | BR-VOU |
| `VOUCHER_EXPIRED` | 422 | Voucher đã hết hạn | BR-VOU-02 |
| `VOUCHER_USAGE_EXCEEDED` | 422 | Voucher đã hết lượt sử dụng | BR-VOU-03 |
| `VOUCHER_MIN_ORDER_NOT_MET` | 422 | Đơn hàng chưa đạt giá trị tối thiểu | BR-VOU-04 |
| `ORDER_INFO_MISSING` | 400 | Thiếu thông tin nhận hàng | BR-ORD-01 |
| `ORDER_CANNOT_BE_CANCELLED` | 422 | Đơn không thể hủy ở trạng thái này | BR-ORD-03 |
| `INVALID_STATUS_TRANSITION` | 422 | Chuyển trạng thái đơn không hợp lệ | |
| `DUPLICATE_VOUCHER_CODE` | 409 | Mã voucher đã tồn tại | |
| `UNAUTHORIZED` | 401 | Chưa xác thực | |
| `FORBIDDEN` | 403 | Không có quyền thực hiện | |

---

## 15. TỔNG HỢP ENDPOINTS

### Nhóm Public 🌐
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/v1/auth/register` | Đăng ký |
| POST | `/v1/auth/login` | Đăng nhập khách hàng |
| GET | `/v1/brands` | Danh sách thương hiệu |
| GET | `/v1/categories` | Danh sách danh mục |
| GET | `/v1/products` | Danh sách sản phẩm |
| GET | `/v1/products/{id}` | Chi tiết sản phẩm |
| GET | `/v1/cart` | Xem giỏ hàng |
| POST | `/v1/cart/items` | Thêm vào giỏ |
| PATCH | `/v1/cart/items/{id}` | Cập nhật số lượng |
| DELETE | `/v1/cart/items/{id}` | Xóa khỏi giỏ |
| DELETE | `/v1/cart` | Xóa toàn bộ giỏ |
| POST | `/v1/cart/voucher` | Áp voucher |
| DELETE | `/v1/cart/voucher` | Hủy voucher |
| POST | `/v1/cart/checkout-preview` | Preview tổng tiền |
| POST | `/v1/orders` | Đặt hàng |

### Nhóm Customer 👤
| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/v1/orders` | Lịch sử đơn hàng |
| GET | `/v1/orders/{id}` | Chi tiết đơn hàng |
| PATCH | `/v1/orders/{id}/cancel` | Hủy đơn |
| POST | `/v1/orders/{id}/returns` | Yêu cầu đổi trả |

### Nhóm Staff/Admin 👷
| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/v1/admin/products` | DS sản phẩm (admin view) |
| PATCH | `/v1/admin/skus/{id}/stock` | Cập nhật tồn kho |
| GET | `/v1/admin/skus/{id}/stock-logs` | Lịch sử tồn kho |
| GET | `/v1/admin/orders` | DS đơn hàng |
| GET | `/v1/admin/orders/{id}` | Chi tiết đơn |
| PATCH | `/v1/admin/orders/{id}/status` | Cập nhật trạng thái đơn |
| PATCH | `/v1/admin/orders/{id}/cancel` | Hủy đơn (nhân viên) |
| GET | `/v1/admin/returns` | DS yêu cầu đổi trả |
| PATCH | `/v1/admin/returns/{id}/review` | Duyệt đổi trả |
| PATCH | `/v1/admin/returns/{id}/complete` | Hoàn tất đổi trả |
| GET | `/v1/admin/reports/inventory` | Báo cáo tồn kho |
| GET | `/v1/admin/reports/best-sellers` | Sản phẩm bán chạy |

### Nhóm Admin only 🔑
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/v1/auth/admin/login` | Đăng nhập nội bộ |
| POST | `/v1/admin/brands` | Tạo thương hiệu |
| PUT | `/v1/admin/brands/{id}` | Sửa thương hiệu |
| PATCH | `/v1/admin/brands/{id}/status` | Trạng thái thương hiệu |
| POST | `/v1/admin/categories` | Tạo danh mục |
| PUT | `/v1/admin/categories/{id}` | Sửa danh mục |
| PATCH | `/v1/admin/categories/{id}/status` | Trạng thái danh mục |
| POST | `/v1/admin/products` | Tạo sản phẩm |
| PUT | `/v1/admin/products/{id}` | Sửa sản phẩm |
| PATCH | `/v1/admin/products/{id}/status` | Trạng thái sản phẩm |
| POST | `/v1/admin/products/{id}/colors` | Thêm màu |
| PUT | `/v1/admin/products/{id}/colors/{cid}` | Sửa màu |
| PATCH | `/v1/admin/products/{id}/colors/{cid}/pricing` | Sửa giá/giảm giá |
| PATCH | `/v1/admin/products/{id}/colors/{cid}/status` | Trạng thái màu |
| POST | `/v1/admin/products/{id}/colors/{cid}/images` | Upload ảnh |
| PATCH | `/v1/admin/products/{id}/colors/{cid}/images/reorder` | Sắp xếp ảnh |
| DELETE | `/v1/admin/products/{id}/colors/{cid}/images/{iid}` | Xóa ảnh |
| POST | `/v1/admin/products/{id}/colors/{cid}/skus` | Thêm size/SKU |
| PATCH | `/v1/admin/products/{id}/colors/{cid}/skus/{sid}/status` | Trạng thái SKU |
| GET | `/v1/admin/vouchers` | DS voucher |
| POST | `/v1/admin/vouchers` | Tạo voucher |
| PUT | `/v1/admin/vouchers/{id}` | Sửa voucher |
| PATCH | `/v1/admin/vouchers/{id}/status` | Trạng thái voucher |
| GET | `/v1/admin/vouchers/{id}/usages` | Lịch sử dùng voucher |
| GET | `/v1/admin/reports/revenue` | Báo cáo doanh thu |
| GET | `/v1/admin/reports/vouchers` | Báo cáo voucher |
