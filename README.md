# AI-KOS DeliveryOS – MVP V0.4.2 FINAL

**Tên tiếng Việt:** Nền tảng AI quản trị thực hiện dự án, công trình và vận hành tài sản  
**English Name:** AI-KOS DeliveryOS – AI Project Delivery, Construction & Asset Operations Platform

## Trạng thái chốt

**V0.4.2 FINAL – bản chốt cấu trúc Views.**

Kiến trúc hiện tại: **GitHub → Streamlit → SQLite**.

Không bổ sung PostgreSQL hoặc nguồn dữ liệu ngoài ở giai đoạn này.

## Cấu trúc GitHub

```text
AI-KOS-DeliveryOS/
├── app.py                        # Bộ định tuyến ứng dụng
├── core/
│   └── runtime.py                # CSDL, hàm dùng chung, cảnh báo, mẫu dự án, xuất báo cáo
├── views/
│   ├── v00_today.py
│   ├── v01_portfolio.py
│   ├── v02_project_profile.py
│   ├── v03_dashboard.py
│   ├── v04_tasks.py
│   ├── v05_contracts.py
│   ├── v06_resources.py
│   ├── v07_cost_cashflow.py
│   ├── v08_diary_files.py
│   ├── v09_changes.py
│   ├── v10_acceptance_payment.py
│   ├── v11_warranty.py
│   └── v12_reports_backup.py
├── docs/
│   ├── ARCHITECTURE_V0.4.2.md
│   ├── VIEW_MAP_V0.4.2.md
│   └── CHANGELOG_V0.4.2.md
├── requirements.txt
├── .streamlit/config.toml
└── data/
    └── deliveryos.db             # GIỮ NGUYÊN trên GitHub, không có trong gói update
```

## 13 Views

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

## Nguyên tắc cập nhật

- Mỗi màn hình Streamlit tương ứng một file trong `views/`.
- `app.py` chỉ chọn dự án, chọn View và chuyển ngữ cảnh chung.
- Dữ liệu hiện tại giữ nguyên trong `data/deliveryos.db`.
- Khi cập nhật V0.4.2 FINAL, **không thay file `deliveryos.db`**.
