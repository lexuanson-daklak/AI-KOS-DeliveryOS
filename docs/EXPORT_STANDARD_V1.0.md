# QUY CHUẨN XUẤT DỮ LIỆU GITHUB + STREAMLIT – V1.0

## 1. Mục tiêu
Mọi sản phẩm trong hệ sinh thái phải cho phép người dùng lấy dữ liệu trực tiếp từ Streamlit, không phụ thuộc việc nhớ đường dẫn hoặc vào GitHub tìm file.

## 2. Bộ định dạng lõi
- DOCX: báo cáo/thuyết minh cho người đọc.
- XLSX: dữ liệu quản trị nhiều sheet.
- CSV: dữ liệu thô từng bảng.
- JSON: dữ liệu máy đọc, chuyển giao AI/hệ thống khác.
- DB: sao lưu cơ sở dữ liệu khi sản phẩm dùng SQLite.
- ZIP: tải đồng loạt.

## 3. Chế độ xuất
Mỗi ứng dụng nên có tối thiểu:
- Tải dữ liệu đối tượng/dự án đang chọn.
- Tải toàn bộ danh mục.
- Tải hồ sơ đính kèm.
- Tải dữ liệu thô.
- Tải bản sao lưu CSDL.
- TẢI TOÀN BỘ – FULL ZIP.

## 4. FULL ZIP
FULL ZIP phải có:
- `00_MANIFEST.json`.
- Báo cáo Word.
- Excel quản trị.
- JSON.
- CSV từng bảng.
- Hồ sơ/tệp đính kèm.
- Bản sao CSDL nếu phù hợp.

## 5. Mở rộng theo chuyên ngành
Ngoài bộ lõi, từng sản phẩm có thể bổ sung:
- PDF.
- GeoJSON.
- KML/KMZ.
- Shapefile.
- DXF/CAD.
- ảnh, bản đồ, mô hình BIM hoặc định dạng chuyên ngành khác.

## 6. Nguyên tắc an toàn
- Xuất dữ liệu là thao tác READ, không làm thay đổi dữ liệu gốc.
- Khôi phục CSDL phải có cảnh báo và xác nhận riêng.
- AI không tự sửa số liệu tài chính, nghiệm thu, thanh toán hoặc phê duyệt.

## 7. Cấu trúc khuyến nghị
```text
core/export_center.py
views/vXX_export_center.py hoặc View Báo cáo & sao lưu
templates/word/
templates/excel/
docs/EXPORT_STANDARD_*.md
```

## 8. README
README của Repository phải ghi rõ:
- link Streamlit;
- phiên bản;
- định dạng có thể xuất;
- vị trí View xuất dữ liệu;
- nội dung FULL ZIP.
