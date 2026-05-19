import pandas as pd

file_path = 'C:/KLTN/paper/Reference.xlsx'

# Data for the verified SOTA papers
data = [
    {
        "STT": 1,
        "Đề tài / Công bố khoa học": "Datamap-Driven Tabular Coreset Selection for Classifier Training",
        "Loại bài toán": "Classification",
        "Mục tiêu": "Coreset Selection for Tabular Data",
        "Ngữ cảnh": "Tabular Data",
        "Input": "Tabular Dataset, Budget",
        "Output": "Coreset Indices",
        "Data": "Tabular",
        "Ingest": "Batch",
        "Process": "Datamap-based Selection",
        "Machine Learning": "XGBoost, GBDT",
        "Kịch bản thực nghiệm": "Comparison with 11 baselines",
        "Phương pháp đánh giá": "F1-score, CCT, MTT",
        "Công nghệ và nền tảng triển khai": "Python, XGBoost",
        "Kết quả": "SOTA performance on multiple datasets",
        "Source": "Aviv Hadar, et al.",
        "BibTeX": "@article{hadar2024datamap, title={Datamap-Driven Tabular Coreset Selection for Classifier Training}, author={Hadar, Aviv and Milo, Tova and Razmadze, Kathy}, journal={PVLDB}, year={2024}}",
        "Báo cáo / Code": "https://github.com/avivhadar33/coretab",
        "Năm xuất bản/ Tên tạp chí hội nghị": "2024 / PVLDB",
        "Link": "https://www.vldb.org/pvldb/vol18/p876-hadar.pdf"
    },
    {
        "STT": 2,
        "Đề tài / Công bố khoa học": "CRAIG: Coresets for Accelerating Incremental Gradient Descent",
        "Loại bài toán": "Regression/Classification",
        "Mục tiêu": "Gradient Matching for Coreset Selection",
        "Ngữ cảnh": "Deep Learning / General ML",
        "Input": "Dataset, Gradients",
        "Output": "Weighted Coreset",
        "Data": "Image/Tabular",
        "Ingest": "Batch",
        "Process": "Submodular Optimization",
        "Machine Learning": "SGD-based models",
        "Kịch bản thực nghiệm": "Speeding up training",
        "Phương pháp đánh giá": "Training loss, Accuracy",
        "Công nghệ và nền tảng triển khai": "PyTorch",
        "Kết quả": "Efficiency in training large models",
        "Source": "Mirzasoleiman, et al.",
        "BibTeX": "@inproceedings{mirzasoleiman2020craig, title={CRAIG: Coresets for Accelerating Incremental Gradient Descent}, author={Mirzasoleiman, Baharan and Bilmes, Jeff and Leskovec, Jure}, booktitle={ICML}, year={2020}}",
        "Báo cáo / Code": "https://github.com/baharanm/craig",
        "Năm xuất bản/ Tên tạp chí hội nghị": "2020 / ICML",
        "Link": "https://proceedings.mlr.press/v119/mirzasoleiman20a.html"
    },
    {
        "STT": 3,
        "Đề tài / Công bố khoa học": "GradMatch: Gradient Matching for Data-Efficient Learning",
        "Loại bài toán": "Classification",
        "Mục tiêu": "Adaptive Gradient Matching",
        "Ngữ cảnh": "Data-Efficient Learning",
        "Input": "Dataset",
        "Output": "Subset with Weights",
        "Data": "Multi-domain",
        "Ingest": "Batch",
        "Process": "Orthogonal Matching Pursuit",
        "Machine Learning": "Deep Neural Networks",
        "Kịch bản thực nghiệm": "Comparison with Random/CRAIG",
        "Phương pháp đánh giá": "Test Accuracy, Training Time",
        "Công nghệ và nền tảng triển khai": "PyTorch (DISTIL)",
        "Kết quả": "Better generalization than CRAIG",
        "Source": "Killamsetty, et al.",
        "BibTeX": "@inproceedings{killamsetty2021gradmatch, title={GradMatch: Gradient Matching for Data-Efficient Learning}, author={Killamsetty, Krishnateja and et al.}, booktitle={ICML}, year={2021}}",
        "Báo cáo / Code": "https://github.com/decile-team/distil",
        "Năm xuất bản/ Tên tạp chí hội nghị": "2021 / ICML",
        "Link": "https://proceedings.mlr.press/v139/killamsetty21a.html"
    },
    {
        "STT": 4,
        "Đề tài / Công bố khoa học": "GoodCore: Coreset Selection over Incomplete Data",
        "Loại bài toán": "Incomplete Data",
        "Mục tiêu": "Handling Missing Values in Coreset Selection",
        "Ngữ cảnh": "Tabular Data with NaNs",
        "Input": "Incomplete Dataset",
        "Output": "Coreset",
        "Data": "Tabular",
        "Ingest": "Batch",
        "Process": "Uncertainty-aware Selection",
        "Machine Learning": "SVM, MLP",
        "Kịch bản thực nghiệm": "Testing on dirty datasets",
        "Phương pháp đánh giá": "Accuracy on full vs coreset",
        "Công nghệ và nền tảng triển khai": "Python",
        "Kết quả": "Robustness to missing data",
        "Source": "Wang, et al.",
        "BibTeX": "@inproceedings{wang2023goodcore, title={GoodCore: Coreset Selection over Incomplete Data}, author={Wang, et al.}, booktitle={SIGMOD}, year={2023}}",
        "Báo cáo / Code": "https://github.com/megagonlabs/goodcore",
        "Năm xuất bản/ Tên tạp chí hội nghị": "2023 / SIGMOD",
        "Link": "https://dl.acm.org/doi/10.1145/3588674"
    },
    {
        "STT": 5,
        "Đề tài / Công bố khoa học": "Selection via Proxy: Efficient Data Selection for Deep Learning",
        "Loại bài toán": "Subset Selection",
        "Mục tiêu": "Proxy Models for Fast Selection",
        "Ngữ cảnh": "Large-scale Training",
        "Input": "Large Dataset",
        "Output": "Subset Indices",
        "Data": "Vision/Tabular",
        "Ingest": "Batch",
        "Process": "Proxy Training",
        "Machine Learning": "Deep Learning",
        "Kịch bản thực nghiệm": "Comparing small vs large model selection",
        "Phương pháp đánh giá": "Training Speedup, Recall",
        "Công nghệ và nền tảng triển khai": "PyTorch",
        "Kết quả": "Selection with small models generalizes to large ones",
        "Source": "Coleman, et al.",
        "BibTeX": "@inproceedings{coleman2020svp, title={Selection via Proxy: Efficient Data Selection for Deep Learning}, author={Coleman, et al.}, booktitle={ICLR}, year={2020}}",
        "Báo cáo / Code": "https://github.com/stanford-futuredata/selection-via-proxy",
        "Năm xuất bản/ Tên tạp chí hội nghị": "2020 / ICLR",
        "Link": "https://openreview.net/forum?id=ryzHXnR5Y7"
    }
]

# Read original columns to match them exactly
df_template = pd.read_excel(file_path)
original_columns = df_template.columns.tolist()

# Create dataframe from data
df_new = pd.DataFrame(data)

# Ensure it matches template columns (filling missing as empty)
for col in original_columns:
    if col not in df_new.columns:
        df_new[col] = ""

# Reorder to match template exactly
df_new = df_new[original_columns]

# Write back
df_new.to_excel(file_path, index=False)
print("Successfully filled Reference.xlsx with 5 SOTA papers.")
