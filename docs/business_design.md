# THIẾT KẾ NGHIỆP VỤ - WEBSITE BÁN GIÀY

> Phiên bản: 1.0 | Ngày: 27/06/2026  
> Phạm vi: Mua bán, Quản lý Sản phẩm, Quản lý Đơn hàng

---

## MỤC LỤC
- [1. TỔNG QUAN HỆ THỐNG](#1-tổng-quan-hệ-thống)
- [2. NGHIỆP VỤ QUẢN LÝ SẢN PHẨM](#2-nghiệp-vụ-quản-lý-sản-phẩm)
- [3. NGHIỆP VỤ MUA HÀNG (PHÍA KHÁCH)](#3-nghiệp-vụ-mua-hàng-phía-khách)
- [4. NGHIỆP VỤ QUẢN LÝ ĐƠN HÀNG](#4-nghiệp-vụ-quản-lý-đơn-hàng)
- [5. NGHIỆP VỤ VOUCHER VÀ KHUYẾN MÃI](#5-nghiệp-vụ-voucher-và-khuyến-mãi)
- [6. QUY TẮC NGHIỆP VỤ TỔNG HỢP](#6-quy-tắc-nghiệp-vụ-tổng-hợp)
- [7. YÊU CẦU PHI CHỨC NĂNG](#7-yêu-cầu-phi-chức-năng)
- [8. TIÊU CHÍ NGHIỆM THU](#8-tiêu-chí-nghiệm-thu)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mục tiêu nghiệp vụ

Website bán giày cho phép khách hàng tìm kiếm, lựa chọn và đặt mua giày trực tuyến. Hệ thống hỗ trợ mô hình sản phẩm có biến thể theo màu sắc và kích thước (size), đảm bảo:

- Hiển thị đúng giá, giảm giá, hình ảnh và tồn kho theo từng biến thể màu/size.
- Quy trình đặt hàng — áp voucher — xử lý đơn — cập nhật tồn kho nhất quán.
- Không bán vượt tồn kho, không mất dữ liệu lịch sử giao dịch.

### 1.2 Phân hệ chính

| Phân hệ | Mô tả |
|---|---|
| **Quản lý sản phẩm** | Sản phẩm gốc, biến thể màu, size/SKU, hình ảnh, giá, giảm giá, tồn kho |
| **Mua hàng (Khách)** | Tìm kiếm, xem sản phẩm, giỏ hàng, voucher, đặt hàng |
| **Quản lý đơn hàng** | Xác nhận, chuẩn bị, giao hàng, hoàn thành, hủy/đổi trả |
| **Voucher & Khuyến mãi** | Tạo, kiểm tra, áp dụng và theo dõi mã giảm giá |
| **Báo cáo** | Tồn kho, doanh thu, bán chạy, hiệu quả voucher |

### 1.3 Vai trò người dùng

| Vai trò | Quyền truy cập |
|---|---|
| **Khách vãng lai** | Xem sản phẩm, tìm kiếm, thêm giỏ hàng tạm thời |
| **Khách hàng** | Đặt hàng, áp voucher, xem lịch sử đơn, yêu cầu hủy/đổi trả |
| **Nhân viên** | Xem & xác nhận đơn, cập nhật trạng thái giao hàng, kiểm tra tồn kho |
| **Quản trị viên** | Toàn quyền: sản phẩm, giá, giảm giá, voucher, tài khoản, báo cáo |

---

## 2. NGHIỆP VỤ QUẢN LÝ SẢN PHẨM

### 2.1 Mô hình sản phẩm 3 cấp

```
Sản phẩm gốc (Product)
    └── Màu sản phẩm (ProductColor)         ← giá, giảm giá, hình ảnh riêng
            └── SKU theo size (ProductSku)   ← tồn kho, số lượng đã bán riêng
```

| Cấp | Dữ liệu quản lý |
|---|---|
| **Sản phẩm gốc** | Tên, thương hiệu, danh mục, mô tả chung, trạng thái hiển thị |
| **Màu sản phẩm** | Mã màu, tên màu, giá bán, loại giảm giá, giá trị giảm, bộ ảnh, trạng thái bán |
| **SKU theo size** | Mã SKU, size, tồn kho, số lượng đã bán, trạng thái còn/hết hàng |

**Lưu ý quan trọng:**
- Mô tả sản phẩm dùng chung cho tất cả màu và size (không lưu lặp).
- Giá và giảm giá gắn theo màu, các size trong cùng màu dùng chung giá màu.
- Mã SKU là duy nhất toàn hệ thống; mã màu là duy nhất trong một sản phẩm.

### 2.2 Quy trình tạo sản phẩm

```
[1] Nhập thông tin sản phẩm gốc
      → Tên, thương hiệu, danh mục, mô tả, trạng thái

[2] Thêm màu cho sản phẩm
      → Mã màu, tên màu, giá bán, loại giảm giá, giá trị giảm, trạng thái

[3] Upload hình ảnh theo màu
      → Nhiều ảnh/màu; chọn ảnh đại diện; sắp xếp thứ tự hiển thị

[4] Thêm size trong từng màu
      → Hệ thống tự sinh SKU; nhập tồn kho ban đầu

[5] Kiểm tra & kích hoạt
      → Phải có ≥1 màu đang hoạt động và ≥1 SKU đang hoạt động mới hiển thị
```

**Điều kiện hiển thị sản phẩm trên website:**
- Sản phẩm gốc có `status = active`.
- Có ít nhất 1 màu có `status = active`.
- Màu đó phải có ít nhất 1 SKU có `status = active`.

### 2.3 Quy trình cập nhật tồn kho

| Tình huống | Hành động | Ghi log |
|---|---|---|
| Nhập thêm hàng | Tăng `stock_quantity` của SKU | Lý do: "Nhập hàng", số lượng, người thực hiện |
| Điều chỉnh sau kiểm kho | Tăng/giảm `stock_quantity` | Lý do: "Kiểm kho điều chỉnh", chênh lệch, người thực hiện |
| Đặt hàng thành công | Giảm `stock_quantity` | Lý do: "Xuất theo đơn hàng", mã đơn |
| Hủy đơn (đã trừ kho) | Tăng `stock_quantity` | Lý do: "Hoàn kho do hủy đơn", mã đơn |
| Đổi size/màu | Tăng SKU trả về; giảm SKU đổi sang | Lý do: "Đổi trả hàng", mã đơn |

**Ràng buộc tồn kho:**
- Tồn kho không được âm (`stock_quantity ≥ 0`).
- Không cho đặt hàng hoặc tăng số lượng trong giỏ vượt quá tồn kho hiện có.
- `sold_quantity` chỉ tăng khi đơn chuyển sang trạng thái **Hoàn thành**.

### 2.4 Quy trình cập nhật giá và giảm giá

- Giá và giảm giá được cập nhật theo từng màu bởi Quản trị viên.
- Mọi thay đổi giá/giảm giá phải được ghi audit log (người sửa, thời gian, giá trị cũ → mới).
- Đơn hàng đã tạo **không bị ảnh hưởng** khi giá thay đổi sau này (lưu `unit_price` snapshot tại thời điểm mua).

### 2.5 Ẩn và ngừng kinh doanh sản phẩm

| Hành động | Điều kiện | Hệ quả |
|---|---|---|
| Ẩn sản phẩm | Bất kỳ lúc nào | Không hiển thị trên website; dữ liệu giữ nguyên |
| Ngừng bán màu | Bất kỳ lúc nào | Màu đó không thể đặt hàng mới |
| Ngừng bán SKU | Bất kỳ lúc nào | Size đó bị khóa, không thể thêm giỏ |
| Xóa vật lý | **KHÔNG CHO PHÉP** nếu đã phát sinh đơn hàng | Chỉ chuyển trạng thái |

---

## 3. NGHIỆP VỤ MUA HÀNG (PHÍA KHÁCH)

### 3.1 Luồng xem và chọn sản phẩm

```
[1] Danh sách sản phẩm
      → Hiển thị ảnh đại diện, tên, giá từ thấp nhất/giá màu mặc định,
         % giảm giá (nếu có), badge "Còn hàng / Hết hàng"

[2] Tìm kiếm & lọc
      → Tên sản phẩm, thương hiệu, danh mục, màu, size,
         khoảng giá, trạng thái còn hàng, đang giảm giá

[3] Xem chi tiết sản phẩm
      → Mô tả chung + màu mặc định hiển thị trước

[4] Chọn màu
      → Hệ thống đổi: ảnh, giá, % giảm giá, danh sách size theo màu đó

[5] Chọn size
      → Kiểm tra SKU tương ứng:
         • Còn hàng → nút "Thêm giỏ hàng" kích hoạt
         • Hết hàng → nút "Thêm giỏ hàng" bị khóa, hiển thị "Hết hàng"

[6] Thêm vào giỏ
      → Yêu cầu: đã chọn đủ màu + size; số lượng ≤ tồn kho hiện có
```

### 3.2 Luồng quản lý giỏ hàng

Dữ liệu lưu mỗi dòng giỏ hàng:

| Trường | Mô tả |
|---|---|
| SKU | Mã SKU cụ thể (xác định màu + size) |
| Tên sản phẩm | Tên hiển thị |
| Màu | Tên màu |
| Size | Kích cỡ |
| Ảnh theo màu | URL ảnh đại diện của màu |
| Giá gốc | Giá của màu tại thời điểm thêm giỏ |
| Giảm giá sản phẩm | % hoặc giá trị giảm theo màu |
| Giá sau giảm | Giá gốc − giảm giá sản phẩm |
| Số lượng | Số lượng đặt |

**Nghiệp vụ giỏ hàng:**
- Tăng số lượng → kiểm tra không vượt tồn kho hiện có.
- Giảm số lượng → nếu về 0, xóa dòng đó khỏi giỏ.
- Xóa dòng → hệ thống tính lại tổng tiền tự động.
- Khách vãng lai: giỏ hàng lưu theo `session_id`; khi đăng nhập, giỏ sẽ được merge với tài khoản.

### 3.3 Luồng áp voucher và tính tiền

```
Tổng thanh toán = Tổng tiền sau giảm giá sản phẩm − Giảm voucher + Phí giao hàng
```

**Các bước tính tiền:**

```
[1] Tính giá từng dòng giỏ hàng:
      Giá sau giảm = Giá màu × (1 − % giảm giá) hoặc Giá màu − Giá trị giảm cố định

[2] Cộng tất cả dòng giỏ → Tạm tính (subtotal)

[3] Khách nhập mã voucher (tùy chọn)
      → Hệ thống kiểm tra: tồn tại, còn hiệu lực, còn lượt, đạt đơn tối thiểu,
         đúng phạm vi áp dụng, khách chưa vượt giới hạn sử dụng

[4] Tính giảm voucher:
      • Phần trăm: discount = subtotal × % (tối đa max_discount nếu có)
      • Tiền cố định: discount = giá trị voucher (nếu subtotal ≥ min_order)
      • Miễn phí vận chuyển: discount = phí giao hàng

[5] Cộng phí giao hàng → Tổng thanh toán cuối cùng
```

**Ràng buộc voucher:**
- Mỗi đơn hàng chỉ áp dụng tối đa **1 voucher**.
- Voucher phải: còn hạn + còn lượt tổng + khách chưa vượt lượt/người + đơn đạt tối thiểu.

### 3.4 Luồng đặt hàng

```
[1] Khách nhấn "Đặt hàng / Thanh toán"

[2] Nhập thông tin nhận hàng:
      → Họ tên, số điện thoại, địa chỉ giao hàng, ghi chú (tùy chọn)
      → Phương thức thanh toán (COD / chuyển khoản / ...)
      → Phương thức giao hàng

[3] Hệ thống kiểm tra lại tại thời điểm đặt hàng:
      → Tồn kho từng SKU (tránh giỏ hàng đã cũ)
      → Voucher còn hợp lệ

[4] Nếu hợp lệ → Tạo đơn hàng:
      • Trạng thái: Chờ xác nhận
      • Lưu snapshot: giá tại thời điểm mua, giảm giá, voucher, phí vận chuyển
      • Tạo các dòng order_detail theo từng SKU

[5] Xử lý tồn kho:
      → Trừ tồn kho ngay khi tạo đơn (hoặc khi xác nhận, theo chính sách cấu hình)
      → Ghi StockLog

[6] Thông báo:
      → Khách hàng nhận xác nhận đặt hàng thành công
      → Đơn xuất hiện trong trang quản trị của nhân viên
```

---

## 4. NGHIỆP VỤ QUẢN LÝ ĐƠN HÀNG

### 4.1 Vòng đời trạng thái đơn hàng

```
                    ┌──────────────────────────────────────┐
                    │                                      │
  [Chờ xác nhận] ──→ [Đã xác nhận] ──→ [Đang chuẩn bị] ──→ [Đang giao hàng] ──→ [Hoàn thành]
         │                │                    │                                        │
         │                │                    │                                        │
         └────────────────┴────────────────────┘                           sold_quantity tăng
                          │
                     [Đã hủy] ←── hoàn tồn kho nếu đã trừ
```

| Trạng thái | Ai thực hiện | Điều kiện |
|---|---|---|
| Chờ xác nhận | Hệ thống tự động | Khi khách đặt hàng thành công |
| Đã xác nhận | Nhân viên | Kiểm tra thông tin hợp lệ |
| Đang chuẩn bị | Nhân viên | Sau khi xác nhận |
| Đang giao hàng | Nhân viên | Bàn giao cho đơn vị vận chuyển |
| Hoàn thành | Nhân viên / Tự động | Khách nhận hàng thành công |
| Đã hủy | Khách hoặc nhân viên | Chỉ khi chưa ở trạng thái "Đang giao hàng" hoặc "Hoàn thành" |

**Khi đơn chuyển sang Hoàn thành:**
- Tăng `sold_quantity` của từng SKU trong đơn.
- Tăng `sold_quantity` tổng của màu và sản phẩm gốc (aggregate).

### 4.2 Luồng xử lý đơn hàng (Nhân viên)

```
[1] Lọc đơn theo trạng thái "Chờ xác nhận"

[2] Xem chi tiết đơn:
      → Thông tin khách hàng, địa chỉ giao hàng
      → Danh sách SKU: tên sản phẩm, màu, size, số lượng, đơn giá, tổng dòng

[3] Xác nhận đơn → trạng thái: "Đã xác nhận"

[4] Chuẩn bị hàng theo đúng SKU/màu/size

[5] Bàn giao vận chuyển → trạng thái: "Đang giao hàng"

[6] Xác nhận giao thành công → trạng thái: "Hoàn thành"
      → Hệ thống tự động tăng sold_quantity
```

### 4.3 Luồng hủy đơn

```
[1] Khách hoặc nhân viên gửi yêu cầu hủy

[2] Kiểm tra trạng thái đơn:
      • Cho phép hủy: "Chờ xác nhận", "Đã xác nhận", "Đang chuẩn bị"
      • KHÔNG cho phép hủy: "Đang giao hàng", "Hoàn thành"

[3] Nhân viên nhập lý do hủy (bắt buộc nếu do nhân viên khởi tạo)

[4] Chuyển trạng thái → "Đã hủy"

[5] Hoàn tồn kho:
      → Nếu đơn đã trừ kho, hoàn lại stock_quantity từng SKU
      → Ghi StockLog với lý do "Hoàn kho do hủy đơn"

[6] Xử lý voucher:
      → Hoàn lại lượt sử dụng voucher theo chính sách hệ thống
```

### 4.4 Luồng đổi trả hàng

```
[1] Khách gửi yêu cầu đổi trả (trong thời hạn cho phép)
      Lý do: sai size, sai màu, lỗi sản phẩm, giao nhầm, khác

[2] Nhân viên kiểm tra và duyệt yêu cầu

[3] Nhận lại hàng, kiểm tra tình trạng sản phẩm

[4a] Nếu đổi size/màu:
      → Tăng stock_quantity SKU cũ (hàng trả về)
      → Giảm stock_quantity SKU mới (hàng đổi đi)
      → Ghi StockLog cho cả hai SKU

[4b] Nếu hoàn tiền:
      → Tạo bản ghi hoàn trả
      → Cập nhật trạng thái đơn liên quan
      → Tăng stock_quantity SKU trả về

[5] Ghi nhận return_request với trạng thái xử lý
```

---

## 5. NGHIỆP VỤ VOUCHER VÀ KHUYẾN MÃI

### 5.1 Phân loại voucher

| Loại | Cách giảm | Điều kiện |
|---|---|---|
| **Phần trăm** | Giảm x% tổng đơn, có thể có mức giảm tối đa | Đơn ≥ min_order |
| **Tiền cố định** | Giảm x đồng khỏi tổng đơn | Đơn ≥ min_order |
| **Miễn phí vận chuyển** | Giảm hoặc miễn phí giao hàng | Theo điều kiện voucher |

### 5.2 Thuộc tính voucher

| Thuộc tính | Mô tả |
|---|---|
| Mã voucher | Chuỗi duy nhất, khách nhập để áp dụng |
| Loại giảm | Phần trăm / Tiền cố định / Miễn phí vận chuyển |
| Giá trị giảm | % hoặc số tiền cụ thể |
| Đơn tối thiểu | Giá trị đơn tối thiểu để áp dụng |
| Giảm tối đa | Chỉ có khi loại = phần trăm |
| Ngày bắt đầu | Thời điểm voucher có hiệu lực |
| Ngày kết thúc | Thời điểm voucher hết hạn |
| Tổng lượt dùng | Giới hạn sử dụng toàn hệ thống |
| Lượt dùng/người | Giới hạn sử dụng trên mỗi khách hàng |
| Trạng thái | Đang hoạt động / Tạm dừng / Hết hạn |

### 5.3 Quy tắc kiểm tra voucher

Hệ thống từ chối voucher nếu bất kỳ điều kiện nào dưới đây không thỏa:

1. Mã voucher tồn tại trong hệ thống.
2. Voucher đang ở trạng thái hoạt động.
3. Ngày hiện tại nằm trong khoảng `start_date` ÷ `end_date`.
4. Tổng lượt sử dụng chưa đạt `usage_limit`.
5. Khách hàng chưa vượt `max_usage_per_customer`.
6. Giá trị đơn (subtotal) ≥ `min_order_amount`.

---

## 6. QUY TẮC NGHIỆP VỤ TỔNG HỢP

### 6.1 Sản phẩm

| Mã | Quy tắc |
|---|---|
| BR-PRO-01 | Tên sản phẩm không được để trống |
| BR-PRO-02 | Sản phẩm phải có ≥1 màu đang hoạt động mới được hiển thị |
| BR-PRO-03 | Màu phải có ≥1 SKU đang hoạt động mới được bán |
| BR-PRO-04 | Mô tả sản phẩm dùng chung cho tất cả màu và size |
| BR-PRO-05 | Mã màu không được trùng trong cùng một sản phẩm |
| BR-PRO-06 | Mã SKU không được trùng trong toàn hệ thống |
| BR-PRO-07 | Không xóa vật lý sản phẩm/màu/SKU đã phát sinh đơn; chỉ chuyển trạng thái |

### 6.2 Giá và giảm giá

| Mã | Quy tắc |
|---|---|
| BR-PRI-01 | Giá bán của màu phải > 0 |
| BR-PRI-02 | Giảm giá không được âm |
| BR-PRI-03 | Nếu giảm theo %, giá trị phải trong khoảng 0% ÷ 100% |
| BR-PRI-04 | Giá và giảm giá áp dụng theo màu, không áp chung toàn sản phẩm |
| BR-PRI-05 | Các size trong cùng màu dùng chung giá của màu đó |
| BR-PRI-06 | Đơn hàng phải lưu giá snapshot tại thời điểm mua |

### 6.3 Tồn kho

| Mã | Quy tắc |
|---|---|
| BR-STK-01 | Tồn kho quản lý theo SKU (màu + size) |
| BR-STK-02 | Tồn kho không được âm |
| BR-STK-03 | Không cho thêm giỏ hoặc đặt hàng khi SKU hết hàng |
| BR-STK-04 | Số lượng trong giỏ không vượt tồn kho có thể bán |
| BR-STK-05 | Hủy đơn → hoàn lại tồn kho nếu đơn đã trừ kho |
| BR-STK-06 | `sold_quantity` chỉ tăng khi đơn chuyển sang "Hoàn thành" |

### 6.4 Voucher và đơn hàng

| Mã | Quy tắc |
|---|---|
| BR-VOU-01 | Mỗi đơn hàng chỉ áp tối đa 1 voucher |
| BR-VOU-02 | Voucher phải còn hạn và đang hoạt động |
| BR-VOU-03 | Voucher phải còn lượt tổng và lượt theo khách hàng |
| BR-VOU-04 | Đơn phải đạt giá trị tối thiểu nếu voucher có điều kiện |
| BR-ORD-01 | Đơn không được tạo nếu thiếu thông tin nhận hàng bắt buộc |
| BR-ORD-02 | Không chỉnh sửa chi tiết đơn sau khi đơn "Hoàn thành" |
| BR-ORD-03 | Không hủy đơn đã "Hoàn thành" |
| BR-ORD-04 | Khi tạo đơn phải kiểm tra lại tồn kho và voucher (tránh giỏ cũ) |

---

## 7. YÊU CẦU PHI CHỨC NĂNG

| Mã | Nhóm | Mô tả | Mức |
|---|---|---|---|
| NFR-01 | Hiệu năng | Danh sách & tìm kiếm phản hồi ≤ 2s; đặt hàng ≤ 3s | Bắt buộc |
| NFR-02 | Nhất quán dữ liệu | Không bán vượt tồn kho; kiểm tra lại kho + voucher khi đặt hàng | Bắt buộc |
| NFR-03 | Bảo mật | Phân quyền 3 cấp; chỉ Admin sửa giá/giảm giá/voucher | Bắt buộc |
| NFR-04 | Khả dụng | Hoạt động ổn định trong giờ bán hàng, chịu tải nhiều người | Bắt buộc |
| NFR-05 | Dễ sử dụng | Giao diện chọn màu/size/voucher rõ ràng; thông báo hết hàng dễ hiểu | Bắt buộc |
| NFR-06 | Bảo trì | Tách module: sản phẩm, đơn hàng, giỏ hàng, voucher, tồn kho | Khuyến nghị |
| NFR-07 | Mở rộng | Có thể thêm thanh toán online, vận chuyển, đánh giá, tích điểm | Khuyến nghị |
| NFR-08 | Audit log | Sửa giá, điều chỉnh kho, hủy đơn → lưu người, thời gian, lý do | Bắt buộc |
| NFR-09 | Sao lưu | Sao lưu định kỳ: sản phẩm, đơn hàng, voucher, tồn kho | Khuyến nghị |

---

## 8. TIÊU CHÍ NGHIỆM THU

| Nhóm | Tiêu chí |
|---|---|
| **Sản phẩm** | Tạo được sản phẩm nhiều màu; mỗi màu có giá, giảm giá, ảnh riêng; mỗi màu có danh sách size và tồn kho riêng |
| **Chi tiết sản phẩm** | Khi chọn màu → đổi đúng ảnh, giá, giảm giá và danh sách size |
| **Giỏ hàng** | Không thêm khi chưa chọn đủ màu/size; không tăng số lượng vượt tồn kho |
| **Voucher** | Áp đúng voucher hợp lệ; từ chối hết hạn/sai điều kiện/hết lượt |
| **Đặt hàng** | Lưu đúng SKU, màu, size, số lượng, giá snapshot, tổng thanh toán |
| **Tồn kho** | Giảm khi đặt hàng; hoàn khi hủy; `sold_quantity` tăng đúng khi hoàn thành |
| **Quản trị** | Admin quản lý sản phẩm/màu/size/kho/voucher/trạng thái đơn theo phân quyền |
