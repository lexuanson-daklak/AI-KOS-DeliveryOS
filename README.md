# AI-KOS DeliveryOS – MVP V0.4.2 FINAL

**Tên tiếng Việt:** Nền tảng AI quản trị thực hiện dự án, công trình và vận hành tài sản  
**English Name:** AI-KOS DeliveryOS – AI Project Delivery, Construction & Asset Operations Platform

## Truy cập nhanh

🌐 **Ứng dụng Streamlit:** https://ai-kos-deliveryos-daklak.streamlit.app  
📦 **GitHub Repository:** https://github.com/lexuanson-daklak/AI-KOS-DeliveryOS  
🏷️ **Phiên bản chốt:** V0.4.2 FINAL

> Quy chuẩn hệ sinh thái: Repository nào đã có ứng dụng Streamlit thì README phải đặt đường link Streamlit ở phần đầu để người dùng mở ứng dụng ngay, không phải nhớ hoặc tìm lại URL.

## Trạng thái chốt

**V0.4.2 FINAL – bản chốt cấu trúc Views.**

Kiến trúc hiện tại: **GitHub → Streamlit → SQLite**.

## Vai trò của từng thành phần

- **GitHub:** lưu mã nguồn, cấu trúc phần mềm, tài liệu và lịch sử phiên bản.
- **Streamlit:** giao diện ứng dụng để sử dụng DeliveryOS.
- **SQLite (`data/deliveryos.db`):** cơ sở dữ liệu thử nghiệm hiện tại.
- **Views:** các màn hình nghiệp vụ độc lập trên Streamlit.

## Cấu trúc GitHub

```text
AI-KOS-DeliveryOS/
├── app.py
├── core/
│   ├── __init__.py
│   └── runtime.py
├── views/
│   ├── __init__.py
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
├── .streamlit/
│   └── config.toml
└── data/
    └── deliveryos.db
```

> Khi cập nhật bản FINAL, **giữ nguyên `data/deliveryos.db` hiện có**.

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

## Luồng nghiệp vụ chính

```text
Danh mục dự án
→ Hồ sơ dự án
→ Công việc & tiến độ
→ Hợp đồng & đối tác
→ Vật tư & nhân công
→ Chi phí & dòng tiền
→ Nhật ký & hồ sơ
→ Phát sinh
→ Nghiệm thu & thanh toán
→ Bảo hành & bảo trì
→ Báo cáo & sao lưu
```

Hai View điều hành xuyên suốt:
- `00. Hôm nay cần làm gì?`
- `03. Tổng quan`

## Nguyên tắc cập nhật

- Mỗi màn hình Streamlit tương ứng một file trong `views/`.
- `app.py` chỉ định tuyến ứng dụng và chuyển ngữ cảnh chung.
- Dữ liệu hiện tại giữ nguyên trong `data/deliveryos.db`.
- AI được phép phân tích, cảnh báo và gợi ý nhưng không tự sửa dữ liệu gốc về tài chính, nghiệm thu, thanh toán hoặc phê duyệt.

## Quy chuẩn link cho các Repository sau này

Mỗi Repository trong hệ sinh thái GitHub của Lê Xuân Sơn khi đã triển khai Streamlit phải có tối thiểu:

1. Tên sản phẩm và mô tả tiếng Việt.
2. English Name để đối chiếu.
3. Link **Streamlit Live App** đặt ở đầu README.
4. Link GitHub Repository.
5. Phiên bản hiện tại.
6. Cấu trúc thư mục/Views.
7. Changelog – lịch sử phiên bản.

**Mục tiêu:** mở GitHub là biết ngay sản phẩm là gì, phiên bản nào và bấm vào đâu để sử dụng ứng dụng.
