import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from src.coreset.base import BaseCoresetSelector
from .m08_datamaps import SimpleMLP

class M14_TDColERSelector(BaseCoresetSelector):
    """
    STT: 14
    Paper: "TDBench: A Benchmark for Tabular Deep Learning" (TDColER Algorithm)
    Repo: inwonakng/tdbench
    Mô tả: Phương pháp lấy ý tưởng từ Active Learning và Deep Tabular Representation.
    Nó huấn luyện nhanh một mạng nơ-ron và chọn ra các mẫu có "Độ bất định" (Uncertainty / Entropy)
    lớn nhất, vì đây là những mẫu mang nhiều thông tin ranh giới nhất.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        torch.manual_seed(self.seed)
        
        input_dim = X_train.shape[1]
        output_dim = len(np.unique(y_train))
        
        # Huấn luyện mô hình Đại diện
        model = SimpleMLP(input_dim, output_dim)
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss()
        
        X_t = torch.FloatTensor(X_train)
        y_t = torch.LongTensor(y_train)
        dataset = TensorDataset(X_t, y_t)
        loader = DataLoader(dataset, batch_size=512, shuffle=True)
        
        model.train()
        for epoch in range(3): # Train nhanh 3 epochs
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                out = model(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()
                
        # Tính Uncertainty (Entropy) cho toàn bộ tập dữ liệu
        model.eval()
        all_entropies = []
        
        loader_eval = DataLoader(dataset, batch_size=2048, shuffle=False)
        with torch.no_grad():
            for batch_x, _ in loader_eval:
                logits = model(batch_x)
                probs = torch.softmax(logits, dim=1).numpy()
                
                # Tính Entropy: -sum(p * log(p))
                # Cộng 1e-12 để tránh log(0)
                entropy = -np.sum(probs * np.log(probs + 1e-12), axis=1)
                all_entropies.extend(entropy)
                
        all_entropies = np.array(all_entropies)
        
        # Chọn các điểm có Entropy cao nhất (Độ bất định / Uncertainty lớn nhất)
        # Cộng thêm nhiễu siêu nhỏ để phá vỡ trùng lặp
        noise = np.random.rand(len(X_train)) * 0.001
        idx_sorted = np.argsort(-(all_entropies + noise))
        
        return idx_sorted[:target_n]
