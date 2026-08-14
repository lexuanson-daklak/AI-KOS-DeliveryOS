# AI-KOS DeliveryOS – MVP V0.3

**Tên tiếng Việt:** Nền tảng AI quản trị thực hiện dự án, công trình và vận hành tài sản  
**English Name:** AI-KOS DeliveryOS – AI Project Delivery, Construction & Asset Operations Platform

> Nền tảng AI quản trị thực hiện dự án (xây nhà phố, sửa chữa/cải tạo nhà, xây dựng công trình, cải tạo mặt bằng/đất...) và vận hành tài sản: tiến độ, chi phí, hợp đồng, nhật ký, phát sinh, nghiệm thu, thanh toán, bảo hành, bảo trì. | AI Project Delivery, Construction & Asset Operations Platform

## V0.3 bổ sung gì?

- Màn hình **Hôm nay cần làm gì?** tổng hợp việc quá hạn, sắp đến hạn, phát sinh chờ duyệt, thanh toán và bảo hành/bảo trì.
- **05 mẫu dự án**:
  1. Xây nhà phố
  2. Sửa chữa/cải tạo nhà
  3. Xây dựng công trình
  4. Cải tạo mặt bằng/đất
  5. Quản lý xưởng cơ khí
- Khi tạo dự án mới, hệ thống **tự sinh khung công việc ban đầu**.
- Giao diện bảng biểu ưu tiên tiếng Việt.
- Hồ sơ/hình ảnh nhỏ có thể lưu trực tiếp vào CSDL với metadata.
- Xuất báo cáo Excel theo từng dự án.
- Hỗ trợ **PostgreSQL** để lưu bền dữ liệu; nếu chưa cấu hình thì tự dùng SQLite như bản demo.

## 10 màn hình V0.3

0. Hôm nay cần làm gì?
1. Danh mục dự án
2. Tổng quan
3. Công việc & tiến độ
4. Chi phí & dòng tiền
5. Nhật ký & hồ sơ
6. Phát sinh
7. Nghiệm thu & thanh toán
8. Bảo hành & bảo trì
9. Báo cáo

## CSDL lưu bền

Nếu chưa cấu hình gì, ứng dụng chạy bằng:

`data/deliveryos.db`

Để dùng thật trên Streamlit, nên cấu hình PostgreSQL và thêm vào **Streamlit Secrets**:

```toml
DATABASE_URL = "postgresql://user:password@host:5432/database"
```

Khi có `DATABASE_URL`, ứng dụng tự chuyển sang PostgreSQL.

## Chạy trên máy

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Nguyên tắc

- Kế hoạch – Thực tế – Chênh lệch.
- AI được phân tích/cảnh báo nhưng không tự sửa số liệu gốc.
- Hợp đồng, phát sinh, nghiệm thu, thanh toán phải có người xác nhận.
- Repository Public chỉ sử dụng dữ liệu demo, không lưu mật khẩu/API key/dữ liệu công vụ thật.
