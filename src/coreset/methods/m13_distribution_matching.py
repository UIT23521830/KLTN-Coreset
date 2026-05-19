import numpy as np
from src.coreset.base import BaseCoresetSelector

class M13_DistributionMatchingSelector(BaseCoresetSelector):
    """
    STT: 13
    Paper: "Dataset Condensation with Distribution Matching" (Zhao et al., WACV 2023)
    Repo: VICO-UoE/DatasetCondensation
    Mô tả: Phiên bản Subset Selection của Distribution Matching. Mục tiêu là chọn
    một tập con sao cho phân phối (đo bằng Maximum Mean Discrepancy - MMD) 
    của tập con giống hệt với phân phối của tập dữ liệu gốc trong không gian đặc trưng.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        np.random.seed(self.seed)
        unique_classes = np.unique(y_train)
        samples_per_class = max(1, target_n // len(unique_classes))
        
        selected_indices = []
        
        # MMD Matching Proxy (Rời rạc hóa): Tối thiểu hóa khoảng cách MMD bằng cách 
        # chọn các điểm sao cho Covariance Matrix (hoặc Mean) của tập con 
        # gần nhất với Covariance của tập gốc. 
        # Để hiệu quả trên Tabular Data lớn, ta dùng Random Projection (hoặc lấy mẫu đại diện)
        # và ưu tiên các điểm có sự đa dạng cao nằm gần phân phối trung tâm.
        
        for cls in unique_classes:
            cls_idx = np.where(y_train == cls)[0]
            X_cls = X_train[cls_idx]
            
            # Tính phân phối gốc (Mean và Variance)
            mu_orig = np.mean(X_cls, axis=0)
            var_orig = np.var(X_cls, axis=0)
            
            # Lấy mẫu ngẫu nhiên để tăng tốc độ nếu dữ liệu quá to
            pool_size = min(len(X_cls), samples_per_class * 20)
            pool_idx_local = np.random.choice(len(X_cls), pool_size, replace=False)
            X_pool = X_cls[pool_idx_local]
            
            # Đánh giá độ "Phù hợp Phân phối" (Distribution Match Score)
            # Điểm tốt là điểm vừa không quá lệch khỏi trung bình, vừa đóng góp 
            # vào phương sai chung của phân phối.
            # Ta dùng hàm mật độ Gaussian đa biến (đơn giản hóa) làm thước đo MMD cục bộ.
            # Tránh chia cho 0
            var_safe = var_orig + 1e-8
            
            # Distance chuẩn hóa (Mahalanobis thu gọn)
            dist_normalized = np.sum(((X_pool - mu_orig) ** 2) / var_safe, axis=1)
            
            # Khác với Moderate-DS (chọn Median), MMD cần một tập con khôi phục lại phân phối gốc,
            # nên ta cần chọn các điểm có khoảng cách phân bố đều đặn (từ gần tâm đến xa tâm)
            # Cách đơn giản: Phân tầng (Stratified) khoảng cách và bốc đều.
            
            # Sắp xếp theo khoảng cách
            sorted_by_dist = np.argsort(dist_normalized)
            
            # Lấy mẫu cách đều (Uniform striding) để đảm bảo phân phối MMD được dàn trải đúng dạng Gauss
            step = max(1, len(sorted_by_dist) // samples_per_class)
            selected_local = sorted_by_dist[::step][:samples_per_class]
            
            selected_global = cls_idx[pool_idx_local[selected_local]]
            selected_indices.extend(selected_global)
            
        final_idx = np.array(selected_indices)
        
        if len(final_idx) > target_n:
            final_idx = final_idx[:target_n]
        elif len(final_idx) < target_n:
            rem = target_n - len(final_idx)
            pool = np.setdiff1d(np.arange(len(X_train)), final_idx)
            rem_idx = np.random.choice(pool, rem, replace=False)
            final_idx = np.concatenate([final_idx, rem_idx])
            
        return final_idx
