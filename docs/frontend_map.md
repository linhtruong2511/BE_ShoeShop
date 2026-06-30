# KIẾN TRÚC FRONTEND - WEBSITE BÁN GIÀY (FE_ShoeShop)

> Tài liệu tổng hợp cấu trúc thư mục và kiến trúc của ứng dụng Frontend hiện tại.
> Công nghệ sử dụng: Vue 3 (Composition API), Vite, TypeScript, Tailwind CSS, Vue Router, Pinia (quản lý state).

---

## MỤC LỤC
- [1. TỔNG QUAN CẤU TRÚC THƯ MỤC](#1-tổng-quan-cấu-trúc-thư-mục)
- [2. CHI TIẾT CÁC THÀNH PHẦN](#2-chi-tiết-các-thành-phần)
- [3. KIẾN TRÚC NGHIỆP VỤ NỔI BẬT](#3-kiến-trúc-nghiệp-vụ-nổi-bật)

---

## 1. TỔNG QUAN CẤU TRÚC THƯ MỤC

Dự án được cấu trúc theo tiêu chuẩn của một ứng dụng Vue 3 với Vite, tách biệt rõ ràng các thành phần giao diện, logic định tuyến, quản lý trạng thái và kiểu dữ liệu.

```text
FE_ShoeShop/
├── public/                 # Các tài nguyên tĩnh (favicon, v.v.)
├── src/                    # Chứa mã nguồn chính của ứng dụng
│   ├── assets/             # Hình ảnh, font chữ, CSS chung
│   ├── components/         # Các thành phần giao diện tái sử dụng
│   │   ├── common/         # Component dùng chung (ví dụ: thẻ sản phẩm)
│   │   └── layout/         # Component bố cục (Header, Footer, Sidebar)
│   ├── mocks/              # Dữ liệu giả lập (Mock data) cho phát triển
│   ├── router/             # Cấu hình định tuyến (Vue Router)
│   ├── stores/             # Quản lý trạng thái toàn cục (Pinia)
│   ├── types/              # Định nghĩa kiểu dữ liệu TypeScript (Interfaces/Types)
│   ├── views/              # Các trang chính của ứng dụng (Pages)
│   │   └── admin/          # Các trang dành cho phân hệ Quản trị viên
│   ├── App.vue             # Component gốc của ứng dụng
│   ├── main.ts             # Điểm khởi chạy ứng dụng (Entry point)
│   └── style.css           # Cấu hình CSS toàn cục (Tailwind directives)
├── index.html              # HTML template gốc
├── package.json            # Quản lý thư viện và scripts
├── tsconfig.json           # Cấu hình TypeScript
└── vite.config.ts          # Cấu hình Vite bundler
```

---

## 2. CHI TIẾT CÁC THÀNH PHẦN

### 2.1 Thành phần giao diện (Components)

- **`src/components/layout/`**: Định nghĩa cấu trúc khung của trang web.
  - `Header.vue`: Thanh điều hướng trên cùng, bao gồm logo, menu, thanh tìm kiếm và icon giỏ hàng.
  - `Footer.vue`: Chân trang với các thông tin liên hệ, liên kết nhanh.
  - `AdminLayout.vue`: Bố cục dành riêng cho trang quản trị, bao gồm sidebar menu quản trị.
  - `CartDrawer.vue`: Ngăn kéo giỏ hàng trượt từ bên phải, hiển thị tóm tắt giỏ hàng.

- **`src/components/common/`**: Các thành phần giao diện nhỏ, độc lập.
  - `ProductCard.vue`: Thẻ hiển thị thông tin tóm tắt của một sản phẩm (hình ảnh, tên, giá, hãng), dùng trong danh sách sản phẩm.

### 2.2 Các trang ứng dụng (Views)

Hệ thống view được chia làm 2 phần chính: Customer (Khách hàng) và Admin (Quản trị).

**Phân hệ Khách hàng (`src/views/`)**:
- `HomeView.vue`: Trang chủ, hiển thị banner, sản phẩm nổi bật, sản phẩm mới.
- `ProductListView.vue`: Trang danh sách sản phẩm, có bộ lọc theo hãng, giá, kích cỡ, màu sắc.
- `ProductDetailView.vue`: Trang chi tiết một sản phẩm, cho phép chọn màu, size và thêm vào giỏ hàng. Kiểm tra tồn kho dựa trên SKU.
- `CheckoutView.vue`: Trang thanh toán, nhập thông tin giao hàng, áp dụng mã giảm giá và tính toán tổng tiền.
- `OrderHistoryView.vue`: Trang lịch sử đơn hàng của người dùng.
- `OrderDetailView.vue`: Trang chi tiết một đơn hàng đã đặt, hỗ trợ hủy đơn hoặc gửi yêu cầu đổi/trả hàng.

**Phân hệ Quản trị (`src/views/admin/`)**:
- `AdminDashboardView.vue`: Bảng điều khiển thống kê tổng quan (doanh thu, đơn hàng, tồn kho, sản phẩm bán chạy).
- `AdminProductListView.vue`: Trang quản lý danh mục sản phẩm (mô hình 3 cấp: Product -> Color -> SKU), quản lý tồn kho và lịch sử kho.
- `AdminOrderListView.vue`: Trang quản lý danh sách đơn hàng và yêu cầu đổi/trả hàng.
- `AdminVoucherListView.vue`: Trang quản lý các mã giảm giá (vouchers).

### 2.3 Quản lý trạng thái (Stores)

- **`src/stores/cart.ts`**: Store quản lý giỏ hàng. Chịu trách nhiệm:
  - Lưu trữ danh sách sản phẩm trong giỏ (lưu ý theo `sku_id` để kiểm soát tồn kho).
  - Quản lý logic tính toán tổng tiền, phí giao hàng.
  - Áp dụng và tính toán tiền giảm giá từ Voucher.
  - Kiểm tra tồn kho của SKU.

### 2.4 Dữ liệu và Kiểu dữ liệu

- **`src/types/index.ts`**: Định nghĩa tất cả các giao thức (interfaces) dùng trong ứng dụng, đảm bảo tính chặt chẽ của TypeScript. Bao gồm: `Product`, `ProductColor`, `ProductSku`, `Order`, `OrderDetail`, `Voucher`, v.v.
- **`src/mocks/products.ts`**: Chứa dữ liệu giả lập chi tiết phục vụ cho việc phát triển giao diện khi chưa có Backend thực. Bao gồm danh sách sản phẩm 3 cấp, danh sách mã giảm giá.

### 2.5 Định tuyến (Router)

- **`src/router/index.ts`**: Quản lý điều hướng URL của ứng dụng. Ánh xạ các đường dẫn (paths) tới các component View tương ứng (ví dụ: `/checkout` tới `CheckoutView.vue`, `/admin/products` tới `AdminProductListView.vue`). Tích hợp `AdminLayout.vue` như một layout bọc ngoài cho các route `/admin/*`.

---

## 3. KIẾN TRÚC NGHIỆP VỤ NỔI BẬT

1. **Mô hình Dữ liệu Sản phẩm 3 Cấp**: 
   - Hệ thống được thiết kế hỗ trợ sản phẩm phức tạp: `Sản phẩm Gốc (Product)` -> `Biến thể Màu (ProductColor)` -> `Biến thể Size (ProductSku)`. 
   - Tồn kho và giá cả (khi có giảm giá riêng biệt) được quản lý chặt chẽ ở cấp độ SKU và Color.
2. **Kiểm soát Tồn kho Thời gian thực (Mô phỏng)**:
   - Giao diện người dùng sẽ khóa (disable) các lựa chọn size đã hết hàng.
   - Ngăn chặn việc thêm vào giỏ hàng nếu số lượng vượt quá tồn kho hiện tại của SKU.
3. **Thiết kế Component-Based**:
   - Khuyến khích tái sử dụng giao diện (`ProductCard`, `CartDrawer`).
   - Tách biệt logic kinh doanh (Stores) ra khỏi giao diện hiển thị (Views/Components).
