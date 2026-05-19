import pandas as pd
from openpyxl.styles import Alignment

file_path = r'C:\KLTN\paper\Reference.xlsx'
csv_path = r'C:\KLTN\paper\SOTA_Verified_List.csv'

# Dữ liệu 15 bài báo (Đã thay máu hoàn toàn, 100% Khớp yêu cầu)
data = [
    {
        "STT": 1, "Trường Phái (Độ Phủ)": "Trục 1: Đặc trị Tabular",
        "Đề tài / Công bố khoa học": "CoreTab: Coreset-based Data-efficient Machine Learning over Tabular Data",
        "Năm": 2024, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Phương pháp cốt lõi (Base Paper).",
        "Mã nguồn (GitHub/Library)": "https://github.com/avivhadar33/coretab",
        "Ưu điểm & Nhược điểm": "- Ưu: Nén trên đa lớp, đặc trị bảng kết hợp Datamap.\n- Nhược: Cần huấn luyện bộ Tree Proxy."
    },
    {
        "STT": 2, "Trường Phái (Độ Phủ)": "Trục 1: Đặc trị Tabular",
        "Đề tài / Công bố khoa học": "RECON: Efficient Coreset Selection for Multi-Table Machine Learning",
        "Năm": 2024, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Phủ trường hợp nén Đa bảng (Multi-table).",
        "Mã nguồn (GitHub/Library)": "https://github.com/jiayi-wang/recon",
        "Ưu điểm & Nhược điểm": "- Ưu: Lấy mẫu không cần Join vật lý.\n- Nhược: Cần tiếp cận sâu vào CSDL."
    },
    {
        "STT": 3, "Trường Phái (Độ Phủ)": "Trục 1: Đặc trị Tabular",
        "Đề tài / Công bố khoa học": "GoodCore: Coreset Selection over Incomplete Data",
        "Năm": 2023, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Phủ trường hợp dữ liệu bảng bị thiếu (NaN).",
        "Mã nguồn (GitHub/Library)": "https://github.com/megagonlabs/goodcore",
        "Ưu điểm & Nhược điểm": "- Ưu: Xử lý giá trị mờ rất tốt.\n- Nhược: Tính toán 'Possible Worlds' chậm."
    },
    {
        "STT": 4, "Trường Phái (Độ Phủ)": "Trục 2: Đạo hàm (Đấu cấu trúc CoreTab)",
        "Đề tài / Công bố khoa học": "CRAIG: Coresets for Accelerating Incremental Gradient Descent",
        "Năm": 2020, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Bản lề số 5 mà tác giả CoreTab dùng đối chiếu.",
        "Mã nguồn (GitHub/Library)": "Thư viện CORDS (decile-team/distil)",
        "Ưu điểm & Nhược điểm": "- Ưu: Khớp đạo hàm tốc độ cao.\n- Nhược: Tốn bộ nhớ sinh ma trận khoảng cách."
    },
    {
        "STT": 5, "Trường Phái (Độ Phủ)": "Trục 2: Đạo hàm (Đấu cấu trúc CoreTab)",
        "Đề tài / Công bố khoa học": "GradMatch: Adaptive Gradient Matching",
        "Năm": 2021, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Cải tiến đạo hàm (SOTA hơn CRAIG).",
        "Mã nguồn (GitHub/Library)": "Thư viện CORDS (decile-team/distil)",
        "Ưu điểm & Nhược điểm": "- Ưu: Bám sát tập validation.\n- Nhược: Chạy thuật toán OMP phức tạp."
    },
    {
        "STT": 6, "Trường Phái (Độ Phủ)": "Trục 2: Đạo hàm (Đấu cấu trúc CoreTab)",
        "Đề tài / Công bố khoa học": "GLISTER: Generalization based Subset Selection",
        "Năm": 2021, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Siêu việt chống nhiễu loạn nhãn (Label Noise).",
        "Mã nguồn (GitHub/Library)": "Thư viện CORDS (decile-team/glister)",
        "Ưu điểm & Nhược điểm": "- Ưu: Kháng nhiễu ngoại lai.\n- Nhược: Tối ưu 2 cấp (Bi-level) làm chậm Tốc độ."
    },
    {
        "STT": 7, "Trường Phái (Độ Phủ)": "Trục 3: Động lực học",
        "Đề tài / Công bố khoa học": "Dataset Cartography: Mapping and Diagnosing Datasets",
        "Năm": 2020, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Tổ tiên của CoreTab (Dùng Data Maps đo Confidence).",
        "Mã nguồn (GitHub/Library)": "https://github.com/allenai/cartography",
        "Ưu điểm & Nhược điểm": "- Ưu: Chẩn đoán mẫu dễ/khó.\n- Nhược: Cần lưu Log nhiều mạng huấn luyện."
    },
    {
        "STT": 8, "Trường Phái (Độ Phủ)": "Trục 3: Động lực học",
        "Đề tài / Công bố khoa học": "An Empirical Study of Example Forgetting",
        "Năm": 2019, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Trụ cột nền tảng đánh giá học máy (Ngoại lệ trước 2020).",
        "Mã nguồn (GitHub/Library)": "Thư viện DeepCore",
        "Ưu điểm & Nhược điểm": "- Ưu: Trực quan.\n- Nhược: Tốn kém tính toán ban đầu."
    },
    {
        "STT": 9, "Trường Phái (Độ Phủ)": "Trục 3: Động lực học",
        "Đề tài / Công bố khoa học": "Deep Learning on a Data Diet (GraNd / EL2N)",
        "Năm": 2021, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Chấm điểm L2 để giữ lại các dòng Error lớn.",
        "Mã nguồn (GitHub/Library)": "Thư viện DeepCore",
        "Ưu điểm & Nhược điểm": "- Ưu: Rất phù hợp với dữ liệu Tabular định lượng.\n- Nhược: Cần mồi huấn luyện epoch đầu."
    },
    {
        "STT": 10, "Trường Phái (Độ Phủ)": "Trục 4: Hình Học (Thay IS-CLUS của CoreTab)",
        "Đề tài / Công bố khoa học": "SubStrat: Optimization Strategy for Faster AutoML",
        "Năm": 2022, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Đối chiếu bản lề 6 mà tác giả CoreTab dùng (Thuật toán Di Truyền).",
        "Mã nguồn (GitHub/Library)": "https://github.com/vl2/substrat",
        "Ưu điểm & Nhược điểm": "- Ưu: Được CoreTab chứng nhận áp dụng Tabular.\n- Nhược: Tìm kiếm lời giải lâu."
    },
    {
        "STT": 11, "Trường Phái (Độ Phủ)": "Trục 4: Hình Học (Thay IS-CLUS của CoreTab)",
        "Đề tài / Công bố khoa học": "Moderate Coreset: A Universal Method of Data Selection",
        "Năm": 2023, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Phủ cụm Hình Học, chọn dòng trung vị (Sáng tạo hơn KNN/KMeans cũ).",
        "Mã nguồn (GitHub/Library)": "https://github.com/tmllab/Moderate-DS",
        "Ưu điểm & Nhược điểm": "- Ưu: Không bị cuốn vào Outliers như các thuật toán hình học khác."
    },
    {
        "STT": 12, "Trường Phái (Độ Phủ)": "Trục 4: Hình Học (Thay IS-CLUS của CoreTab)",
        "Đề tài / Công bố khoa học": "Active Learning for CNNs (K-Center Greedy)",
        "Năm": 2018, "Loại Nén": "Chọn dòng (Geometry)",
        "Định hướng So Sánh": "SOTA Hình học nền tảng bắt buộc phải có.",
        "Mã nguồn (GitHub/Library)": "Thư viện DeepCore / Scikit-learn",
        "Ưu điểm & Nhược điểm": "- Ưu: Đảm bảo độ đa dạng không gian dòng.\n- Nhược: Cũ (2018)."
    },
    {
        "STT": 13, "Trường Phái (Độ Phủ)": "Trục 5: Sinh Tín Hiệu Nén Đột Phá",
        "Đề tài / Công bố khoa học": "Dataset Condensation with Gradient Matching",
        "Năm": 2021, "Loại Nén": "Sinh dòng ảo (Condensation)",
        "Định hướng So Sánh": "Dùng thay thế VAE (Baseline số 4 của CoreTab). Đỉnh cao của Dữ liệu ảo.",
        "Mã nguồn (GitHub/Library)": "https://github.com/VICO-UoE/DatasetCondensation",
        "Ưu điểm & Nhược điểm": "- Ưu: Kích thước siêu nhỏ.\n- Nhược: Biến dạng kiểu dữ liệu gốc Categorical."
    },
    {
        "STT": 14, "Trường Phái (Độ Phủ)": "Trục 5: Sinh Tín Hiệu Nén Đột Phá",
        "Đề tài / Công bố khoa học": "Selection via Proxy (SVP)",
        "Năm": 2020, "Loại Nén": "Chọn dòng (Coreset)",
        "Định hướng So Sánh": "Phủ trường phái dùng Mô hình con học hộ mô hình cha.",
        "Mã nguồn (GitHub/Library)": "https://github.com/stanford-futuredata/selection-via-proxy",
        "Ưu điểm & Nhược điểm": "- Ưu: Tăng tốc tính toán nghìn lần.\n- Nhược: Lệ thuộc Proxy."
    },
    {
        "STT": 15, "Trường Phái (Độ Phủ)": "Trục 5: Sinh Tín Hiệu Nén Đột Phá",
        "Đề tài / Công bố khoa học": "InfoBatch: Lossless Training Speed Up by Dynamic Data Pruning",
        "Năm": 2024, "Loại Nén": "Pruning Động",
        "Định hướng So Sánh": "Phương pháp Tabular / Multi siêu mới nén thời gian thực.",
        "Mã nguồn (GitHub/Library)": "https://github.com/NUS-HPC-AI-Lab/InfoBatch",
        "Ưu điểm & Nhược điểm": "- Ưu: SOTA 2024, không làm rớt Accuracy.\n- Nhược: Phải nén trong lúc chạy (Dynamic)."
    }
]

df = pd.DataFrame(data)

# 1. Ghi ra CSV (Để bạn view nhanh)
df.to_csv(csv_path, index=False, encoding='utf-8-sig')

# 2. Ghi ra Excel làm vũ khí chính thức
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Final_SOTA_15')
    ws = writer.sheets['Final_SOTA_15']
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical='top', horizontal='left')
    
    # Định dạng chiều rộng cột cho đẹp
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 50
    ws.column_dimensions['F'].width = 50
    ws.column_dimensions['G'].width = 30
    ws.column_dimensions['H'].width = 50

print("Đã tổng hợp đanh sách SOTA Hoàn Mỹ vào cả CSV và Excel.")
