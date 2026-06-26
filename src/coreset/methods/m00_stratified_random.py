import numpy as np
from sklearn.model_selection import train_test_split
from src.coreset.base import BaseCoresetSelector

class M00_StratifiedRandomSelector(BaseCoresetSelector):
    """
    STT: 00
    Mô tả: Lựa chọn ngẫu nhiên có bảo toàn tỉ lệ class (Stratified).
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        try:
            budget_n = target_n / len(X_train)
            if budget_n >= 1.0:
                budget_n = 0.9999
            _, _, _, selected_idx = train_test_split(
                X_train, np.arange(len(X_train)), 
                test_size=budget_n, 
                stratify=y_train, 
                random_state=self.random_seed if hasattr(self, 'random_seed') else 42
            )
        except ValueError:
            # Fallback nếu dữ liệu quá mất cân bằng không stratify được
            selected_idx = np.random.choice(len(X_train), size=target_n, replace=False)
            
        return selected_idx
