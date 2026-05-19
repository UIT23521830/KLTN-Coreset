import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from src.coreset.base import BaseCoresetSelector
from .m08_datamaps import SimpleMLP

class M09_ForgettingSelector(BaseCoresetSelector):
    """
    STT: 09
    Paper: "An Empirical Study of Example Forgetting during Deep Neural Network Learning" (Toneva et al., 2018)
    Repo: mtoneva/example_forgetting
    Mô tả: Đếm số lần một mẫu dữ liệu bị "quên" (từ dự đoán đúng chuyển sang dự đoán sai)
    qua các epochs huấn luyện. Những mẫu có độ "quên" cao được coi là quan trọng.
    """
    def __init__(self, random_seed=42, epochs=10):
        super().__init__(random_seed)
        self.epochs = epochs

    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
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
        
        # Mảng lưu vết kết quả dự đoán (Đúng/Sai) qua từng epoch
        correct_predictions = []
        
        for epoch in range(self.epochs):
            # Tính toán độ chính xác trước khi train epoch mới
            model.eval()
            with torch.no_grad():
                preds = []
                for i in range(0, len(X_t), 10000):
                    batch = X_t[i:i+10000].to(device)
                    p = model(batch).argmax(dim=1).cpu().numpy()
                    preds.append(p)
                preds = np.concatenate(preds, axis=0)
                is_correct = (preds == y_train)
                correct_predictions.append(is_correct)
            
            # Huấn luyện mô hình
            model.train()
            for batch_x, batch_y in loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                optimizer.zero_grad()
                out = model(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()
                
        correct_predictions = np.array(correct_predictions) # Shape: (epochs, n_samples)
        
        # Tính toán Forgetting Events
        forgetting_counts = np.zeros(len(X_train))
        # Nếu epoch t dự đoán đúng (True), nhưng epoch t+1 dự đoán sai (False) -> Bị quên
        for t in range(self.epochs - 1):
            forgotten = (correct_predictions[t] == True) & (correct_predictions[t+1] == False)
            forgetting_counts += forgotten.astype(int)
            
        # Ưu tiên các điểm bị quên nhiều nhất
        # Sắp xếp giảm dần theo số lần bị quên
        # Sắp xếp giảm dần theo số lần bị quên
        idx_sorted = np.argsort(-forgetting_counts)
        
        return idx_sorted[:target_n]
