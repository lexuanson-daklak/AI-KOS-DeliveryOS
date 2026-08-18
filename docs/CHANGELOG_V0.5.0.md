# CHANGELOG – AI-KOS DeliveryOS V0.5.0

## Tên phiên bản
**V0.5.0 – Bảng điều hành dự án sống**

## Nền tảng kế thừa
V0.4.2 FINAL – cấu trúc 13 Views độc lập.

## Bổ sung
1. View 00 có 8 chỉ tiêu điều hành thay cho bảng theo dõi đơn giản.
2. Tự xếp thứ tự ưu tiên theo mức độ và thời hạn.
3. Tự gom việc từ tiến độ, phát sinh, thanh toán, nghiệm thu, bảo hành/bảo trì.
4. Hiển thị Top 5 việc nên xử lý trước.
5. View 03 trở thành bảng điều hành riêng cho từng dự án.
6. Hiển thị cùng lúc ngân sách, dự báo, tiến độ, thanh toán, phát sinh, lỗi nghiệm thu và bảo trì.
7. Thêm `core/command_center.py` làm lớp tổng hợp điều hành.
8. Không thay schema SQLite.
9. Không thay dữ liệu 5 dự án kiểm thử.
10. Giữ link Streamlit trong README.

## Nguyên tắc an toàn dữ liệu
Các hàm điều hành chỉ READ dữ liệu; không tự UPDATE các bảng nghiệp vụ.
