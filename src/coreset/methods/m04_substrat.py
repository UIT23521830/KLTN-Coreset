import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from src.coreset.base import BaseCoresetSelector

try:
    import apricot
except ImportError:
    print("[WARNING] Thư viện 'apricot-select' chưa được cài đặt. Vui lòng chạy: pip install apricot-select")

class M04_SubStratSelector(BaseCoresetSelector):
    """
    STT: 04
    Paper: "SubStrat: A Subset Selection Strategy for Efficient Machine Learning"
    Repo: teddy4445/SubStrat
    Mô tả: Phương pháp tối ưu hóa Submodular. Dùng hàm Facility Location 
    của thư viện apricot để giải quyết chính xác bài toán của tác giả gốc.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        np.random.seed(self.seed)
        
        # Để tránh tràn RAM do tính toán pairwise matrix toàn tập, 
        # tác giả gốc thường chạy trên từng class hoặc dùng mini-batch.
        # Ta sẽ chạy trên tập pool đại diện lớn (nhưng không vượt giới hạn RAM).
        pool_size = min(len(X_train), max(20000, target_n * 5))
        pool_idx = np.random.choice(len(X_train), pool_size, replace=False)
        X_pool = X_train[pool_idx]
        
        # Áp dụng chính xác hàm FacilityLocationSelection từ apricot
        # giống hệt cách thư viện CORDS/SubStrat hoạt động
        fl = apricot.functions.facilityLocation.FacilityLocationSelection(
            n_samples=target_n,
            metric='euclidean',
            optimizer='lazy',
            random_state=self.seed
        )
        
        # Fit và lấy index được chọn
        fl.fit(X_pool)
        selected_local_idx = fl.ranking
        
        # Chuyển đổi về index toàn cục
        final_idx = pool_idx[selected_local_idx]
        return final_idx
