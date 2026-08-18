# AI-KOS DeliveryOS – V0.5.0

**Tên tiếng Việt:** Nền tảng AI quản trị thực hiện dự án, công trình và vận hành tài sản  
**English Name:** AI-KOS DeliveryOS – AI Project Delivery, Construction & Asset Operations Platform

## Truy cập nhanh

🌐 **Ứng dụng Streamlit:** https://ai-kos-deliveryos-daklak.streamlit.app  
📦 **GitHub Repository:** https://github.com/lexuanson-daklak/AI-KOS-DeliveryOS  
🏷️ **Phiên bản:** V0.5.0 – Bảng điều hành dự án sống

## Mục tiêu V0.5.0

V0.4.2 đã chốt kiến trúc 13 Views. V0.5.0 giữ nguyên nền móng đó và nâng hai View điều hành:

- `00. Hôm nay cần làm gì?`
- `03. Tổng quan`

Từ dữ liệu hiện có, hệ thống tự tổng hợp và xếp thứ tự ưu tiên:

- công việc quá hạn / sắp đến hạn;
- phát sinh chờ duyệt;
- khoản đã duyệt nhưng chưa thanh toán đủ;
- nghiệm thu còn lỗi hoặc quá hạn khắc phục;
- bảo hành / bảo trì đến hạn;
- chậm tiến độ;
- dự báo vượt ngân sách.

## Kiến trúc

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

### Thành phần mới

```text
core/
└── command_center.py
    ├── command_actions()
    ├── portfolio_metrics()
    ├── project_command_summary()
    └── operating_message()
```

Không đổi cấu trúc bảng SQLite và **không thay `data/deliveryos.db`**.

## Nguyên tắc AI

AI tại V0.5.0:
- được tổng hợp dữ liệu;
- được cảnh báo;
- được xếp ưu tiên;
- được gợi ý việc cần xử lý trước.

AI không:
- tự duyệt phát sinh;
- tự nghiệm thu;
- tự thanh toán;
- tự sửa số liệu tài chính;
- tự thay đổi dữ liệu gốc đã xác nhận.

## Cập nhật từ V0.4.2

Chỉ thay / bổ sung:

```text
app.py
README.md
core/command_center.py
views/v00_today.py
views/v03_dashboard.py
docs/CHANGELOG_V0.5.0.md
docs/TEST_PLAN_V0.5.0.md
```

**Giữ nguyên toàn bộ các View còn lại và `data/deliveryos.db`.**
