# KLTN - Tabular Coreset Selection Benchmark

Đây là mã nguồn hệ thống thử nghiệm nén dữ liệu dạng bảng (Tabular Dataset Condensation/Coresets) cho Khóa Luận Tốt Nghiệp.

## 1. Cấu trúc Dự án
- `src/data/`: Data Station (Làm sạch, chuẩn hóa, chống Data Leakage).
- `src/coreset/`: Coreset Factory (Tích hợp 15+ thuật toán nén như CRAIG, SVP, CoreTab, TabKDE...).
- `src/training/`: Training Arena (Huấn luyện các mô hình ML truyền thống và DL như TabNet, MLP trên dữ liệu nén, đồng thời xuất kết quả 20+ metrics).

## 2. Cách chạy trên Kaggle
Dữ liệu rất lớn nên sẽ KHÔNG được lưu trên GitHub. 
Toàn bộ dữ liệu nằm trên một Kaggle Dataset.

### Bước 1: Setup trên Kaggle
Tạo một Kaggle Notebook mới và thêm Dataset dữ liệu của dự án vào. Ở Cell đầu tiên, chạy lệnh sau để đồng bộ toàn bộ Code mới nhất từ GitHub về:

```bash
!git clone https://github.com/hoangzy/Ten-Repo-Cua-Ban.git
%cd Ten-Repo-Cua-Ban
```
*(Lưu ý: Bạn cần tạo Repo GitHub và sửa lại URL ở trên)*

### Bước 2: Cập nhật Code (Sync)
Mỗi khi bạn sửa code ở máy tính local và Push lên GitHub, chỉ cần quay lại Kaggle và chạy:
```bash
!git pull
```
Hệ thống Kaggle sẽ ngay lập tức có được Code mới nhất mà không cần Zip/Upload lại!

### Bước 3: Chạy Pipeline
```bash
# Chạy nén dữ liệu
!python -m src.coreset.factory

# Chạy huấn luyện và đánh giá
!python -m src.training.train_arena
```
