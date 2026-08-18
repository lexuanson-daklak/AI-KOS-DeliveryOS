# BẢN ĐỒ VIEWS – V0.4.2 FINAL

| STT | View trên Streamlit | File cấu trúc | Vai trò |
|---|---|---|---|
| 00 | Hôm nay cần làm gì? | `views/v00_today.py` | Tổng hợp quá hạn, sắp hạn, chờ duyệt/thanh toán, bảo hành/bảo trì |
| 01 | Danh mục dự án | `views/v01_portfolio.py` | Danh mục và tạo dự án |
| 02 | Hồ sơ dự án | `views/v02_project_profile.py` | Hồ sơ tổng thể |
| 03 | Tổng quan | `views/v03_dashboard.py` | Tiến độ, chi phí, cảnh báo điều hành |
| 04 | Công việc & tiến độ | `views/v04_tasks.py` | Danh sách việc và cập nhật tiến độ |
| 05 | Hợp đồng & đối tác | `views/v05_contracts.py` | Nhà thầu, đối tác, hợp đồng |
| 06 | Vật tư & nhân công | `views/v06_resources.py` | Vật tư, tồn kho, nhân công |
| 07 | Chi phí & dòng tiền | `views/v07_cost_cashflow.py` | Ngân sách, cam kết, thực tế, dự báo |
| 08 | Nhật ký & hồ sơ | `views/v08_diary_files.py` | Nhật ký hiện trường và tệp hồ sơ |
| 09 | Phát sinh | `views/v09_changes.py` | Tạo, duyệt, từ chối phát sinh |
| 10 | Nghiệm thu & thanh toán | `views/v10_acceptance_payment.py` | Nghiệm thu, lỗi, công nợ, thanh toán |
| 11 | Bảo hành & bảo trì | `views/v11_warranty.py` | Theo dõi hạn và chi phí bảo hành/bảo trì |
| 12 | Báo cáo & sao lưu | `views/v12_reports_backup.py` | Xuất Excel, backup/restore SQLite |

## Luồng nghiệp vụ

```text
Danh mục → Hồ sơ → Công việc → Hợp đồng → Vật tư/Nhân công
→ Chi phí → Nhật ký → Phát sinh → Nghiệm thu → Thanh toán
→ Bảo hành/Bảo trì → Báo cáo
```
