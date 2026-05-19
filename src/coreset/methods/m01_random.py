import numpy as np
from src.coreset.base import BaseCoresetSelector

class M01_RandomSelector(BaseCoresetSelector):
    """
    STT: 01
    Paper: Baseline (Ngẫu nhiên)
    Mô tả: Lựa chọn ngẫu nhiên các mẫu dữ liệu dựa trên phân phối đồng đều.
    Dùng để làm thước đo (baseline) cho các thuật toán SOTA khác.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        # Chọn ngẫu nhiên không hoàn lại (replace=False)
        selected_idx = np.random.choice(len(X_train), size=target_n, replace=False)
        return selected_idx
