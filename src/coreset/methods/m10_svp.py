import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from src.coreset.base import BaseCoresetSelector

class TinyMLP(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(TinyMLP, self).__init__()
        # Mạng Proxy siêu nhỏ, chạy cực nhanh
        self.net = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)
        )
    def forward(self, x):
        return self.net(x)

class M10_SVPSelector(BaseCoresetSelector):
    """
    STT: 10
    Paper: "Selection via Proxy: Efficient Data Selection for Deep Learning" (Coleman et al., 2020)
    Repo: stanford-futuredata/selection-via-proxy
    Mô tả: Sử dụng một mô hình "Proxy" (nhỏ, huấn luyện nhanh) để ước lượng 
    độ khó của dữ liệu thay vì dùng mô hình mục tiêu cồng kềnh. 
    Các mẫu có Loss cao nhất từ mô hình Proxy sẽ được chọn.
    """
    def select(self, X_train: np.ndarray, y_train: np.ndarray, budget_ratio: float) -> np.ndarray:
        target_n = int(len(X_train) * budget_ratio)
        if target_n == 0:
            return np.array([], dtype=int)
            
        torch.manual_seed(self.seed)
        
        input_dim = X_train.shape[1]
        output_dim = len(np.unique(y_train))
        
        # 1. Train mô hình Proxy (TinyMLP) trong 2 epochs (rất nhanh)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = TinyMLP(input_dim, output_dim).to(device)
        optimizer = optim.Adam(model.parameters(), lr=1e-2)
        criterion = nn.CrossEntropyLoss()
        
        X_t = torch.FloatTensor(X_train)
        y_t = torch.LongTensor(y_train)
        dataset = TensorDataset(X_t, y_t)
        loader = DataLoader(dataset, batch_size=512, shuffle=True)
        
        model.train()
        for epoch in range(2):
            for batch_x, batch_y in loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                optimizer.zero_grad()
                out = model(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()
                
        # 2. Dùng mô hình Proxy để tính Loss cho toàn bộ tập dữ liệu
        model.eval()
        all_losses = []
        loss_fn_none = nn.CrossEntropyLoss(reduction='none')
        
        loader_eval = DataLoader(dataset, batch_size=1024, shuffle=False)
        with torch.no_grad():
            for batch_x, batch_y in loader_eval:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                out = model(batch_x)
                losses = loss_fn_none(out, batch_y).cpu().numpy()
                all_losses.extend(losses)
                
        all_losses = np.array(all_losses)
        
        # 3. SVP chọn các mẫu có Loss cao nhất (điểm khó học nhất đối với proxy)
        idx_sorted = np.argsort(-all_losses)
        
        return idx_sorted[:target_n]
