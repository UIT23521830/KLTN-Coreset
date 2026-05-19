import os
import sys
import numpy as np
import pandas as pd
import time
from src.coreset.base import BaseCoresetSelector

# Thêm đường dẫn tới thư mục repo gốc của CoreTab
repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "sota_repos", "coretab"))
if repo_path not in sys.path:
    sys.path.append(repo_path)

try:
    from coretab.coreset_algorithms import CoreTabDT
except ImportError:
    CoreTabDT = None
    print("Warning: Không thể import CoreTabDT từ repo gốc.")

class M03_CoreTabSelector(BaseCoresetSelector):
    """
    STT: 03
    Paper: "Datamap-Driven Tabular Coreset Selection for Classifier Training" (Hadar et al., 2025)
    Repo: avivhadar33/coretab
    Mô tả (Nguyên bản): Sử dụng Decision Tree để lọc các nhánh lá thuần nhất.
    Sử dụng Binary Search để tìm sample_percent tiệm cận với target_n.
    """
    def __init__(self, random_seed=42):
        super().__init__(random_seed)

    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        if CoreTabDT is None:
            raise ImportError("Không tìm thấy mã nguồn CoreTabDT. Hãy đảm bảo repo coretab đã được clone.")
            
        # Chuyển Numpy thành Pandas DataFrame (yêu cầu của CoreTabDT)
        feature_names = [f"F_{i}" for i in range(X_train.shape[1])]
        X_df = pd.DataFrame(X_train, columns=feature_names)
        y_series = pd.Series(y_train)
        
        # Binary Search cho sample_percent
        low, high = 0.0, 1.0
        best_idx = None
        best_diff = float('inf')
        best_time = 0.0
        
        self.last_search_time = 0.0
        
        # Sử dụng đúng tham số budget_ratio
        # examples_to_keep = 1 hoặc tùy chỉnh thủ công theo kích thước tập dữ liệu
        coretab = CoreTabDT(sample_percent=budget_ratio, examples_to_keep=1)
        
        t0 = time.time()
        try:
            X_filtered, _ = coretab.create_coreset(X_df, y_series)
            best_idx = X_filtered.index.values
        except Exception as e:
            best_idx = np.array([])
            
        self.last_core_time = time.time() - t0
        
        actual_ratio = len(best_idx) / len(X_train) if len(X_train) > 0 else 0
        print(f"    [CoreTab] Đã chọn: {len(best_idx)} mẫu (Tỷ lệ thực tế: {actual_ratio:.2%} vs Yêu cầu: {budget_ratio:.2%})")
        return best_idx
