# KLTN - Tabular Coreset Selection Benchmark

Đây là mã nguồn hệ thống thử nghiệm nén dữ liệu dạng bảng (Tabular Dataset Condensation/Coresets) cho Khóa Luận Tốt Nghiệp. Hệ thống được thiết kế để giải quyết bài toán: Làm thế nào để huấn luyện mô hình Machine Learning/Deep Learning trên một tập dữ liệu khổng lồ một cách nhanh chóng mà vẫn giữ được độ chính xác (Accuracy/AUC) gần bằng việc huấn luyện trên toàn bộ dữ liệu gốc.

## 1. Cấu trúc Dự án (Pipeline Architecture)

Dự án được chia thành 3 giai đoạn (Trạm) hoạt động tuyến tính và hoàn toàn độc lập với nhau:

*   **`src/data/` (Data Station):** 
    *   *Nhiệm vụ:* Đọc file CSV gốc, làm sạch, tách chương (chapter splitting), chuyển mã (Label Encoding), và xử lý khoảng trống.
    *   *Chống rò rỉ (Data Leakage):* Loại bỏ triệt để các cột ID (như `user_id`, `course_id`) để tránh mô hình học vẹt. Xóa nhãn (masking) đối với các Phase test không hợp lệ.
    *   *Đầu ra:* Các file ma trận numpy `.npy` siêu nhẹ, sẵn sàng cho Giai đoạn 2.
*   **`src/coreset/` (Coreset Factory):** 
    *   *Nhiệm vụ:* Nén dữ liệu. Đọc các file `.npy` và áp dụng 15+ thuật toán State-Of-The-Art (Random, CRAIG, SVP, CoreTab, TabKDE...) để trích xuất ra một tập con (Subset).
    *   *Tối ưu:* Hỗ trợ cắt lát (List Slicing) giúp tăng tốc x4 lần. Có cơ chế bắt lỗi tràn RAM (OOM) tự động để không làm sập tiến trình.
    *   *Đầu ra:* Các file `.csv` đã được nén theo nhiều mức Budget (vd: 10%, 20%) lưu trong thư mục `coresets/`.
*   **`src/training/` (Training Arena):** 
    *   *Nhiệm vụ:* Đấu trường huấn luyện. Load các tập dữ liệu đã nén, đưa vào các mô hình Machine Learning (XGBoost, Random Forest, SVM...) và Deep Learning (MLP, TabNet).
    *   *Đánh giá:* Tính toán hơn 20+ chỉ số học thuật (F1 Macro, Weighted, G-Mean, MCC, Per-Class Precision...).
    *   *Đầu ra:* Xuất kết quả đo lường ra file `.json` thô và lưu trữ mô hình `.pkl` (Checkpoint) để tái sử dụng mà không cần train lại.

## 2. Hướng dẫn Chạy trên Kaggle

Vì dữ liệu nguyên bản và dữ liệu nén có dung lượng khổng lồ, chúng ta **KHÔNG** lưu Data trên GitHub. Data sẽ được đặt ở một Kaggle Dataset độc lập. Code sẽ được kéo thẳng từ GitHub về Kaggle để thực thi.

### Bước 1: Khởi tạo trên Kaggle
Tạo một Kaggle Notebook mới. Nhấn "Add Data" và gắn Kaggle Dataset chứa các file CSV của bạn vào. Ở Cell đầu tiên của Notebook, chạy đoạn mã sau để kéo Code từ GitHub về:

```bash
# Thay URL bên dưới bằng Link GitHub Repository thực tế của bạn
!git clone https://github.com/UIT23521830/KLTN-Coreset.git
%cd KLTN-Coreset
```

### Bước 2: Cập nhật Code Nhanh (Sync)
Nếu bạn có chỉnh sửa file Python trên máy tính cá nhân và Push lên GitHub, bạn không cần phải tải file Zip lên Kaggle nữa. Chỉ cần chạy Cell này:
```bash
!git pull origin main
```
Toàn bộ code mới nhất sẽ được cập nhật trong 1 giây.

### Bước 3: Chạy Toàn Bộ Quy Trình (Execution)
Kích hoạt lần lượt 3 trạm xử lý:

```bash
# 1. Tiền xử lý dữ liệu thô (Raw -> .npy)
!python -m src.data.process_course

# 2. Ép nén dữ liệu qua 15 thuật toán (tốn nhiều thời gian nhất)
!python -m src.coreset.factory

# 3. Huấn luyện các mô hình ML/DL và chấm điểm 20 metrics
!python -m src.training.train_arena
```

File kết quả thô sẽ nằm trong thư mục `results/raw_metrics/`. Mô hình đã train sẽ nằm ở `results/checkpoints/`.
