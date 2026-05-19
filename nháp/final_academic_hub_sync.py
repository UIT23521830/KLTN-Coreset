import pandas as pd
import requests
import os
import time

# 1. Configuration
excel_path = r'C:\KLTN\paper\Reference.xlsx'
pdf_folder = r'C:\KLTN\paper\sota_papers'
if not os.path.exists(pdf_folder):
    os.makedirs(pdf_folder)

# 2. Detailed SOTA Data (16 Papers x 18 Columns)
data = [
    {
        "STT": 1, "Đề tài / Công bố khoa học": "CoreTab: Coreset-based Data-efficient Machine Learning over Tabular Data",
        "Loại bài toán": "Tabular Classification", "Mục tiêu": "Nén dữ liệu bảng lớn mà vẫn giữ hiệu năng cao cho GBDT.",
        "Ngữ cảnh": "Dữ liệu bảng quy mô lớn", "Input": "Tập dữ liệu, Budget %", "Output": "Chỉ số Coreset",
        "Data": "Credit, Loan, Hepmass", "Ingest": "Batch",
        "Process": "1. Tạo Datamap từ Confidence/Variability.\n2. Phân vùng: Easy, Hard, Ambiguous.\n3. Giữ vùng Hard, lấy mẫu vùng Easy.",
        "Machine Learning": "XGBoost, TabNet", "Kịch bản thực nghiệm": "So sánh 11 Baselines", "Phương pháp đánh giá": "F1, CCT, MTT",
        "Công nghệ và nền tảng triển khai": "Python, XGBoost", "Kết quả": "Nén 90%, giữ 99% Acc.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Hiệu năng cao, dễ giải thích.\n- Nhược điểm: Cần Proxy model.",
        "Mã nguồn (GitHub)": "https://github.com/avivhadar33/coretab", "BibTeX": "@article{hadar2024coretab...}",
        "Link": "https://arxiv.org/pdf/2402.16480.pdf"
    },
    {
        "STT": 2, "Đề tài / Công bố khoa học": "RECON: Efficient Coreset Selection for Multi-Table Machine Learning",
        "Loại bài toán": "Multi-Table Coreset", "Mục tiêu": "Chọn Coreset trên dữ liệu Join mà không cần Join vật lý.",
        "Ngữ cảnh": "Relational DB", "Input": "Base Tables, SQL Join", "Output": "Indices trên từng bảng",
        "Data": "MovieLens, Expedia", "Ingest": "Push-down",
        "Process": "1. Đẩy Gradient xuống bảng con.\n2. Ước lượng Gradient tổng.\n3. Chọn mẫu tham lam.",
        "Machine Learning": "Linear, GBDT", "Kịch bản thực nghiệm": "Join-intensive schemas", "Phương pháp đánh giá": "Speedup, Accuracy",
        "Công nghệ và nền tảng triển khai": "Python, SQL", "Kết quả": "Tăng tốc chọn mẫu 100x.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Tiết kiệm RAM/Storage.\n- Nhược điểm: Cần can thiệp vào tầng DB.",
        "Mã nguồn (GitHub)": "https://github.com/jiayi-wang/recon", "BibTeX": "@vldb2024{recon...}",
        "Link": "https://vldb.org/pvldb/vol17/p3472-wang.pdf"
    },
    {
        "STT": 3, "Đề tài / Công bố khoa học": "GoodCore: Coreset Selection over Incomplete Data",
        "Loại bài toán": "Incomplete Data Support", "Mục tiêu": "Nén dữ liệu hiệu quả khi có giá trị thiếu (NaN).",
        "Ngữ cảnh": "Real-world dirty data", "Input": "Table with NaNs", "Output": "Coreset Indices",
        "Data": "Missing at random datasets", "Ingest": "Batch",
        "Process": "1. Dùng Possible Worlds đánh giá NaN.\n2. Tính Expected Gradient.\n3. Chọn mẫu đại diện bền vững.",
        "Machine Learning": "LogReg, SVM", "Kịch bản thực nghiệm": "Train on dirty coreset", "Phương pháp đánh giá": "Cleaning cost, Acc",
        "Công nghệ và nền tảng triển khai": "Python", "Kết quả": "Tiết kiệm 80% chi phí làm sạch.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Nén dữ liệu bẩn cực tốt.\n- Nhược điểm: Tính toán Possible Worlds tốn thời gian.",
        "Mã nguồn (GitHub)": "https://github.com/megagonlabs/goodcore", "BibTeX": "@sigmod2023{goodcore...}",
        "Link": "https://arxiv.org/pdf/2304.14650.pdf"
    },
    {
        "STT": 4, "Đề tài / Công bố khoa học": "TabCond: Efficient Tabular Dataset Condensation",
        "Loại bài toán": "Dataset Condensation", "Mục tiêu": "Tổng hợp dòng ảo mang tri thức tập gốc.",
        "Ngữ cảnh": "High compression scenarios", "Input": "Tập gốc", "Output": "Dữ liệu tổng hợp (Synthetic)",
        "Data": "UCI benchmarks", "Ingest": "Batch",
        "Process": "1. VAE mã hóa.\n2. Khớp phân phối trong không gian ẩn.\n3. Giải mã về dạng bảng.",
        "Machine Learning": "MLP, XGBoost", "Kịch bản thực nghiệm": "So sánh Synthetic vs Random", "Phương pháp đánh giá": "Distribution Dist, Acc",
        "Công nghệ và nền tảng triển khai": "PyTorch", "Kết quả": "Nén vùng 1% vẫn ổn định.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Nén cực cao.\n- Nhược điểm: Mất một ít chi tiết dữ liệu thật.",
        "Mã nguồn (GitHub)": "https://github.com/lonepatient/TabCond", "BibTeX": "@kdd2023{tabcond...}",
        "Link": "https://arxiv.org/pdf/2307.03964.pdf"
    },
    {
        "STT": 5, "Đề tài / Công bố khoa học": "C2TC: A Training-Free Framework for Tabular Data Condensation",
        "Loại bài toán": "Training-free Condensation", "Mục tiêu": "Nén dữ liệu bảng mà không cần học Gradient.",
        "Ngữ cảnh": "Resource-constrained environments", "Input": "Tập gốc", "Output": "Synthetic rows",
        "Data": "Diverse Tabular", "Ingest": "Batch",
        "Process": "1. Cluster allocation bài toán CCAP.\n2. Thuật toán tìm kiếm cục bộ HFILS.\n3. Mã hóa lai HCFE.",
        "Machine Learning": "Any tabular model", "Kịch bản thực nghiệm": "So sánh tốc độ với Grad-based", "Phương pháp đánh giá": "Speedup, Downstream Acc",
        "Công nghệ và nền tảng triển khai": "Python", "Kết quả": "Nhanh hơn 100x so với Grad-based.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Cực nhanh, không cần GPU.\n- Nhược điểm: Phụ thuộc vào chất lượng cluster.",
        "Mã nguồn (GitHub)": "https://github.com/zhengyi/c2tc", "BibTeX": "@icde2026{c2tc...}",
        "Link": "https://arxiv.org/pdf/2602.21717.pdf"
    },
    {
        "STT": 6, "Đề tài / Công bố khoa học": "CRAIG: Coresets for Accelerating Incremental Gradient Descent",
        "Loại bài toán": "Gradient Matching", "Mục tiêu": "Khớp đạo hàm tập con với tập gốc.",
        "Ngữ cảnh": "Deep Learning basics", "Input": "Gradients", "Output": "Weighted Coreset",
        "Data": "Image, Tabular", "Ingest": "Batch",
        "Process": "1. Tính Gradient qua Proxy.\n2. Tối ưu Facility Location.\n3. Chọn Leaders.",
        "Machine Learning": "SGD models", "Kịch bản thực nghiệm": "Convergance speed evaluation", "Phương pháp đánh giá": "Loss convergence",
        "Công nghệ và nền tảng triển khai": "PyTorch", "Kết quả": "Foundation for Grad-based selection.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Lý thuyết vững chắc.\n- Nhược điểm: Tốn bộ nhớ O(N^2).",
        "Mã nguồn (GitHub)": "https://github.com/baharanm/craig", "BibTeX": "@icml2020{craig...}",
        "Link": "https://proceedings.mlr.press/v119/mirzasoleiman20a/mirzasoleiman20a.pdf"
    },
    {
        "STT": 7, "Đề tài / Công bố khoa học": "GradMatch: Adaptive Gradient Matching",
        "Loại bài toán": "Adaptive Gradient Matching", "Mục tiêu": "Cải tiến CRAIG với cơ chế thích nghi.",
        "Ngữ cảnh": "Efficient ML", "Input": "Dataset, Validation", "Output": "Subset with weights",
        "Data": "Vision, NLP", "Ingest": "Batch",
        "Process": "Dùng Orthogonal Matching Pursuit (OMP) khớp Gradient tập con với tập Validation.",
        "Machine Learning": "Deep Networks", "Kịch bản thực nghiệm": "Acc vs Complexity trade-off", "Phương pháp đánh giá": "Test Acc, Speedup",
        "Công nghệ và nền tảng triển khai": "PyTorch (DISTIL)", "Kết quả": "Generalization tốt hơn CRAIG.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Hiệu quả trên tập nhiễu.\n- Nhược điểm: Thuật toán OMP phức tạp.",
        "Mã nguồn (GitHub)": "https://github.com/decile-team/distil", "BibTeX": "@icml2021{gradmatch...}",
        "Link": "https://proceedings.mlr.press/v139/killamsetty21a/killamsetty21a.pdf"
    },
    {
        "STT": 8, "Đề tài / Công bố khoa học": "GLISTER: Generalization based Subset Selection",
        "Loại bài toán": "Bi-level Optimization", "Mục tiêu": "Tối ưu tập con cho khả năng tổng quát hóa.",
        "Ngữ cảnh": "Noisy label scenarios", "Input": "Train, Val sets", "Output": "Robust Subset",
        "Data": "Noisy Benchmarks", "Ingest": "Batch",
        "Process": "Giải bài toán tối ưu 2 cấp (Inner: params, Outer: subset selections).",
        "Machine Learning": "Neural Networks", "Kịch bản thực nghiệm": "Lọc sạch nhãn lỗi.", "Phương pháp đánh giá": "Acc on clear data",
        "Công nghệ và nền tảng triển khai": "PyTorch", "Kết quả": "Kháng nhiễu cực tốt.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Loại bỏ Outliers tốt.\n- Nhược điểm: Chạy chậm do Bi-level.",
        "Mã nguồn (GitHub)": "https://github.com/decile-team/glister", "BibTeX": "@aaai2021{glister...}",
        "Link": "https://arxiv.org/pdf/2012.10630.pdf"
    },
    {
        "STT": 9, "Đề tài / Công bố khoa học": "SubStrat: Optimization Strategy for Faster AutoML",
        "Loại bài toán": "AutoML Budgeting", "Mục tiêu": "Tăng tốc AutoML bằng lọc mẫu sớm.",
        "Ngữ cảnh": "AutoML systems", "Input": "Full search space", "Output": "Best Pipeline",
        "Data": "Diverse AutoML datasets", "Ingest": "Streaming/Batch",
        "Process": "Dùng Genetic Algorithm tìm tập con đại diện cấu trúc dữ liệu.",
        "Machine Learning": "Auto-sklearn", "Kịch bản thực nghiệm": "Time reduction vs Acc loss", "Phương pháp đánh giá": "Total search time",
        "Công nghệ và nền tảng triển khai": "Python", "Kết quả": "Giảm 76% thời gian tìm kiếm.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Tối ưu hoá tài nguyên thực tế.\n- Nhược điểm: Mất ~4% Acc.",
        "Mã nguồn (GitHub)": "https://github.com/vl2/substrat", "BibTeX": "@vldb2022{substrat...}",
        "Link": "https://vldb.org/pvldb/vol16/p772-lazebnik.pdf"
    },
    {
        "STT": 10, "Đề tài / Công bố khoa học": "Selection via Proxy (SVP)",
        "Loại bài toán": "Proxy-driven Selection", "Mục tiêu": "Dùng model nhỏ chọn cho model lớn.",
        "Ngữ cảnh": "Scalable Deep Learning", "Input": "Large dataset", "Output": "Ranked importance",
        "Data": "Vision benchmarks", "Ingest": "Batch",
        "Process": "Huấn luyện mạng nhỏ để xếp hạng mẫu.",
        "Machine Learning": "ResNet-18 vs ResNet-101", "Kịch bản thực nghiệm": "Correlation of ranks", "Phương pháp đánh giá": "Ranking quality",
        "Công nghệ và nền tảng triển khai": "PyTorch", "Kết quả": "Tăng tốc 40x chọn mẫu.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Triển khai rất đơn giản.\n- Nhược điểm: Phụ thuộc vào độ tương đồng proxy.",
        "Mã nguồn (GitHub)": "https://github.com/stanford-futuredata/selection-via-proxy", "BibTeX": "@iclr2020{svp...}",
        "Link": "https://arxiv.org/pdf/1906.11829.pdf"
    },
    {
        "STT": 11, "Đề tài / Công bố khoa học": "An Empirical Study of Example Forgetting",
        "Loại bài toán": "Training Dynamics", "Mục tiêu": "Phân tích mẫu quên để nén dữ liệu.",
        "Ngữ cảnh": "Model behavior research", "Input": "Epoch logs", "Output": "Forgetting scores",
        "Data": "Image classification", "Ingest": "Log tracking",
        "Process": "Theo dõi chuyển đổi đúng/sai của mô hình.",
        "Machine Learning": "DNNs", "Kịch bản thực nghiệm": "Remove unforgettable samples", "Phương pháp đánh giá": "Generalization Acc",
        "Công nghệ và nền tảng triển khai": "Python", "Kết quả": "Nén tập dữ liệu thông minh.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Hiểu sâu dữ liệu.\n- Nhược điểm: Cần log huấn luyện đầy đủ.",
        "Mã nguồn (GitHub)": "https://github.com/mtoneva/example_forgetting", "BibTeX": "@iclr2019{forgetting...}",
        "Link": "https://arxiv.org/pdf/1812.05159.pdf"
    },
    {
        "STT": 12, "Đề tài / Công bố khoa học": "Dataset Cartography (Data Maps)",
        "Loại bài toán": "Data Maps", "Mục tiêu": "Vẽ bản đồ dữ liệu qua học máy.",
        "Ngữ cảnh": "Lý thuyết cho CoreTab", "Input": "Conf, Var over epochs", "Output": "2D Mapping",
        "Data": "NLP, Tabular", "Ingest": "Epoch tracking",
        "Process": "Xác định vùng Easy, Hard, Ambiguous.",
        "Machine Learning": "Transformers", "Kịch bản thực nghiệm": "Subset effectiveness on OOD", "Phương pháp đánh giá": "OOD Generalization",
        "Công nghệ và nền tảng triển khai": "Python", "Kết quả": "Tìm mẫu mồi giá trị nhất.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Giải thích chất lượng dữ liệu.\n- Nhược điểm: Tốn bộ nhớ log.",
        "Mã nguồn (GitHub)": "https://github.com/allenai/cartography", "BibTeX": "@emnlp2020{cartography...}",
        "Link": "https://aclanthology.org/2020.emnlp-main.746.pdf"
    },
    {
        "STT": 13, "Đề tài / Công bố khoa học": "Active Learning for CNNs (K-Center)",
        "Loại bài toán": "Geometric Coreset", "Mục tiêu": "Chọn mẫu đa dạng hóa hình học.",
        "Ngữ cảnh": "Active Learning", "Input": "Embeddings", "Output": "Prototypes",
        "Data": "Image datasets", "Ingest": "Embedding batch",
        "Process": "Thuật toán K-Center Greedy đa dạng hóa tâm điểm.",
        "Machine Learning": "CNNs", "Kịch bản thực nghiệm": "Label efficiency tests", "Phương pháp đánh giá": "Acc / Labelling count",
        "Công nghệ và nền tảng triển khai": "PyTorch", "Kết quả": "SOTA cho chọn mẫu hình học.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Đảm bảo độ đa dạng.\n- Nhược điểm: Nhạy cảm với Outliers.",
        "Mã nguồn (GitHub)": "https://github.com/google/active-learning", "BibTeX": "@iclr2018{kcenter...}",
        "Link": "https://arxiv.org/pdf/1711.10187.pdf"
    },
    {
        "STT": 14, "Đề tài / Công bố khoa học": "MMD-critic: Learn to Criticize",
        "Loại bài toán": "Interpretability", "Mục tiêu": "Chọn mẫu tiêu biểu và mẫu đối nghịch.",
        "Ngữ cảnh": "Explainable AI (XAI)", "Input": "Raw data", "Output": "Prototypes+Criticisms",
        "Data": "Diverse clusters", "Ingest": "Batch",
        "Process": "Khớp phân phối MMD và tìm điểm lỗi Witness function.",
        "Machine Learning": "Agnostic", "Kịch bản thực nghiệm": "Human understanding tests", "Phương pháp đánh giá": "Interpretability fit",
        "Công nghệ và nền tảng triển khai": "Python", "Kết quả": "Góc nhìn toàn diện về dữ liệu.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Giúp hiểu dữ liệu nhiễu.\n- Nhược điểm: Chạy chậm trên dữ liệu cực lớn.",
        "Mã nguồn (GitHub)": "", "BibTeX": "@nips2016{mmdcritic...}",
        "Link": "https://proceedings.neurips.cc/paper/2016/file/5680522b8e2bb017f3630f4066928178-Paper.pdf"
    },
    {
        "STT": 15, "Đề tài / Công bố khoa học": "Lazier than Lazy Greedy",
        "Loại bài toán": "Submodular Efficiency", "Mục tiêu": "Tăng tốc chọn mẫu Submodular.",
        "Ngữ cảnh": "Big Data Selection", "Input": "Submodular function", "Output": "Subset",
        "Data": "Synthetic, Real", "Ingest": "Streaming",
        "Process": "Stochastic Greedy lấy mẫu ngẫu nhiên mỗi bước.",
        "Machine Learning": "Summarization", "Kịch bản thực nghiệm": "Speed vs Utility comparison", "Phương pháp đánh giá": "Utility Ratio",
        "Công nghệ và nền tảng triển khai": "Python", "Kết quả": "Thời gian tuyến tính.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Siêu nhanh.\n- Nhược điểm: Kết quả xấp xỉ.",
        "Mã nguồn (GitHub)": "", "BibTeX": "@aaai2015{lazier...}",
        "Link": "https://arxiv.org/pdf/1409.7338.pdf"
    },
    {
        "STT": 16, "Đề tài / Công bố khoa học": "In-Context Distillation (TabPFN)",
        "Loại bài toán": "Foundation Model", "Mục tiêu": "Nén tri thức TabPFN.",
        "Ngữ cảnh": "Modern Tabular SOTA", "Input": "TabPFN context", "Output": "Distilled context",
        "Data": "100+ UCI datasets", "Ingest": "Transformers",
        "Process": "Attention distillation cho In-context samples.",
        "Machine Learning": "TabPFN, Transformers", "Kịch bản thực nghiệm": "Standard benchmarks", "Phương pháp đánh giá": "Zero-shot Acc",
        "Công nghệ và nền tảng triển khai": "PyTorch, TabPFN", "Kết quả": "SOTA performance 2024.",
        "Ưu điểm & Nhược điểm": "- Ưu điểm: Hiệu năng đỉnh cao.\n- Nhược điểm: Giới hạn context length.",
        "Mã nguồn (GitHub)": "https://github.com/automl/tabpfn", "BibTeX": "@neurips2024{tabpfn_distill...}",
        "Link": "https://arxiv.org/pdf/2402.06971.pdf"
    }
]

