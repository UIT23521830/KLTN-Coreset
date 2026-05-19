import numpy as np
import torch
from src.coreset.base import BaseCoresetSelector

class M11_ModerateDSSelector(BaseCoresetSelector):
    """
    STT: 11
    Paper: "Moderate Coreset: A Universal Method of Data Selection" (Xia et al., ICLR 2023)
    Repo: tmllab/2023_ICLR_Moderate-DS
    Mô tả: Thay vì chọn điểm Hard (dễ nhiễu) hay Easy (ít thông tin), Moderate-DS
    chọn các điểm có khoảng cách "trung bình" đến tâm cụm của từng class, 
    nhằm giữ được phân phối gốc và định hình biên quyết định tốt nhất.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        np.random.seed(self.seed)
        unique_classes = np.unique(y_train)
        
        # Số lượng mẫu cần chọn cho mỗi class (để cân bằng)
        samples_per_class = max(1, target_n // len(unique_classes))
        
        selected_indices = []
        
        for cls in unique_classes:
            cls_idx = np.where(y_train == cls)[0]
            X_cls = X_train[cls_idx]
            
            # Tính trung tâm (Center) của class này
            center = np.mean(X_cls, axis=0)
            
            # Tính khoảng cách Euclidean từ các điểm tới Center
            # Để tiết kiệm RAM cho ma trận lớn, ta dùng hàm linalg.norm
            distances = np.linalg.norm(X_cls - center, axis=1)
            
            # Tính giá trị Median distance (Điểm ở khoảng cách trung bình - Moderate)
            median_dist = np.median(distances)
            
            # Mức độ "Moderate" được đo bằng độ lệch so với Median. Càng gần Median càng tốt.
            moderate_scores = np.abs(distances - median_dist)
            
            # Sắp xếp tăng dần (Gần Median nhất đứng đầu)
            # Dùng argsort trên idx cục bộ của class, sau đó map ngược ra idx gốc
            idx_sorted_local = np.argsort(moderate_scores)
            
            selected_local = idx_sorted_local[:samples_per_class]
            selected_global = cls_idx[selected_local]
            selected_indices.extend(selected_global)
            
        final_idx = np.array(selected_indices)
        
        # Lấy đúng số lượng target_n (trường hợp chia lấy phần nguyên bị lẻ)
        if len(final_idx) > target_n:
            final_idx = final_idx[:target_n]
        elif len(final_idx) < target_n:
            # Bù ngẫu nhiên nếu còn thiếu một vài điểm
            rem = target_n - len(final_idx)
            pool = np.setdiff1d(np.arange(len(X_train)), final_idx)
            rem_idx = np.random.choice(pool, rem, replace=False)
            final_idx = np.concatenate([final_idx, rem_idx])
            
        return final_idx
