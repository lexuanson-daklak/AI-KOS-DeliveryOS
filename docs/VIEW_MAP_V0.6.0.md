# BẢN ĐỒ VIEWS – AI-KOS DeliveryOS V0.6.0

| STT | View | File | Vai trò |
|---|---|---|---|
| 00 | Hôm nay cần làm gì? | `views/v00_today.py` | Danh sách việc cần xử lý |
| 00A | Trung tâm điều hành danh mục | `views/v00a_portfolio_center.py` | So sánh nhiều dự án, xếp hạng rủi ro |
| 01 | Danh mục dự án | `views/v01_portfolio.py` | Danh mục và tạo dự án |
| 02 | Hồ sơ dự án | `views/v02_project_profile.py` | Hồ sơ dự án |
| 03 | Tổng quan | `views/v03_dashboard.py` | Điều hành một dự án |
| 04 | Công việc & tiến độ | `views/v04_tasks.py` | Công việc và tiến độ |
| 05 | Hợp đồng & đối tác | `views/v05_contracts.py` | Hợp đồng, nhà thầu, đối tác |
| 06 | Vật tư & nhân công | `views/v06_resources.py` | Nguồn lực |
| 07 | Chi phí & dòng tiền | `views/v07_cost_cashflow.py` | Chi phí, dự báo, dòng tiền |
| 08 | Nhật ký & hồ sơ | `views/v08_diary_files.py` | Nhật ký và tệp hồ sơ |
| 09 | Phát sinh | `views/v09_changes.py` | Phát sinh và phê duyệt |
| 10 | Nghiệm thu & thanh toán | `views/v10_acceptance_payment.py` | Nghiệm thu và thanh toán |
| 11 | Bảo hành & bảo trì | `views/v11_warranty.py` | Bảo hành/bảo trì |
| 12 | Báo cáo & sao lưu | `views/v12_reports_backup.py` | Xuất báo cáo và sao lưu |

## Ba tầng điều hành

```text
00A. Trung tâm điều hành danh mục
        ↓
Chọn dự án cần ưu tiên
        ↓
03. Tổng quan dự án
        ↓
00. Hôm nay cần làm gì? + các View nghiệp vụ chi tiết
```

Cách hiểu:
- **00A:** dự án nào đáng lo nhất?
- **03:** dự án đó đang vướng ở đâu?
- **00 và 04–12:** hôm nay phải xử lý việc cụ thể nào?
