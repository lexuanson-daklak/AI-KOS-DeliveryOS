# CHANGELOG – AI-KOS DeliveryOS V0.6.1

## Tên phiên bản
**V0.6.1 – Trung tâm xuất dữ liệu & bàn giao**

## Bổ sung
1. Nâng View 12 thành `Xuất dữ liệu, báo cáo & sao lưu`.
2. Thêm `core/export_center.py`.
3. Xuất báo cáo Word cho dự án đang chọn.
4. Xuất báo cáo Word toàn danh mục.
5. Xuất Excel dự án và toàn danh mục.
6. Xuất JSON máy đọc.
7. Xuất dữ liệu thô CSV theo từng bảng.
8. Xuất toàn bộ hồ sơ đính kèm từ dữ liệu base64.
9. Sao lưu SQLite `deliveryos.db`.
10. Tạo FULL ZIP cho một dự án.
11. Tạo FULL ZIP cho toàn bộ hệ thống gồm Word + Excel + JSON + CSV + hồ sơ đính kèm + SQLite + MANIFEST.
12. Bổ sung quy chuẩn xuất dữ liệu áp dụng cho các Repository/Streamlit khác trong hệ sinh thái.

## Không thay
- Schema SQLite.
- `data/deliveryos.db`.
- Logic nghiệp vụ của 12 View còn lại.
- Nguyên tắc AI không tự sửa dữ liệu gốc.
