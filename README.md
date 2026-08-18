# AI-KOS DeliveryOS – V0.5.1

**Tên tiếng Việt:** Nền tảng AI quản trị thực hiện dự án, công trình và vận hành tài sản  
**English Name:** AI-KOS DeliveryOS – AI Project Delivery, Construction & Asset Operations Platform

## Truy cập nhanh

🌐 **Ứng dụng Streamlit:** https://ai-kos-deliveryos-daklak.streamlit.app  
📦 **GitHub Repository:** https://github.com/lexuanson-daklak/AI-KOS-DeliveryOS  
🏷️ **Phiên bản:** V0.5.1 – Vá giao diện bảng điều hành

## V0.5.1 sửa gì?

V0.5.1 là bản vá nhỏ trên nền V0.5.0, không thay logic điều hành và không thay dữ liệu.

- Tiền ở KPI hiển thị gọn theo `tỷ / triệu / nghìn` để không bị cắt.
- Phát sinh chờ duyệt dùng màu cảnh báo thay vì màu xanh tích cực.
- Nghiệm thu còn lỗi/quá hạn khắc phục dùng màu cảnh báo.
- View 00 có chú thích rõ rằng các chỉ tiêu có thể chồng lấn.
- Giữ nguyên 13 Views, `core/command_center.py` và SQLite.

## Kiến trúc giữ nguyên

```text
GitHub
  ↓
Streamlit
  ↓
app.py
  ↓
13 Views
  ↓
core/runtime.py
  +
core/command_center.py
  ↓
SQLite: data/deliveryos.db
```

## Cập nhật từ V0.5.0

Chỉ thay / bổ sung:

```text
app.py
README.md
views/v00_today.py
views/v03_dashboard.py
docs/CHANGELOG_V0.5.1.md
docs/TEST_PLAN_V0.5.1.md
```

**Không thay `core/command_center.py`. Không thay `data/deliveryos.db`.**
