import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from src.coreset.base import BaseCoresetSelector
from .m08_datamaps import SimpleMLP

class M07_GlisterSelector(BaseCoresetSelector):
    """
    STT: 07
    Paper: "GLISTER: Generalization based Data Subset Selection" (Killamsetty et al., 2021)
    Repo: dssresearch/GLISTER & decile-team/cords
    Mô tả: Tối ưu hóa hai cấp (Bilevel Optimization). GLISTER chọn một tập con 
    sao cho mô hình được huấn luyện trên tập con đó sẽ đạt Loss thấp nhất trên một tập Validation.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)
        
        # Để chạy được Bi-level optimization, GLISTER gốc tốn rất nhiều tài nguyên.
        # Chúng ta giả lập tính chất của nó: Chọn các mẫu có đóng góp lớn nhất vào việc 
        # giảm Loss chung. "Đóng góp" này xấp xỉ bằng Inner-product của Gradient từng mẫu 
        # với Gradient của tập Validation.
        #
        # Ở đây, ta dùng 10% của pool làm Pseudo-Validation set.
        pool_size = min(len(X_train), max(20000, target_n * 5))
        pool_idx = np.random.choice(len(X_train), pool_size, replace=False)
        
        X_pool = X_train[pool_idx]
        y_pool = y_train[pool_idx]
        
        val_size = max(1000, int(pool_size * 0.1))
        X_val = X_pool[:val_size]
        y_val = y_pool[:val_size]
        
        X_cand = X_pool[val_size:]
        y_cand = y_pool[val_size:]
        cand_idx = pool_idx[val_size:]
        
        input_dim = X_train.shape[1]
        output_dim = len(np.unique(y_train))
        model = SimpleMLP(input_dim, output_dim)
        
        # Train nhanh 1 epoch
        X_t = torch.FloatTensor(X_train)
        y_t = torch.LongTensor(y_train)
        dataset = TensorDataset(X_t, y_t)
        loader = DataLoader(dataset, batch_size=256, shuffle=True)
        
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss(reduction='none')
        model.train()
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            out = model(batch_x)
            loss = criterion(out, batch_y).mean()
            loss.backward()
            optimizer.step()
            
        # Trích xuất Proxy Gradient
        feature_extractor = nn.Sequential(*list(model.net.children())[:-1])
        feature_extractor.eval()
        model.eval()
        
        # 1. Gradient của Validation
        X_val_t = torch.FloatTensor(X_val)
        with torch.no_grad():
            f_val = feature_extractor(X_val_t).numpy()
            logits_val = model(X_val_t)
            probs_val = torch.softmax(logits_val, dim=1).numpy()
            
        y_val_onehot = np.zeros((len(y_val), output_dim))
        y_val_onehot[np.arange(len(y_val)), y_val] = 1
        err_val = probs_val - y_val_onehot
        
        # Proxy validation gradient
        grad_val = np.mean(f_val * np.linalg.norm(err_val, axis=1, keepdims=True), axis=0)
        
        # 2. Gradient của Candidate
        X_cand_t = torch.FloatTensor(X_cand)
        with torch.no_grad():
            f_cand = feature_extractor(X_cand_t).numpy()
            logits_cand = model(X_cand_t)
            probs_cand = torch.softmax(logits_cand, dim=1).numpy()
            
        y_cand_onehot = np.zeros((len(y_cand), output_dim))
        y_cand_onehot[np.arange(len(y_cand)), y_cand] = 1
        err_cand = probs_cand - y_cand_onehot
        
        grad_cand = f_cand * np.linalg.norm(err_cand, axis=1, keepdims=True)
        
        # 3. GLISTER Log-likelihood Taylor approximation:
        # Lợi ích của 1 mẫu xấp xỉ bằng Tích vô hướng Gradient của nó với Validation Gradient.
        # Điểm nào có hướng Gradient càng giống tập Validation (giúp giảm Val Loss) càng tốt.
        utility_scores = np.dot(grad_cand, grad_val)
        
        idx_sorted = np.argsort(-utility_scores)
        
        # Do ta bỏ val_size khỏi candidate, nếu số lượng không đủ, lấy thêm từ validation
        n_needed = target_n
        if n_needed <= len(idx_sorted):
            selected = idx_sorted[:n_needed]
            final_idx = cand_idx[selected]
        else:
            selected_cand = cand_idx
            # Thiếu bao nhiêu bù bằng ngẫu nhiên từ Val
            rem = n_needed - len(selected_cand)
            val_chosen = np.random.choice(pool_idx[:val_size], rem, replace=False)
            final_idx = np.concatenate([selected_cand, val_chosen])
            
        return final_idx
