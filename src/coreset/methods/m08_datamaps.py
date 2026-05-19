import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from src.coreset.base import BaseCoresetSelector

class SimpleMLP(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(SimpleMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim),
            nn.Softmax(dim=1)
        )
    def forward(self, x):
        return self.net(x)

class M08_DataMapsSelector(BaseCoresetSelector):
    """
    STT: 08
    Paper: "Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics" (Swayamdipta et al., 2020)
    Repo: allenai/cartography
    Mô tả: Sử dụng mạng MLP (thay thế cho RoBERTa trong bản gốc) để ghi log 
    xác suất dự đoán qua các epochs. Tính toán Confidence và Variability để 
    tìm ra các mẫu Ambiguous (khó đoán) làm Coreset.
    """
    def __init__(self, random_seed=42, epochs=10):
        super().__init__(random_seed)
        self.epochs = epochs

    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        # Đảm bảo tính ngẫu nhiên cố định cho PyTorch
        torch.manual_seed(self.seed)
        
        input_dim = X_train.shape[1]
        output_dim = len(np.unique(y_train))
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = SimpleMLP(input_dim, output_dim).to(device)
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss()
        
        X_t = torch.FloatTensor(X_train)
        y_t = torch.LongTensor(y_train)
        dataset = TensorDataset(X_t, y_t)
        loader = DataLoader(dataset, batch_size=256, shuffle=True)
        
        history_probas = []
        
        for epoch in range(self.epochs):
            # Tính toán proba trước khi train epoch mới
            model.eval()
            with torch.no_grad():
                # Split thành các chunk nhỏ để tránh OOM RAM nếu X_train quá lớn
                probas = []
                for i in range(0, len(X_t), 10000):
                    batch = X_t[i:i+10000].to(device)
                    p = model(batch).cpu().numpy()
                    probas.append(p)
                probas = np.concatenate(probas, axis=0)
                history_probas.append(probas)
            
            # Huấn luyện mô hình
            model.train()
            for batch_x, batch_y in loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                optimizer.zero_grad()
                out = model(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()
                
        history_probas = np.array(history_probas) # Shape: (epochs, n_samples, n_classes)
        n_samples = X_train.shape[0]
        
        # Trích xuất xác suất dự đoán đúng class cho từng epoch
        correct_probas = history_probas[np.arange(self.epochs)[:, None], np.arange(n_samples), y_train]
        
        # DataMaps Formulas:
        # 1. Confidence = Mean(correct_probas)
        # 2. Variability = Std(correct_probas)
        confidences = np.mean(correct_probas, axis=0)
        variabilities = np.std(correct_probas, axis=0)
        
        # Cartography Paper ưu tiên vùng "Ambiguous" (độ biến thiên cao)
        # Sắp xếp giảm dần theo variability
        idx_sorted = np.argsort(-variabilities)
        
        return idx_sorted[:target_n]
