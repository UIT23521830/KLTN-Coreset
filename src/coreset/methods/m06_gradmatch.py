import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.linear_model import OrthogonalMatchingPursuit
from src.coreset.base import BaseCoresetSelector
from .m08_datamaps import SimpleMLP

class M06_GradMatchSelector(BaseCoresetSelector):
    """
    STT: 06
    Paper: "GradMatch: Gradient Matching based Data Subset Selection" (Killamsetty et al., 2021)
    Repo: decile-team/cords
    Mô tả: Phương pháp gốc GradMatch. Sử dụng chuẩn xác thuật toán
    Orthogonal Matching Pursuit (OMP) để tìm ra một tập con sao cho tổng
    Gradient của nó xấp xỉ tổng Gradient của toàn bộ tập dữ liệu.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)
        
        input_dim = X_train.shape[1]
        output_dim = len(np.unique(y_train))
        model = SimpleMLP(input_dim, output_dim)
        criterion = nn.CrossEntropyLoss(reduction='none')
        
        X_t = torch.FloatTensor(X_train)
        y_t = torch.LongTensor(y_train)
        dataset = TensorDataset(X_t, y_t)
        loader = DataLoader(dataset, batch_size=256, shuffle=True)
        
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        model.train()
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            out = model(batch_x)
            loss = criterion(out, batch_y).mean()
            loss.backward()
            optimizer.step()
            
        feature_extractor = nn.Sequential(*list(model.net.children())[:-1])
        feature_extractor.eval()
        model.eval()
        
        pool_size = min(len(X_train), max(10000, target_n * 5))
        pool_idx = np.random.choice(len(X_train), pool_size, replace=False)
        X_pool = X_train[pool_idx]
        y_pool = y_train[pool_idx]
        
        X_pool_t = torch.FloatTensor(X_pool)
        with torch.no_grad():
            features = feature_extractor(X_pool_t).numpy()
            logits = model(X_pool_t)
            probs = torch.softmax(logits, dim=1).numpy()
            
        y_onehot = np.zeros((len(y_pool), output_dim))
        y_onehot[np.arange(len(y_pool)), y_pool] = 1
        errors = probs - y_onehot
        
        error_norms = np.linalg.norm(errors, axis=1, keepdims=True)
        proxy_gradients = features * error_norms # Shape: (pool_size, features_dim)
        
        # OMP đòi hỏi bài toán: Giải min || full_grad - proxy_gradients.T @ weights ||_2
        full_gradient = np.mean(proxy_gradients, axis=0) # Vector mục tiêu y (n_features,)
        
        # Ma trận X cho OMP có shape (n_features, pool_size)
        X_omp = proxy_gradients.T
        y_omp = full_gradient
        
        # SỬ DỤNG CHUẨN XÁC THUẬT TOÁN OMP TỪ SKLEARN
        omp = OrthogonalMatchingPursuit(n_nonzero_coefs=target_n, fit_intercept=False)
        omp.fit(X_omp, y_omp)
        
        # Các hệ số khác 0 chính là các mẫu được OMP chọn
        selected_local_idx = np.nonzero(omp.coef_)[0]
        
        # Dự phòng trường hợp OMP chọn ít hơn target_n do hội tụ sớm
        if len(selected_local_idx) < target_n:
            rem = target_n - len(selected_local_idx)
            pool = np.setdiff1d(np.arange(pool_size), selected_local_idx)
            rem_idx = np.random.choice(pool, rem, replace=False)
            selected_local_idx = np.concatenate([selected_local_idx, rem_idx])
        elif len(selected_local_idx) > target_n:
            selected_local_idx = selected_local_idx[:target_n]
            
        final_idx = pool_idx[selected_local_idx]
        return final_idx
