# AI-KOS DeliveryOS – V0.6.1

**Tên tiếng Việt:** Nền tảng AI quản trị thực hiện dự án, công trình và vận hành tài sản  
**English Name:** AI-KOS DeliveryOS – AI Project Delivery, Construction & Asset Operations Platform

## Truy cập nhanh

🌐 **Ứng dụng Streamlit:** https://ai-kos-deliveryos-daklak.streamlit.app  
📦 **GitHub Repository:** https://github.com/lexuanson-daklak/AI-KOS-DeliveryOS  
🏷️ **Phiên bản:** V0.6.1 – Trung tâm điều hành nhiều dự án + Trung tâm xuất dữ liệu

## Hai nâng cấp chính

### 1. Trung tâm điều hành nhiều dự án
View `00A. Trung tâm điều hành danh mục` so sánh toàn bộ dự án, xếp hạng rủi ro và xác định dự án cần ưu tiên.

### 2. Trung tâm xuất dữ liệu
View `12. Xuất dữ liệu, báo cáo & sao lưu` cho phép tải dữ liệu trực tiếp từ Streamlit.

Định dạng lõi:

- Word `.docx`
- Excel `.xlsx`
- CSV `.csv`
- JSON `.json`
- SQLite `.db`
- ZIP `.zip`

Người dùng có thể:

- tải riêng dự án đang chọn;
- tải riêng từng định dạng;
- tải hồ sơ đính kèm;
- tải toàn bộ dữ liệu thô;
- tải toàn bộ danh mục một lần bằng **FULL ZIP**.

## FULL ZIP toàn bộ hệ thống

```text
AI_KOS_DeliveryOS_FULL_EXPORT_YYYYMMDD_HHMM.zip
├── 00_MANIFEST.json
├── 01_Bao_cao_danh_muc.docx
├── 02_Du_lieu_toan_bo.xlsx
├── 03_Du_lieu_toan_bo.json
├── 04_Du_lieu_tho/
│   ├── projects.csv
│   ├── work_items.csv
│   ├── contracts.csv
│   ├── costs.csv
│   ├── changes.csv
│   ├── acceptances.csv
│   ├── payments.csv
│   └── ...
├── 05_Ho_so_dinh_kem/
└── 06_CSDL_Sao_luu/
    └── deliveryos.db
```

## Kiến trúc

```text
GitHub
  ↓
Streamlit
  ↓
app.py
  ↓
14 Views
  │
  ├── 00A. Trung tâm điều hành danh mục
  └── 12. Xuất dữ liệu, báo cáo & sao lưu
        ↓
core/portfolio_center.py
core/export_center.py
        ↓
core/runtime.py + core/command_center.py
        ↓
SQLite: data/deliveryos.db
```

## Quy chuẩn bắt buộc cho hệ sinh thái GitHub + Streamlit

Mỗi Repository đã triển khai Streamlit phải có:

1. Link Streamlit ở đầu README và About/Website.
2. View/khu vực **Xuất dữ liệu – Báo cáo – Sao lưu**.
3. Tối thiểu Word + Excel + dữ liệu thô + sao lưu + FULL ZIP khi nghiệp vụ cho phép.
4. FULL ZIP phải có `MANIFEST` mô tả gói dữ liệu.
5. Khả năng tải riêng và tải đồng loạt.
6. AI chỉ phân tích/cảnh báo; không tự sửa dữ liệu gốc đã xác nhận.

## Cập nhật từ V0.5.1

Gói V0.6.1 là gói **cộng dồn**, chứa cả nâng cấp V0.6.0 và Trung tâm xuất dữ liệu. Nếu GitHub hiện vẫn là V0.5.1, có thể cập nhật trực tiếp V0.6.1.

Các file thay/bổ sung:

```text
app.py
README.md
requirements.txt
core/portfolio_center.py
core/export_center.py
views/v00a_portfolio_center.py
views/v12_reports_backup.py
docs/CHANGELOG_V0.6.0.md
docs/TEST_PLAN_V0.6.0.md
docs/VIEW_MAP_V0.6.0.md
docs/CHANGELOG_V0.6.1.md
docs/EXPORT_STANDARD_V1.0.md
docs/TEST_PLAN_V0.6.1.md
templates/...
```

**Không thay `data/deliveryos.db`. Không thay 12 View nghiệp vụ còn lại.**
