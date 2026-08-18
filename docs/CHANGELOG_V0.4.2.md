# CHANGELOG – V0.4.2 FINAL

## Chốt chức năng sau kiểm thử V0.4.1
- Thêm chỉ tiêu Sắp đến hạn.
- Hiển thị rõ Vượt ngân sách.
- Phát sinh có Duyệt/Từ chối.
- Nghiệm thu có lỗi/tồn tại và hạn khắc phục.
- Thanh toán có Còn phải trả và cập nhật thanh toán.
- Vật tư có mua vượt, tồn kho, giá trị mua.
- Nhân công có thành tiền.
- Bảo hành/bảo trì có cảnh báo hạn.
- Giữ báo cáo và sao lưu SQLite.

## Chốt cấu trúc Views
- Tách 13 màn hình khỏi `app.py` thành 13 file trong `views/`.
- `app.py` trở thành bộ định tuyến.
- Lõi dùng chung gom tại `core/runtime.py`.
- Không thay `data/deliveryos.db`.

## Hoàn thiện liên kết triển khai

- Bổ sung Streamlit Live App vào README.
- Bổ sung GitHub Repository link vào README.
- Chốt quy chuẩn: mọi Repository có Streamlit phải gắn link ứng dụng ở README và About/Website.
