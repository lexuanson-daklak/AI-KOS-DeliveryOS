# KẾ HOẠCH KIỂM THỬ V0.5.0

Dùng nguyên bộ 05 dự án kiểm thử V0.4.1.

## TC-V05-01 – Toàn bộ danh mục
Mở `00. Hôm nay cần làm gì?` → chọn `Tất cả dự án`.
Kỳ vọng:
- có số liệu tổng việc;
- có mức đỏ;
- có quá hạn;
- có phát sinh chờ duyệt;
- có khoản còn phải trả;
- có nghiệm thu còn lỗi;
- có bảo hành/bảo trì;
- bảng được xếp theo mức ưu tiên giảm dần.

## TC-V05-02 – Dự án OFFICE
Chọn `TEST-OFFICE-005` → View 03.
Kỳ vọng:
- ngân sách 2,4 tỷ;
- dự báo 2,55 tỷ;
- hiển thị vượt 150 triệu;
- tiến độ KH 70%, thực tế 52%, chậm 18 điểm %;
- có phát sinh CHG-O03 chờ duyệt;
- có thanh toán còn thiếu;
- có nghiệm thu còn lỗi/tồn tại;
- trạng thái điều hành mức đỏ.

## TC-V05-03 – Xưởng cơ khí
Chọn `TEST-WORKSHOP-004` → View 03.
Kỳ vọng:
- thấy khoản thanh toán còn thiếu 30 triệu nếu dữ liệu hiện tại còn giữ nguyên;
- thấy lịch bảo trì máy hàn MIG;
- bảng ưu tiên không làm thay đổi dữ liệu nguồn.

## TC-V05-04 – Kiểm tra dữ liệu
Sau khi mở các View:
- vào `12. Báo cáo & sao lưu`;
- tải lại `deliveryos.db`;
- xác nhận việc chỉ xem bảng điều hành không làm thay đổi bản ghi nghiệp vụ.
