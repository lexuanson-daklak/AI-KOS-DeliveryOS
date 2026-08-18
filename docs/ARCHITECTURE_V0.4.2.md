# KIẾN TRÚC AI-KOS DeliveryOS V0.4.2 FINAL

## Cấu trúc 4 lớp

```text
NGƯỜI DÙNG
   ↓
STREAMLIT / app.py
   ↓
13 VIEWS NGHIỆP VỤ
   ↓
CORE / runtime.py
   ↓
SQLITE / data/deliveryos.db
```

### 1. `app.py` – Bộ định tuyến
- Chọn chức năng.
- Chọn dự án.
- Nạp dữ liệu nền.
- Gọi đúng View.

### 2. `views/` – Các góc nhìn nghiệp vụ
Mỗi View độc lập theo một màn hình, giúp sửa một chức năng mà không phải sửa toàn bộ ứng dụng.

### 3. `core/runtime.py` – Lõi dùng chung
- kết nối SQLite;
- schema dữ liệu;
- định dạng tiền/ngày;
- tạo mã;
- 05 mẫu dự án;
- cảnh báo;
- xuất Excel;
- sao lưu dữ liệu.

### 4. `data/deliveryos.db` – Dữ liệu
Giữ nguyên dữ liệu kiểm thử V0.4.1 hiện có trên GitHub.

## Nguyên tắc
- Một màn hình = một View.
- Không tạo Repository mới cho từng View.
- Không đổi schema dữ liệu trong bản chốt này.
- AI chỉ phân tích/cảnh báo; các phê duyệt nghiệp vụ do con người xác nhận.
