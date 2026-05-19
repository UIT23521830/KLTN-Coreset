import numpy as np

class BaseCoresetSelector:
    """
    Base class (Interface) cho tất cả các phương pháp nén dữ liệu (Coreset).
    Bắt buộc mọi SOTA wrapper phải kế thừa và thiết lập hàm `select`.
    """
    def __init__(self, random_seed=42):
        self.seed = random_seed
        self.last_core_time = 0.0
        self.last_search_time = 0.0
        self._set_seed()

    def _set_seed(self):
        """Đảm bảo tính tái lập (Reproducibility) bằng cách cố định seed"""
        np.random.seed(self.seed)

    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        """
        Input:
            X_train: Ma trận đặc trưng (n_samples, n_features)
            y_train: Vector nhãn (n_samples,)
            budget_ratio: Tỷ lệ ngân sách nén (ví dụ: 0.05 tức là nén lấy 5%)
            
        Output:
            Một mảng NumPy chứa các index (chỉ mục hàng) được chọn.
            Ví dụ: array([0, 5, 12, 102])
        """
        raise NotImplementedError("Phương thức `select` phải được ghi đè ở class con!")
