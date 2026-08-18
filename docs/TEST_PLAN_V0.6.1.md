# KẾ HOẠCH KIỂM THỬ V0.6.1 – TRUNG TÂM XUẤT DỮ LIỆU

## TC-01 – Dự án đang chọn
Mở View `12. Xuất dữ liệu, báo cáo & sao lưu` → tab `Dự án đang chọn`.

Kỳ vọng có 6 nút:
1. Word.
2. Excel.
3. JSON.
4. CSV ZIP.
5. Hồ sơ đính kèm ZIP.
6. FULL ZIP dự án.

## TC-02 – Toàn bộ danh mục
Kỳ vọng có:
- Word danh mục.
- Excel toàn bộ.
- JSON toàn bộ.
- CSV toàn bộ.
- hồ sơ đính kèm.
- SQLite DB.
- FULL ZIP toàn bộ.

## TC-03 – Kiểm tra FULL ZIP
Mở ZIP và xác nhận có:
- `00_MANIFEST.json`.
- Word.
- Excel.
- JSON.
- thư mục CSV.
- thư mục hồ sơ đính kèm.
- với FULL ZIP toàn bộ: có `deliveryos.db`.

## TC-04 – Word
Mở Word và xác nhận có tiêu đề, thông tin dự án/danh mục, chỉ báo điều hành và các bảng chính.

## TC-05 – Excel
Mở Excel và xác nhận các sheet chính có dữ liệu; sheet `Tong_quan` đứng đầu.

## TC-06 – Không thay dữ liệu
Chỉ tải file không được làm thay đổi bản ghi SQLite.

## TC-07 – Khôi phục
Chỉ kiểm tra giao diện cảnh báo/xác nhận, chưa cần khôi phục DB nếu không có nhu cầu.
