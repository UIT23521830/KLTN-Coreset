import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from src.coreset.base import BaseCoresetSelector
from .m08_datamaps import SimpleMLP

try:
    import apricot
except ImportError:
    print("[WARNING] Thư viện 'apricot-select' chưa được cài đặt. Vui lòng chạy: pip install apricot-select")

class M05_CraigSelector(BaseCoresetSelector):
    """
    STT: 05
    Paper: "Data Selection for Data-Efficient Instruction Tuning / CRAIG" (Mirzasoleiman et al., 2020)
    Repo: baharanm/craig & decile-team/cords
    Mô tả: Phương pháp CRAIG gốc. Giải bài toán Facility Location trên không gian Gradient
    (dùng apricot) để đảm bảo tập con có tổng gradient xấp xỉ với tập dữ liệu gốc.
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
            
        # Rút trích Pseudo-Gradients (features * error) giống implementation của CORDS
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
        proxy_gradients = features * error_norms
        
        # SỬ DỤNG CHUẨN XÁC HÀM FACILITY LOCATION TỪ APRICOT (đúng theo mã nguồn gốc)
        fl = apricot.functions.facilityLocation.FacilityLocationSelection(
            n_samples=target_n,
            metric='euclidean',
            optimizer='lazy',
            random_state=self.seed
        )
        
        fl.fit(proxy_gradients)
        selected_local_idx = fl.ranking
        
        final_idx = pool_idx[selected_local_idx]
        return final_idx