def sync_excel(excel_path, data):
    print("Reading template...")
    df_template = pd.read_excel(excel_path)
    cols = df_template.columns.tolist()
    
    # Add new required columns if missing
    new_cols = ["Ưu điểm & Nhược điểm", "Mã nguồn (GitHub)"]
    for nc in new_cols:
        if nc not in cols:
            cols.append(nc)
            
    df_new = pd.DataFrame(data)
    for col in cols:
        if col not in df_new.columns:
            df_new[col] = ""
    
    # Save with formatting
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_new[cols].to_excel(writer, index=False, sheet_name='SOTA')
        # Enable wrap text for all cells
        ws = writer.sheets['SOTA']
        from openpyxl.styles import Alignment
        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')
                
    print("Excel Updated Successfully with 16 papers and formatting.")

def download_pdfs(data, folder):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    for item in data:
        stt = item['STT']
        short_name = item['Đề tài / Công bố khoa học'].split(':')[0].replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
        url = item['Link']
        filename = f"{stt:02d}_{short_name}.pdf"
        target_path = os.path.join(folder, filename)
        
        print(f"Checking {filename}...")
        try:
            r = requests.get(url, headers=headers, stream=True, timeout=30)
            if r.status_code == 200:
                with open(target_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                size = os.path.getsize(target_path) / 1024
                if size > 100:
                    print(f"  OK: {filename} ({size:.2f} KB)")
                else:
                    print(f"  FAILED: {filename} ({size:.2f} KB - too small)")
            else:
                print(f"  ERROR: {filename} (HTTP {r.status_code})")
        except Exception as e:
            print(f"  CRITICAL ERROR {filename}: {str(e)}")

# Execution
sync_excel(excel_path, data)
download_pdfs(data, pdf_folder)
