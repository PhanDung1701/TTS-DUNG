# VieNeu-TTS trên Windows

Đã cài mã nguồn VieNeu SDK 3.8.3 với model v3 Turbo, 25 giọng mẫu, ONNX Runtime CPU fp32 trong môi trường `.venv` riêng.

## Mở và sử dụng

1. Nhấp đúp [start-vieneu.cmd](./start-vieneu.cmd), giữ cửa sổ chạy.
2. Mở http://127.0.0.1:7862.
3. Chọn **VieNeu-TTS-v3-Turbo** và **CPU**, bấm **Tải Model** để nạp model đã tải vào RAM.
4. Trong tab **Đọc truyện**, nhập văn bản, chọn giọng rồi bấm **Bắt đầu**.
5. Nghe và tải kết quả. Nhấn Ctrl+C trong cửa sổ chạy để dừng máy chủ.

Giữ bản Turbo mặc định (fp32). Bản int8 cần CPU hỗ trợ VNNI; chưa tải bản int8 hoặc Nano.
Batch Processing không tăng tốc trên CPU. Không cần CUDA/PyTorch cho cấu hình đã cài.
ZeroTTS dùng cổng 7860; Kokoro dùng 7861; VieNeu dùng 7862.

## Nhân bản giọng

Tab **Voice Cloning** nhận đoạn ghi âm mẫu khoảng 3–8 giây. Chọn đoạn rõ giọng, ít nhạc nền/tiếng ồn.
Các model codec, speaker encoder và denoiser đã được tải để hỗ trợ đường chạy CPU.
Phép kiểm tra cài đặt đã xác minh tổng hợp bằng giọng mẫu; chưa đánh giá chất lượng nhân bản giọng riêng.

## Kiểm tra và tái cài

- Mẫu tạo thành công: [hello-vieneu.wav](./outputs/hello-vieneu.wav), giọng Hải Đăng, 48 kHz.
- Giao diện repo cần **Gradio 5.50.0**; Gradio 6 gây lỗi `show_copy_button`.
- [requirements-installed.txt](./requirements-installed.txt) ghi lại các phiên bản đã cài.
- Cache model nằm tại `models/hf-cache`. Launcher đặt `HF_HUB_DISABLE_SYMLINKS=1` để tránh lỗi ONNX đọc external data qua symlink trên Windows.
- [prepare_local.py](./prepare_local.py) tải model và chạy phép thử: `.\.venv\Scripts\python.exe prepare_local.py`.
- Hướng dẫn chính thức: [README](./README.md).

Model tải về là v3 Turbo mã nguồn mở. Bản v4 được tác giả cung cấp riêng qua dịch vụ của họ, không nằm trong cài đặt này.
