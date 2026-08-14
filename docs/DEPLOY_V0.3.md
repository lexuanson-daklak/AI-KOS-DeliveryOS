# TRIỂN KHAI V0.3 TRÊN STREAMLIT

## Cách cập nhật từ V0.2
Thay/cập nhật:
- `app.py`
- `requirements.txt`
- `README.md`
- thêm `docs/CHANGELOG_V0.3.md`
- thêm `.streamlit/config.toml`

Giữ nguyên `data/deliveryos.db` nếu muốn giữ dữ liệu mẫu V0.2. V0.3 sẽ tự tạo thêm bảng mới còn thiếu.

## Lưu bền dữ liệu
SQLite trên Streamlit Community Cloud chỉ phù hợp demo.

Để dùng thực tế:
1. Tạo PostgreSQL.
2. Lấy chuỗi kết nối `DATABASE_URL`.
3. Trong Streamlit: Manage app → Settings → Secrets.
4. Thêm:
   `DATABASE_URL = "postgresql://..."`
5. Reboot app.

Ứng dụng sẽ nhận biết PostgreSQL và hiển thị “PostgreSQL – lưu bền”.
