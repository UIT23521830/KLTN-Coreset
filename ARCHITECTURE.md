# Tabular Coreset


---

## 1. DATA STORAGE


```text
C:\KLTN\paper\
│
├── 📂 datasets/                   <-- Kho Nguyên Liệu Thô (Raw)
│   ├── CourseQuality/             <-- File CSV gốc tải về từ nguồn
│   ├── Adult/
│   └── CreditCard/
│
├── 📂 processed/                  <-- Kho Thành Phẩm (Đã làm sạch bởi Data Station)
│   ├── CourseQuality/
│   │   ├── *.npy                  <-- Định dạng NumPy: Tốc độ siêu nhanh dành cho Python/PyTorch
│   │   ├── *.csv                  <-- Định dạng CSV: Sạch sẽ, dành riêng cho các C++ repo (như RECON)
│   │   ├── encoders.pkl           <-- Lưu lại "Ký ức" bộ giải mã (LabelEncoder)
│   │   └── metadata.json          <-- Tóm tắt thông tin dataset (số cột, class...)
│   └── ...
│
├── 📂 coresets/                   <-- Kho Dữ liệu Nén (Kết quả Giai đoạn 2)
│   ├── CoreTab/                   <-- Được chia theo từng Phương pháp Nén
│   ├── RECON/
│   └── CRAIG/
│
└── 📂 results/                    <-- Kho Báo cáo & Đánh giá (Giai đoạn 3 & 4)
    ├── raw_metrics/               <-- File .json chứa kết quả thô của từng mô hình
    └── figures/                   <-- Ảnh biểu đồ xuất ra cho báo cáo
```

---

## 2. SOURCE CODE


```text
C:\KLTN\paper\
│
├── 📂 src/
│   │
│   ├── 📂 data/                   <-- Trạm Xử Lý (Giai đoạn 1)
│   │   ├── __init__.py
│   │   ├── station_core.py        <-- Các hàm xuất chung (.npy và .csv)
│   │   ├── process_course.py      <-- Luật xử lý riêng chống rò rỉ cho CourseQuality
│   │   └── process_adult.py
│   │
│   ├── 📂 coreset/                <-- Nhà Máy Nén (Giai đoạn 2)
│   │   ├── __init__.py
│   │   └── coreset_factory.py     <-- Pipeline sinh coreset từ /processed/
│   │
│   ├── 📂 training/               <-- Huấn Luyện (Giai đoạn 3 & 4)
│   │   ├── __init__.py
│   │   └── train_arena.py         <-- Đọc dữ liệu từ /coresets/, huấn luyện ML và đánh giá
│   │
│   └── 📂 utils/                  <-- Công cụ phụ trợ
│       └── config.py              <-- Chứa thiết lập chung (Hyperparameters, Paths...)
│
├── 📂 analysis/                   <-- [Nháp] Code phân tích độc lập để khám phá dữ liệu
│   ├── baseline_cells.py
│   └── label_analysis.py
│
├── 📋 Plan.xlsx                   <-- Bảng khảo sát đánh giá 15 phương pháp SOTA
└── 📄 README.md                   <-- Giới thiệu dự án, cách setup môi trường
```

---

## 3. LUỒNG DỮ LIỆU (DATA FLOW)

Toàn bộ hệ thống chạy theo một chiều tuyến tính (Pipeline) nghiêm ngặt:

1.  **Giai đoạn 1 (Data Station):** Đọc CSV từ `datasets/` ➔ Tiền xử lý ➔ Xuất ra `.npy` & `.csv` vào `processed/`.
2.  **Giai đoạn 2 (Coreset Factory):** Đọc file chuẩn từ `processed/` ➔ Chạy thuật toán nén (CRAIG, RECON...) ➔ Xuất file CSV nén vào `coresets/`.
3.  **Giai đoạn 3 (Training Arena):** Đọc file nén từ `coresets/` ➔ Cho mô hình (XGBoost/RandomForest) học ➔ Tính toán F1, AUC, Time ➔ Đẩy kết quả vào `results/`.
