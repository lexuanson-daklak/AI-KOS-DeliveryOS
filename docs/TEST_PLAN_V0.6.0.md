# KẾ HOẠCH KIỂM THỬ V0.6.0

Dùng nguyên bộ 05 dự án kiểm thử hiện tại.

## TC-V06-01 – Mở Trung tâm điều hành
Chọn `00A. Trung tâm điều hành danh mục`.

Kỳ vọng:
- hiện 05 dự án;
- có tổng ngân sách;
- có tổng dự báo cuối kỳ;
- có giá trị dự báo vượt ngân sách;
- có số việc quá hạn;
- có số tiền còn phải thanh toán.

## TC-V06-02 – Xếp hạng rủi ro
Kỳ vọng:
- mỗi dự án có điểm 0–100;
- danh sách sắp từ điểm cao xuống thấp;
- dự án `TEST-OFFICE-005` phải nằm trong nhóm rủi ro cao nhất do vừa chậm tiến độ vừa dự báo vượt ngân sách và có nghiệm thu/phát sinh/thanh toán cần xử lý;
- `TEST-HOUSE-002` phải phản ánh dự báo 3,28 tỷ so với ngân sách 3,20 tỷ.

## TC-V06-03 – Top 3 dự án
Kỳ vọng:
- có 3 dự án ưu tiên;
- mỗi dự án có lý do dễ hiểu: chậm tiến độ, vượt ngân sách, quá hạn, phát sinh, nghiệm thu hoặc thanh toán.

## TC-V06-04 – Soi nhanh một dự án
Chọn từng dự án trong mục `Soi nhanh một dự án`.

Kỳ vọng:
- điểm rủi ro;
- chênh tiến độ;
- chênh dự báo;
- còn phải trả;
- việc quá hạn;
- phát sinh chờ duyệt;
- nghiệm thu còn lỗi;
- bảo hành/bảo trì cần theo dõi.

## TC-V06-05 – Không thay dữ liệu
Chỉ mở View 00A rồi quay sang các View nghiệp vụ.

Kỳ vọng:
- không có bản ghi bị sửa;
- `data/deliveryos.db` giữ nguyên;
- các View 00 và 03 của V0.5.1 vẫn hoạt động như trước.
