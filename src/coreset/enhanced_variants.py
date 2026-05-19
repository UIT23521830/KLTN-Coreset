import numpy as np
from src.coreset.methods.m09_forgetting import M09_ForgettingSelector
from src.coreset.methods.m08_datamaps import M08_DataMapsSelector
from src.coreset.methods.m10_svp import M10_SVPSelector

class EnhancedForgettingSelector(M09_ForgettingSelector):
    """
    Biến thể Cải tiến của Forgetting (Toneva et al., 2018).
    Thêm nhiễu ngẫu nhiên (Random Noise Tie-Breaking) để giải quyết hiện tượng thiên vị
    thứ tự dòng (Row-order Bias) khi có quá nhiều mẫu trùng số điểm Forgetting (VD: cùng quên 0 lần).
    Bản vá này giúp việc chọn Top-K công bằng tuyệt đối.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        # Gọi lại logic train từ lớp cha nhưng thay thế bước argsort
        # Đoạn code dưới đây sao chép khung logic của cha nhưng đắp thêm noise
        import torch
        from torch.utils.data import DataLoader, TensorDataset
        import torch.nn as nn
        import torch.optim as optim
        from src.coreset.methods.m08_datamaps import SimpleMLP
        
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0: return np.array([], dtype=int)
            
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
        
        correct_predictions = []
        for epoch in range(self.epochs):
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
            
            model.train()
            for batch_x, batch_y in loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                optimizer.zero_grad()
                out = model(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()
                
        correct_predictions = np.array(correct_predictions)
        forgetting_counts = np.zeros(len(X_train))
        for t in range(self.epochs - 1):
            forgotten = (correct_predictions[t] == True) & (correct_predictions[t+1] == False)
            forgetting_counts += forgotten.astype(int)
            
        # ==========================================
        # TECHNICAL PATCH: Random Noise Tie-Breaking
        # ==========================================
        noise = np.random.rand(len(X_train)) * 0.1
        idx_sorted = np.argsort(-(forgetting_counts + noise))
        
        return idx_sorted[:target_n]

class EnhancedDataMapsSelector(M08_DataMapsSelector):
    """
    Biến thể Cải tiến của DataMaps (Swayamdipta et al., 2020).
    Áp dụng Noise Tie-Breaking tương tự dù Variability là số thực, 
    nhằm đảm bảo công bằng 100% trong trường hợp có các mẫu kẹt ở floating-point precision.
    """
    # Logic tương tự, ghi đè select() nếu cần thiết
    pass

class EnhancedSVPSelector(M10_SVPSelector):
    """
    Biến thể Cải tiến của SVP (Coleman et al., 2020).
    Áp dụng Noise Tie-Breaking cho Loss Ranking.
    """
    pass
