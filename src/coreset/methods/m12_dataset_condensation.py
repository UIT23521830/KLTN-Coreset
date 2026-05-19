import numpy as np
import torch
import torch.nn as nn
from src.coreset.base import BaseCoresetSelector

class M12_DatasetCondensationSelector(BaseCoresetSelector):
    """
    STT: 12
    Paper: "Dataset Condensation with Gradient Matching" (Zhao et al., ICLR 2021)
    Repo: VICO-UoE/DatasetCondensation
    Mô tả: Bản gốc của phương pháp này tạo ra dữ liệu tổng hợp (Synthetic)
    thông qua việc tối ưu Gradient Matching. Tuy nhiên, trong bài toán Subset Selection, 
    ta áp dụng cơ chế K-Means Centers (hoặc Herding) trên không gian Gradient/Đặc trưng
    như một phiên bản Rời rạc (Discrete proxy) để chọn ra các điểm thật mang 
    đặc trưng ngưng tụ (condensed) tốt nhất.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        # OOM/Timeout Trap: Herding có độ phức tạp O(N*K). 
        # Với dữ liệu siêu lớn (K > 50,000), thuật toán sẽ mất hàng tuần để chạy.
        # Ném lỗi để Factory tự động nhảy sang thuật toán tiếp theo.
        if target_n > 50000:
            raise MemoryError(f"Herding Timeout Risk: Target N ({target_n}) quá lớn cho thuật toán O(NK).")
            
        np.random.seed(self.seed)
        unique_classes = np.unique(y_train)
        samples_per_class = max(1, target_n // len(unique_classes))
        
        selected_indices = []
        
        # Phương pháp Herding: Chọn điểm lần lượt sao cho trung bình cộng 
        # của tập con ngày càng tiến sát đến trung bình cộng của toàn bộ tập gốc.
        for cls in unique_classes:
            cls_idx = np.where(y_train == cls)[0]
            X_cls = X_train[cls_idx]
            
            # Tính trung bình toàn cục (Full dataset center)
            mu = np.mean(X_cls, axis=0)
            
            selected_local = []
            current_sum = np.zeros(X_cls.shape[1])
            
            # Chọn điểm đầu tiên gần mu nhất
            distances = np.linalg.norm(X_cls - mu, axis=1)
            first_idx = np.argmin(distances)
            selected_local.append(first_idx)
            current_sum += X_cls[first_idx]
            
            # Herding loop
            for k in range(1, samples_per_class):
                if k >= len(X_cls):
                    break
                # Tiêu chí: Chọn x sao cho (current_sum + x)/(k+1) gần với mu nhất
                # Tương đương với tối thiểu hóa || (current_sum + x) - (k+1)*mu ||
                target = (k + 1) * mu - current_sum
                dist = np.linalg.norm(X_cls - target, axis=1)
                
                # Tránh chọn lại điểm cũ
                dist[selected_local] = np.inf
                
                best_idx = np.argmin(dist)
                selected_local.append(best_idx)
                current_sum += X_cls[best_idx]
                
            selected_global = cls_idx[selected_local]
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
