import pandas as pd

file_path = 'C:/KLTN/paper/Reference.xlsx'

data = [
    {
        "STT": 1,
        "Đề tài / Công bố khoa học": "CoreTab: Coreset-based Data-efficient Machine Learning over Tabular Data",
        "Loại bài toán": "Tabular Classification / Subset Selection",
        "Mục tiêu": "Giải quyết vấn đề huấn luyện mô hình chậm trên tập dữ liệu bảng lớn bằng cách sử dụng GBDT tạo bản đồ dữ liệu (Datamap) để chọn tập con đại diện.",
        "Ngữ cảnh": "Dữ liệu bảng quy mô lớn",
        "Input": "Tập dữ liệu bảng, Ngân sách (Budget %)",
        "Output": "Tập Coreset (Tập con)",
        "Process": "1. Sử dụng GBDT (XGBoost/LightGBM) để tạo Datamap dựa trên độ tin cậy (Confidence) và biến động (Variability). 2. Phân chia dữ liệu thành 3 vùng: Dễ (Easy), Khó (Hard), và Mơ hồ (Ambiguous). 3. Giữ lại toàn bộ vùng Khó vì chứa thông tin quan trọng về biên quyết định. 4. Lấy mẫu đại diện cực nhỏ cho vùng Dễ.",
        "Machine Learning": "XGBoost, TabNet, LightGBM",
        "Kịch bản thực nghiệm": "So sánh với 11 Baselines trên 6 bộ dữ liệu chuẩn.",
        "Phương pháp đánh giá": "F1-score, thời gian nén (CCT), thời gian học (MTT)",
        "Kết quả": "Giảm 90% dữ liệu nhưng vẫn giữ được 99% độ chính xác. Nhanh hơn các phương pháp Gradient-based 10-100 lần.",
        "Link": "https://www.vldb.org/pvldb/vol18/p876-hadar.pdf"
    },
    {
        "STT": 2,
        "Đề tài / Công bố khoa học": "CRAIG: Coresets for Accelerating Incremental Gradient Descent",
        "Loại bài toán": "Gradient Matching / Coreset Selection",
        "Mục tiêu": "Chọn một tập con có trọng số sao cho tổng Gradient của nó xấp xỉ tốt nhất với Gradient của toàn bộ tập dữ liệu gốc.",
        "Ngữ cảnh": "Deep Learning / Đào tạo mô hình lớn",
        "Input": "Gradients của tập huấn luyện",
        "Output": "Tập mẫu có trọng số (Weighted Coreset)",
        "Process": "1. Tính toán Gradient cho từng mẫu dữ liệu thông qua một mô hình Proxy (thường là Logistic Regression). 2. Xây dựng ma trận tương đồng dựa trên khoảng cách Gradient. 3. Giải bài toán tối ưu hóa hàm Facility Location để chọn ra tập điểm đại diện (Leaders) khớp với đạo hàm tổng thể.",
        "Machine Learning": "SGD-based models, CNNs",
        "Kịch bản thực nghiệm": "Đánh giá tốc độ hội tụ và độ chính xác cuối cùng trên CIFAR, MNIST.",
        "Phương pháp đánh giá": "Training Loss, Test Accuracy",
        "Kết quả": "Tăng tốc huấn luyện đáng kể với chứng minh toán học về giới hạn sai số (Error bounds).",
        "Link": "https://proceedings.mlr.press/v119/mirzasoleiman20a.html"
    },
    {
        "STT": 3,
        "Đề tài / Công bố khoa học": "GradMatch: Gradient Matching based Data Subset Selection",
        "Loại bài toán": "Adaptive Gradient Matching",
        "Mục tiêu": "Cải thiện CRAIG bằng cách khớp đạo hàm một cách thích nghi, giúp tập con thích ứng tốt hơn với sự thay đổi của mô hình trong quá trình học.",
        "Ngữ cảnh": "Học máy hiệu quả (Data-Efficient Learning)",
        "Input": "Dữ liệu huấn luyện, Validation set",
        "Output": "Tập con tối ưu",
        "Process": "Sử dụng thuật toán Orthogonal Matching Pursuit (OMP) để chọn mẫu sao cho Gradient của tập con khớp nhất với Gradient của tập Validation hoặc tập gốc tại mỗi bước huấn luyện.",
        "Machine Learning": "Deep Neural Networks",
        "Kịch bản thực nghiệm": "Thử nghiệm trên nhiều bài toán phân loại ảnh và văn bản.",
        "Phương pháp đánh giá": "Generalization Error, Speedup",
        "Kết quả": "Vượt trội hơn CRAIG về khả năng tổng quát hóa và độ ổn định.",
        "Link": "https://proceedings.mlr.press/v139/killamsetty21a.html"
    },
    {
        "STT": 4,
        "Đề tài / Công bố khoa học": "TabCond: Efficient Tabular Dataset Condensation",
        "Loại bài toán": "Dataset Condensation (Ngưng đọng dữ liệu)",
        "Mục tiêu": "Tổng hợp dữ liệu ảo (Synthetic Data) thay vì chọn dòng từ tập gốc, nhằm nén tri thức vào một lượng cực ít mẫu.",
        "Ngữ cảnh": "Nén dữ liệu mức độ cao (High Compression)",
        "Input": "Tập dữ liệu bảng gốc",
        "Output": "Tập dữ liệu tổng hợp (Mẫu ảo)",
        "Process": "1. Sử dụng VAE để đưa dữ liệu vào không gian ẩn (Latent space). 2. Thực hiện khớp phân phối (Distribution Matching) để dữ liệu ảo mang đặc trưng thống kê của tập gốc. 3. Giải mã về định dạng bảng.",
        "Machine Learning": "XGBoost, MLP, Decision Trees",
        "Kịch bản thực nghiệm": "So sánh khả năng biểu diễn của mẫu ảo so với mẫu thật bị Random Sampling.",
        "Phương pháp đánh giá": "Accuracy, Distribution Similarity",
        "Kết quả": "Tạo ra tập nén siêu nhỏ (vùng 1%) nhưng vẫn cho hiệu năng mô hình cực kỳ ổn định.",
        "Link": "https://dl.acm.org/doi/10.1145/3580305.3599420"
    },
    {
        "STT": 5,
        "Đề tài / Công bố khoa học": "GoodCore: Coreset Selection over Incomplete Data",
        "Loại bài toán": "Incomplete Data Support",
        "Mục tiêu": "Chọn tập đại diện hiệu quả ngay cả khi dữ liệu đầu vào bị thiếu giá trị (NaN/Missing values).",
        "Ngữ cảnh": "Dữ liệu thực tế bị nhiễu và thiếu hụt",
        "Input": "Dữ liệu bảng có giá trị rỗng",
        "Output": "Chỉ số các dòng chất lượng cao nhất",
        "Process": "Lồng ghép lý thuyết 'Thế giới khả thi' để tính toán Gradient kỳ vọng. Thuật toán tham lam chọn dòng giúp giảm thiểu sai số dự đoán trên mọi kịch bản điền khuyết dữ liệu có thể xảy ra.",
        "Machine Learning": "Logistic Regression, SVM",
        "Kịch bản thực nghiệm": "Huấn luyện trên dữ liệu bẩn và đo Accuracy sau khi làm sạch Coreset.",
        "Phương pháp đánh giá": "Lợi ích chi phí (Cleaning Cost savings), Accuracy",
        "Kết quả": "Tiết kiệm 80% công sức làm sạch dữ liệu mà không làm giảm độ chính xác của mô hình.",
        "Link": "https://dl.acm.org/doi/10.1145/3588674"
    },
    {
        "STT": 6,
        "Đề tài / Công bố khoa học": "Selection via Proxy: Efficient Data Selection for Deep Learning",
        "Loại bài toán": "Proxy-based Selection (Lý thuyết nền tảng)",
        "Mục tiêu": "Chứng minh rằng có thể dùng một mô hình nhỏ, rẻ tiền (Proxy) để chọn dữ liệu cho một mô hình lớn, đắt tiền.",
        "Ngữ cảnh": "Huấn luyện mô hình Deep Learning khổng lồ",
        "Input": "Dataset lớn",
        "Output": "Thứ hạng độ quan trọng của dữ liệu",
        "Process": "Huấn luyện một mạng Neural nhẹ (vd: ResNet-18) để tính toán điểm tin cậy hoặc Gradient, sau đó lấy các mẫu quan trọng nhất cho mạng lớn (vd: ResNet-164).",
        "Machine Learning": "CNN, Deep Networks",
        "Kịch bản thực nghiệm": "So sánh thứ hạng mẫu giữa các kiến trúc mô hình khác nhau.",
        "Phương pháp đánh giá": "Spearman Correlation, Training Time Reduction",
        "Kết quả": "Tăng tốc quá trình chọn mẫu 40 lần mà gần như không mất độ chính xác.",
        "Link": "https://openreview.net/forum?id=ryzHXnR5Y7"
    },
    {
        "STT": 7,
        "Đề tài / Công bố khoa học": "GLISTER: Generalization based Data Subset Selection",
        "Loại bài toán": "Bi-level Optimization",
        "Mục tiêu": "Chọn tập con tối ưu hóa trực tiếp khả năng tổng quát hóa của mô hình trên tập Validation.",
        "Ngữ cảnh": "Dữ liệu có nhãn nhiễu (Label Noise)",
        "Input": "Training set, Validation set",
        "Output": "Tập con ổn định",
        "Process": "Giải bài toán tối ưu 2 cấp (Bi-level): Cấp ngoài chọn mẫu để cực tiểu hóa Loss trên tập Validation; Cấp trong cập nhật tham số mô hình.",
        "Machine Learning": "General ML models",
        "Kịch bản thực nghiệm": "Thử nghiệm trên dữ liệu bị cố tình làm sai lệch nhãn.",
        "Phương pháp đánh giá": "Robustness to Noise, Test Accuracy",
        "Kết quả": "Cực kỳ hiệu quả trong việc loại bỏ mẫu nhiễu và mẫu outliers ra khỏi Coreset.",
        "Link": "https://arxiv.org/abs/2012.10630"
    },
    {
        "STT": 8,
        "Đề tài / Công bố khoa học": "SubStrat: A Subset-Based Optimization Strategy for AutoML",
        "Loại bài toán": "AutoML Optimization",
        "Mục tiêu": "Tăng tốc quá trình tìm kiếm mô hình tự động (AutoML) bằng cách chỉ chạy trên tập con đại diện.",
        "Ngữ cảnh": "Hệ thống AutoML tốn kém thời gian",
        "Input": "Toàn bộ không gian tìm kiếm mô hình",
        "Output": "Pipeline mô hình tối ưu",
        "Process": "Dùng thuật toán di truyền (Genetic Algorithm) để tìm tập con dữ liệu bảo tồn được entropy và cấu trúc của tập gốc, sau đó chạy bộ lọc AutoML trên tập này.",
        "Machine Learning": "Auto-sklearn, TPOT",
        "Kịch bản thực nghiệm": "So sánh thời gian chạy AutoML trên tập gốc vs tập SubStrat.",
        "Phương pháp đánh giá": "Search Time, Accuracy loss",
        "Kết quả": "Giảm 75% thời gian tìm kiếm mô hình mà sai số chỉ dưới 4%.",
        "Link": "https://www.vldb.org/pvldb/vol16/p772-lazebnik.pdf"
    },
    {
        "STT": 9,
        "Đề tài / Công bố khoa học": "An Empirical Study of Example Forgetting",
        "Loại bài toán": "Training Dynamics (Động lực học)",
        "Mục tiêu": "Xác định những mẫu dữ liệu nào bị mô hình 'quên' (đang đúng thành sai) trong quá trình huấn luyện.",
        "Ngữ cảnh": "Phân tích hành vi học tập của mạng Neural",
        "Input": "Log huấn luyện qua nhiều Epochs",
        "Output": "Điểm Forgetting Score cho mỗi mẫu",
        "Process": "Theo dõi từng lần cập nhật trọng số. Các mẫu có điểm Forgetting thấp (không bao giờ quên) có thể bị loại bỏ mà không ảnh hưởng kết quả.",
        "Machine Learning": "Deep Learning",
        "Kịch bản thực nghiệm": "Nén tập dữ liệu bằng cách loại bỏ mẫu Unforgettable.",
        "Phương pháp đánh giá": "Generalization performance",
        "Kết quả": "Tìm ra tập lõi chứa các mẫu 'khó' nhất mà mô hình trầy trật mới học được.",
        "Link": "https://arxiv.org/abs/1812.05159"
    },
    {
        "STT": 10,
        "Đề tài / Công bố khoa học": "Dataset Cartography: Mapping and Diagnosing Datasets",
        "Loại bài toán": "Data Maps / Model Diagnostics",
        "Mục tiêu": "Phân loại dữ liệu thành các nhóm dựa trên hành vi của mô hình trong lúc học.",
        "Ngữ cảnh": "Lý thuyết nền tảng cho CoreTab",
        "Input": "Xác suất dự đoán qua các Epochs",
        "Output": "Bản đồ dữ liệu 2D (Confidence vs Variability)",
        "Process": "Tính độ tin cậy trung bình và biến động xác suất. Chia thành: Easy-to-learn (Dễ), Hard-to-learn (Khó - tiềm năng lỗi nhãn), và Ambiguous (Mơ hồ - quan trọng nhất).",
        "Machine Learning": "NLP models, Classification",
        "Kịch bản thực nghiệm": "Đánh giá khả năng OOD (Out-of-distribution) của mô hình học trên tập Ambiguous.",
        "Phương pháp đánh giá": "Standard Benchmarks performance",
        "Kết quả": "Cung cấp cái nhìn trực quan về chất lượng và độ khó của từng điểm dữ liệu.",
        "Link": "https://aclanthology.org/2020.emnlp-main.746/"
    },
    {
        "STT": 11,
        "Đề tài / Công bố khoa học": "Active Learning for CNNs: A Core-Set Approach",
        "Loại bài toán": "Geometric Coreset / K-Center",
        "Mục tiêu": "Chọn tập con giúp đại diện tốt nhất cho phân phối hình học của dữ liệu trong không gian đặc trưng.",
        "Ngữ cảnh": "Học chủ động (Active Learning)",
        "Input": "Đặc trưng (Embeddings) của dữ liệu",
        "Output": "Tập điểm đại diện",
        "Process": "Dùng thuật toán K-Center Greedy để chọn các điểm sao cho khoảng cách tối đa từ bất kỳ điểm nào đến tâm (tập con) là nhỏ nhất.",
        "Machine Learning": "CNNs",
        "Kịch bản thực nghiệm": "Chọn mẫu để gán nhãn thủ công cho Deep Learning.",
        "Phương pháp đánh giá": "Label Efficiency, Accuracy",
        "Kết quả": "Là phương pháp hình học tiêu chuẩn, cực kỳ Diverse (đa dạng) nhưng đôi khi nhạy cảm với Outliers.",
        "Link": "https://openreview.net/forum?id=H1VsbSgAW"
    },
    {
        "STT": 12,
        "Đề tài / Công bố khoa học": "Examples are not Enough, Learn to Criticize! (MMD-critic)",
        "Loại bài toán": "Interpretability / Prototype Selection",
        "Mục tiêu": "Chọn ra các mẫu tiêu biểu (Prototypes) và mẫu đối nghịch (Criticisms) để giải thích dữ liệu.",
        "Ngữ cảnh": "Giải thích mô hình (Explainable AI)",
        "Input": "Tập dữ liệu gốc",
        "Output": "Tập Prototype và tập Criticism",
        "Process": "Tối ưu hóa độ đo Maximum Mean Discrepancy (MMD) để tập con khớp phân phối của tập lớn. Chọn thêm các điểm lỗi (Criticism) nơi Prototype không đại diện được.",
        "Machine Learning": "Model-agnostic",
        "Kịch bản thực nghiệm": "Kiểm tra khả năng hiểu dữ liệu của con người qua các ví dụ được chọn.",
        "Phương pháp đánh giá": "Human Pilot Study, Distribution Fit",
        "Kết quả": "Giúp người dùng hiểu được cả vùng dữ liệu phổ biến và các trường hợp ngoại lệ.",
        "Link": "https://proceedings.neurips.cc/paper/2016/hash/568282245b5952f462f43475c7420108-Abstract.html"
    },
    {
        "STT": 13,
        "Đề tài / Công bố khoa học": "RECON: Efficient Coreset Selection for Multi-Table ML",
        "Loại bài toán": "Relational Data Coreset",
        "Mục tiêu": "Nén dữ liệu từ nhiều bảng SQL mà không cần JOIN thực tế.",
        "Ngữ cảnh": "Hệ quản trị CSDL lớn",
        "Input": "Lược đồ bảng quan hệ",
        "Output": "Indices trên từng bảng con",
        "Process": "Tận dụng cấu trúc Join để ước tính đạo hàm từ các bảng thành phần, sau đó chọn trực tiếp dòng từ bảng gốc trước khi chúng gộp lại.",
        "Machine Learning": "GBDT, Linear Models",
        "Kịch bản thực nghiệm": "Join-intensive datasets.",
        "Phương pháp đánh giá": "Join Time saving, Accuracy",
        "Kết quả": "Tiết kiệm dung lượng lưu trữ trung gian khổng lồ khi làm việc với Big Data.",
        "Link": "https://dl.acm.org/doi/10.14778/3690182.3690187"
    },
    {
        "STT": 14,
        "Đề tài / Công bố khoa học": "Lazier Than Lazy Greedy",
        "Loại bài toán": "Submodular Optimization (Toán học nền tảng)",
        "Mục tiêu": "Tăng tốc tối đa việc chọn mẫu dựa trên hàm cận lồi (vd: Facility Location).",
        "Ngữ cảnh": "Chọn mẫu trên quy mô hàng tỷ điểm",
        "Input": "Hàm mục tiêu cận lồi",
        "Output": "Tập con tối ưu",
        "Process": "Cơ chế Stochastic Greedy: Mỗi bước chỉ kiểm tra một tập con ngẫu nhiên nhỏ thay vì duyệt toàn bộ dữ liệu, đảm bảo tốc độ tuyến tính.",
        "Machine Learning": "Data Summarization",
        "Kịch bản thực nghiệm": "Sensor placement, Image summarization.",
        "Phương pháp đánh giá": "Execution Time, Utility Ratio",
        "Kết quả": "Đạt độ tối ưu 1-1/e với tốc độ nhanh gấp hàng trăm lần thuật toán Greedy thông thường.",
        "Link": "https://www.aaai.org/ocs/index.php/AAAI/AAAI15/paper/view/9793"
    },
    {
        "STT": 15,
        "Đề tài / Công bố khoa học": "DS2: Deep Subset Selection",
        "Loại bài toán": "Model-agnostic Selection",
        "Mục tiêu": "Chọn tập con mà hiệu năng mô hình trên đó phản ánh đúng hiệu năng trên tập gốc (Proxy-free).",
        "Ngữ cảnh": "Học máy chuyên sâu",
        "Input": "Model predictions",
        "Output": "Optimal subset",
        "Process": "Phát triển hàm mục tiêu dựa trên lý thuyết Machine Teaching để tìm ra 'người thầy' (tập dữ liệu nhỏ) dạy tốt nhất cho mô hình học.",
        "Machine Learning": "Any classifier",
        "Kịch bản thực nghiệm": "Image and Tabular benchmarks.",
        "Phương pháp đánh giá": "Test Error convergence",
        "Kết quả": "Tính tổng quát hóa rất cao trên nhiều domain khác nhau.",
        "Link": "https://proceedings.mlr.press/v119/coleman20a.html"
    },
    {
        "STT": 16,
        "Đề tài / Công bố khoa học": "In-Context Data Distillation with TabPFN",
        "Loại bài toán": "Foundation Model Compression",
        "Mục tiêu": "Nén tri thức từ mô hình nền tảng dữ liệu bảng (TabPFN) vào một tập dữ liệu mồi.",
        "Ngữ cảnh": "Modern Tabular ML (2024-2025)",
        "Input": "TabPFN Pre-trained model",
        "Output": "Distilled context (Tập mẫu ảo)",
        "Process": "Tối ưu hóa các mẫu dữ liệu mồi dựa trên cơ chế Attention để khi đưa vào TabPFN, mô hình đạt độ chính xác cao nhất ngay lập tức (Zero-shot/Few-shot).",
        "Machine Learning": "TabPFN, Transformers",
        "Kịch bản thực nghiệm": "So sánh với Standard TabPFN trên 100+ UCI datasets.",
        "Phương pháp đánh giá": "Accuracy, Inference Speed",
        "Kết quả": "Đạt hiệu năng SOTA 2024 cho dữ liệu bảng với kích thước cực nhỏ.",
        "Link": "https://arxiv.org/abs/2402.06971"
    }
]

df_template = pd.read_excel(file_path)
original_columns = df_template.columns.tolist()

df_new = pd.DataFrame(data)
for col in original_columns:
    if col not in df_new.columns:
        df_new[col] = ""

df_new = df_new[original_columns]
df_new.to_excel(file_path, index=False)
print("Reference.xlsx has been successfully updated with detailed Vietnamese content for 16 papers.")
