# Đọc nhiều chương

1. Tải model ở đầu giao diện, mở tab **📚 Đọc nhiều chương**.
2. Dán toàn bộ kịch bản hoặc tải file TXT UTF-8 theo mẫu:

   ```text
   CHƯƠNG 1: Mở đầu
   Nội dung lời đọc chương một.

   CHƯƠNG 2: Tiếp nối
   Nội dung lời đọc chương hai.
   ```

3. Bấm **Kiểm tra các chương**. Tiêu đề không được đưa vào audio. Sửa trực tiếp
   trong ô kịch bản; tiêu đề phải có số, không trùng số, mỗi chương phải có nội dung.
4. Chọn giọng (bao gồm giọng clone đã lưu). Nếu danh sách trống sau khi tải model,
   bấm **Làm mới danh sách giọng**. Thiết lập batch/nhiệt độ/độ dài đoạn dùng chung
   với tab Đọc truyện. Chương chạy lần lượt; batch GPU xử lý các đoạn trong chương.
5. Bấm **Tạo tất cả / Tiếp tục**. Có thể chọn ghép thêm bản đầy đủ. File WAV được
   đánh số theo thứ tự xuất hiện trong kịch bản, ZIP có bảng đối chiếu tên chương.

Chương hoàn thành được lưu ngay. Nếu dừng hoặc lỗi, bấm chạy tiếp trong cùng phiên:
chương đã xong với cùng nội dung và thiết lập được tái sử dụng. Sửa một chương chỉ
tạo lại chương đó. Đổi giọng, model hoặc thiết lập sinh sẽ tạo lại audio. Không đổi
hay xoá giọng clone trong lúc đang tạo audio. Nút dừng chờ đoạn/batch hiện tại xong.

File được lưu tại `outputs/chapters/<mã công việc>/` khi chạy local. Có thể đổi bằng
biến môi trường `VIENEU_CHAPTER_OUTPUT_DIR`. Khi dùng [Compose production](../docker/docker-compose.prod.yml),
file nằm ở `docker/output_audio/chapters/` trên máy chủ. Compose mount mã nguồn
`apps` từ checkout hiện tại; cần tạo lại container để áp dụng thay đổi mount/env.

Tải lại trang sẽ tạo phiên mới, không tự khôi phục hàng đợi cũ. Các file đã lưu vẫn
còn trên đĩa, gồm `progress.json` và các WAV. Hệ thống không tự xoá kết quả; bạn có
thể dọn các thư mục công việc đã tải xuống khi cần giải phóng dung lượng.

ZIP sau khi dừng hoặc lỗi chỉ chứa chương đã hoàn thành; bản ghép chỉ được tạo khi
đủ tất cả các chương. Nghe thử và kiểm tra nội dung trước khi sử dụng bản cuối.
