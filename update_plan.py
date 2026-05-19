import pandas as pd
import numpy as np

file_path = r'C:\KLTN\paper\Plan.xlsx'

# Đọc file excel
df = pd.read_excel(file_path)

# Các repo tương ứng với 15 phương pháp
repos_dict = {
    "Random Selection": "Không có (Baseline toán học)",
    "RECON": "for0nething/RECON",
    "CoreTab": "avivhadar33/coretab",
    "SubStrat": "teddy4445/SubStrat",
    "CRAIG": "baharanm/craig & decile-team/cords",
    "GradMatch": "decile-team/cords",
    "GLISTER": "dssresearch/GLISTER",
    "Data Maps": "allenai/cartography",
    "Forgetting Events": "mtoneva/example_forgetting",
    "SVP": "stanford-futuredata/selection-via-proxy",
    "Moderate-DS": "tmllab/2023_ICLR_Moderate-DS",
    "Dataset Condensation": "VICO-UoE/DatasetCondensation",
    "Distribution Matching": "VICO-UoE/DatasetCondensation",
    "C2TC": "Sssara-5/TF-TabularCondensation",
    "TDColER": "inwonakng/tdbench"
}

# Cột tên phương pháp thường là cột đầu tiên hoặc cột có chứa tên các thuật toán
# Ta tìm cột chứa các tên này
method_col = df.columns[0] # Giả định cột đầu tiên là tên phương pháp

if 'Repo GitHub' not in df.columns:
    # Hàm map để tạo cột mới
    def get_repo(name):
        for k, v in repos_dict.items():
            if str(name).strip().lower() in k.lower() or k.lower() in str(name).strip().lower():
                return v
        return ""
        
    df['Repo GitHub'] = df[method_col].apply(get_repo)
    
    # Ghi đè lại file
    df.to_excel(file_path, index=False)
    print("Đã thêm cột 'Repo GitHub' thành công!")
else:
    print("Cột 'Repo GitHub' đã tồn tại!")
