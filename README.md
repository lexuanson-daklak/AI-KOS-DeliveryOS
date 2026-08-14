# AI-KOS DeliveryOS – MVP V0.4

**Tên tiếng Việt:** Nền tảng AI quản trị thực hiện dự án, công trình và vận hành tài sản  
**English Name:** AI-KOS DeliveryOS – AI Project Delivery, Construction & Asset Operations Platform

## Quan điểm V0.4

V0.4 giữ kiến trúc **đơn giản**:

**GitHub → Streamlit → SQLite**

Không bổ sung PostgreSQL hay một nguồn dữ liệu bên ngoài ở giai đoạn này.

Để tránh mất dữ liệu thử nghiệm, V0.4 có chức năng **tải bản sao `deliveryos.db` về máy và khôi phục lại khi cần**.

## V0.4 bổ sung

- Hồ sơ dự án có thể chỉnh sửa trực tiếp.
- Hợp đồng & đối tác/nhà thầu.
- Vật tư & nhân công.
- Báo cáo Excel.
- Sao lưu và khôi phục toàn bộ SQLite.
- Giữ màn hình “Hôm nay cần làm gì?” và 05 mẫu dự án.

## 13 màn hình

0. Hôm nay cần làm gì?
1. Danh mục dự án
2. Hồ sơ dự án
3. Tổng quan
4. Công việc & tiến độ
5. Hợp đồng & đối tác
6. Vật tư & nhân công
7. Chi phí & dòng tiền
8. Nhật ký & hồ sơ
9. Phát sinh
10. Nghiệm thu & thanh toán
11. Bảo hành & bảo trì
12. Báo cáo & sao lưu

## Cập nhật từ V0.3

Chỉ cần thay:
- `app.py`
- `requirements.txt`
- `README.md`

và thêm:
- `docs/CHANGELOG_V0.4.md`

**Giữ nguyên thư mục `data` và file `data/deliveryos.db` hiện tại.**

V0.4 tự tạo các bảng mới `partners`, `contracts`, `materials`, `labour_logs` nếu chưa có.
