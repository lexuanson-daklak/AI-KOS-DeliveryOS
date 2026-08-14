# AI-KOS DeliveryOS – MVP V0.2

**Tên tiếng Việt:** Nền tảng AI quản trị thực hiện dự án, công trình và vận hành tài sản  
**English Name:** AI-KOS DeliveryOS – AI Project Delivery, Construction & Asset Operations Platform

## Mục tiêu

MVP V0.2 dùng một dự án mẫu **Sửa chữa, cải tạo nhà ở cũ** để kiểm chứng kiến trúc quản trị:

**Hồ sơ → Công việc → Tiến độ → Chi phí → Nhật ký → Phát sinh → Nghiệm thu → Thanh toán → Bảo hành → Bảo trì.**

## 7 màn hình MVP

1. Tổng quan
2. Công việc & tiến độ
3. Chi phí & dòng tiền
4. Nhật ký & hình ảnh
5. Phát sinh
6. Nghiệm thu & thanh toán
7. Bảo hành & bảo trì

## Nguyên tắc cốt lõi

- Kế hoạch – Thực tế – Chênh lệch.
- Mỗi công việc, phát sinh, nghiệm thu, thanh toán có mã riêng.
- AI được phân tích/cảnh báo nhưng **không tự sửa số liệu gốc**.
- Dữ liệu tài chính, nghiệm thu và phê duyệt phải có người xác nhận.
- Bản demo không dùng dữ liệu công vụ, mật khẩu, API key hoặc thông tin bí mật.

## Chạy trên máy tính

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Đưa lên GitHub

Repository dự kiến:

`ai-kos-deliveryos`

Sau khi chạy thử ổn định, có thể đưa toàn bộ thư mục này lên GitHub và kết nối Streamlit Community Cloud.

## Dữ liệu

- `data/deliveryos.db`: cơ sở dữ liệu SQLite mẫu, dùng để chạy ứng dụng.
- `data/AI_KOS_DeliveryOS_CSDL_Mau_V0.1.xlsx`: bộ dữ liệu mẫu song song để đọc, kiểm tra và tiếp tục thiết kế.

## Trạng thái

**MVP V0.2 – thử nghiệm kiến trúc nghiệp vụ.**

Chưa phải hệ thống quản lý hợp đồng/kế toán/nghiệm thu chính thức và chưa thay thế hồ sơ pháp lý theo quy định.


## Bổ sung trong V0.2

- Màn hình **00. Danh mục dự án / Project Portfolio**.
- Quản lý đồng thời nhiều dự án.
- Tạo dự án mới trực tiếp trên giao diện.
- Dữ liệu mẫu gồm:
  - Sửa chữa, cải tạo nhà ở cũ.
  - Quản lý xưởng cơ khí mẫu.
  - Công trình sửa chữa văn phòng mẫu.
- Mỗi dự án sử dụng `PROJECT_ID` duy nhất và dùng chung kiến trúc công việc – chi phí – nhật ký – phát sinh – nghiệm thu – thanh toán – bảo hành.

## Mục tiêu V0.3

- Bổ sung phân quyền người dùng.
- Bổ sung hồ sơ hợp đồng và vật tư sâu hơn.
- Tải ảnh có metadata đầy đủ.
- Trang tổng hợp toàn danh mục theo chi phí, tiến độ và cảnh báo.
