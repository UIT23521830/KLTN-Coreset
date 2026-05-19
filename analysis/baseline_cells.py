# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session
---
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import LabelEncoder
import torch
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset, DataLoader
from torch.utils.data import Dataset
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    log_loss, roc_auc_score, roc_curve, auc
)
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)
import time
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
---
test_med_1 = pd.read_csv('/kaggle/input/moocs-dataset-process/test_med_1.csv')
test_med_2 = pd.read_csv('/kaggle/input/moocs-dataset-process/test_med_2.csv')
test_med_3 = pd.read_csv('/kaggle/input/moocs-dataset-process/test_med_3.csv')
test_med_4 = pd.read_csv('/kaggle/input/moocs-dataset-process/test_med_4.csv')

train_med = pd.read_csv('/kaggle/input/moocs-dataset-process/train_med.csv')
train_med_sas = pd.read_csv('/kaggle/input/moocs-dataset-process/train_sassmote_med.csv')
val_med_sas = pd.read_csv('/kaggle/input/moocs-dataset-process/val_med.csv')
---
META_COLS = [
    'user_id_enc',
    'course_id_enc',
    'school_id',
    'Rank',
    'type_of_rank',
    'teacher_id',
    'label_f'
]

def process_test(df, keep_phases):

    # ép kiểu phase
    df['phase'] = df['phase'].astype(int)

    # nếu keep_phases là scalar → chuyển thành list
    if not isinstance(keep_phases, (list, tuple, set)):
        keep_phases = [keep_phases]

    # các cột được bảo vệ (giữ nguyên)
    protected_cols = META_COLS + ['phase']

    # các cột còn lại sẽ bị điền -1
    other_cols = [c for c in df.columns if c not in protected_cols]

    # mask các phase ngoài keep_phases
    mask = ~df['phase'].isin(keep_phases)

    # điền -1 cho các cột KHÔNG protected
    df.loc[mask, other_cols] = -1

    return df.drop(columns = 'phase')

---
test_med_1 = process_test(test_med_1, keep_phases=[1])
test_med_2 = process_test(test_med_2, keep_phases=[1, 2])
test_med_3 = process_test(test_med_3, keep_phases=[1, 2, 3])
test_med_4 = process_test(test_med_4, keep_phases=[1, 2, 3, 4])
---
def split_chapter(df, col='chapter', max_level=3):
    parts = df[col].astype(str).str.split('.', expand=True)

    for i in range(max_level):
        df[f'{col}_{i+1}'] = (
            pd.to_numeric(parts[i], errors='coerce')
            .fillna(0)
            .astype(int)
        )

    df.drop(columns=[col], inplace=True)
    return df
---
train_med = split_chapter(train_med, 'chapter')
val_med_sas = split_chapter(val_med_sas, 'chapter')
---
# Giả sử X_train là tập train TRƯỚC khi smote để lấy danh sách cột
original_feature_names = train_med.drop(columns = 'label').columns.tolist() 

# Tạo dictionary: {0: 'Tuoi', 1: 'Thu_nhap', ...}
mapping = {i: col_name for i, col_name in enumerate(original_feature_names)}
---
mapping
---

# # Đổi tên các cột từ số sang chữ
# df_full = train_mean_cd.drop(columns = 'label')
---
# Đổi tên các cột từ số sang chữ
df_full = train_med_sas.drop(columns = 'label')
df_full.columns = original_feature_names
---
df_full = df_full.assign(label=train_med['label'])
---
df_full
---
test_med_1 = test_med_1[df_full.columns.tolist()]
test_med_2 = test_med_2[df_full.columns.tolist()]
test_med_3 = test_med_3[df_full.columns.tolist()]
test_med_4 = test_med_4[df_full.columns.tolist()]
---

label_mapping = {'excellent': 0, 'good': 1, 'average': 2}

class Final_Dataset_Deep(Dataset):
    def __init__(
        self,
        df,
        school_enc=None,
        teacher_enc=None,
        fit_encoder=False
    ):
        # Tạo bản sao để không ảnh hưởng đến dataframe gốc bên ngoài
        df = df.copy().drop_duplicates()

        # ===== 1. Xử lý Label =====
        # Giả sử cột label đầu vào tên là 'label'
        df = df.drop(columns = 'label')
        if df['label_f'].dtype == 'object':
            df['label_f'] = df['label_f'].map(label_mapping)

        # ===== 2. Encode school_id (Chỉ encode nếu là object) =====
        if 'school_id' in df.columns and school_enc is not None:
            if df['school_id'].dtype == 'object': # Kiểm tra nếu là object mới encode
                if fit_encoder:
                    df['school_id'] = school_enc.fit_transform(df['school_id'].astype(str))
                else:
                    df['school_id'] = df['school_id'].map(
                        lambda x: school_enc.transform([str(x)])[0]
                        if str(x) in school_enc.classes_ else -1
                    )

        # ===== 3. Encode teacher_id (Chỉ encode nếu là object) =====
        if 'teacher_id' in df.columns and teacher_enc is not None:
            if df['teacher_id'].dtype == 'object': # Kiểm tra nếu là object mới encode
                if fit_encoder:
                    df['teacher_id'] = teacher_enc.fit_transform(df['teacher_id'].astype(str))
                else:
                    df['teacher_id'] = df['teacher_id'].map(
                        lambda x: teacher_enc.transform([str(x)])[0]
                        if str(x) in teacher_enc.classes_ else -1
                    )

        # ===== 4. Ép tất cả cột (trừ label_f) sang numeric =====
        for col in df.columns:
            if col != 'label_f':
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # ===== 5. Xử lý giá trị trống (NaN) =====
        df = df.fillna(0)

        # ===== 6. Tạo tensor =====
        # Tách features và target
        y = df['label_f'].values.astype(np.int64)
        X = df.drop(columns=['label_f']).values.astype(np.float32)

        self.x = torch.tensor(X).unsqueeze(1)  # (N, 1, F) - Phù hợp cho CNN 1D hoặc RNN
        self.y = torch.tensor(y)

        self.n_samples = self.x.shape[0]
        self.num_features = self.x.shape[2]

    def __len__(self):
        return self.n_samples

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]


train_dataset = Final_Dataset_Deep(df_full)
val_dataset   = Final_Dataset_Deep(val_med_sas)
test_dataset_1 = Final_Dataset_Deep(test_med_1)
test_dataset_2 = Final_Dataset_Deep(test_med_2) # Nếu dùng chung df
test_dataset_3 = Final_Dataset_Deep(test_med_3)
test_dataset_4 = Final_Dataset_Deep(test_med_4)
---
# Lấy toàn bộ y_train dưới dạng tensor
y_train_tensor = train_dataset.y  

# Nếu cần numpy array để tính toán class weight, confusion matrix, v.v.
y_train = y_train_tensor.numpy()
---
# y_train đang là numpy array
df = pd.DataFrame(y_train, columns=["label_f"])
df.to_csv("y_train.csv", index=False)
---
criterion = nn.CrossEntropyLoss()
---
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader   = DataLoader(val_dataset, batch_size=32)
test_loader_1  = DataLoader(test_dataset_1, batch_size=32)
test_loader_2  = DataLoader(test_dataset_2, batch_size=32)
test_loader_3  = DataLoader(test_dataset_3, batch_size=32)
test_loader_4  = DataLoader(test_dataset_4, batch_size=32)
---
class SimpleLSTM(nn.Module):
    def __init__(self, input_size = None, hidden_size=128, num_layers=1, num_classes=3):
        super(SimpleLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size=input_size,
                            hidden_size=hidden_size,
                            num_layers=num_layers,
                            batch_first=True)
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out, _ = self.lstm(x)          # (batch, seq, hidden)
        out = out[:, -1, :]            # lấy timestep cuối
        out = self.fc(out)             # (batch, num_classes)
        return out
---
def train_LSTM(num_epochs=None, train_loader=None, valid_loader=None, test_loaders=None,
               criterion=None, device='cuda'):

    total_start = time.time()

    model = SimpleLSTM(
        input_size=train_dataset.num_features,
        hidden_size=128,
        num_classes=3
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # ================= TRAIN =================
    train_start = time.time()
    for epoch in range(num_epochs):
        model.train()
        total_loss, total_correct = 0, 0

        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * batch_X.size(0)
            total_correct += (outputs.argmax(1) == batch_y).sum().item()

        train_loss = total_loss / len(train_loader.dataset)
        train_acc  = total_correct / len(train_loader.dataset)

        # =============== VALID =================
        model.eval()
        val_loss, val_correct = 0, 0

        with torch.no_grad():
            for batch_X, batch_y in valid_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)

                val_loss += loss.item() * batch_X.size(0)
                val_correct += (outputs.argmax(1) == batch_y).sum().item()

        val_loss /= len(valid_loader.dataset)
        val_acc = val_correct / len(valid_loader.dataset)

        print(
            f"Epoch {epoch+1}/{num_epochs} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
        )

    train_time = time.time() - train_start
    print(f"\n⏱ Thời gian huấn luyện: {train_time:.2f} giây")

    # ================= TEST (N tập) =================
    model.eval()
    test_results = []

    for idx, test_loader in enumerate(test_loaders):
        print(f"\n========== TEST SET {idx+1} ==========")

        test_start = time.time()
        test_correct = 0
        y_pred, y_true, all_probs = [], [], []

        with torch.no_grad():
            for batch_X, batch_y in test_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)

                preds = torch.argmax(outputs, dim=1)
                probs = torch.softmax(outputs, dim=1)

                y_pred.extend(preds.cpu().numpy())
                y_true.extend(batch_y.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())

                test_correct += (preds == batch_y).sum().item()

        test_time = time.time() - test_start
        test_acc = test_correct / len(test_loader.dataset)

        print(f"Test Accuracy: {test_acc:.4f}")
        print("Classification Report:")
        print(classification_report(y_true, y_pred))

        cm = confusion_matrix(y_true, y_pred)

        test_results.append({
            "test_id": idx + 1,
            "accuracy": test_acc,
            "y_pred": y_pred,
            "y_true": y_true,
            "confusion_matrix": cm,
            "probs": all_probs,
            "test_time": test_time
        })

    total_time = time.time() - total_start
    print(f"\n⏱ Tổng thời gian (train + all tests): {total_time:.2f} giây")

    return model, test_results, train_time, total_time

---
test_loaders = [
    test_loader_1,
    test_loader_2,
    test_loader_3,
    test_loader_4
]

model, test_results, train_time, total_time = train_LSTM(
    num_epochs=50,
    train_loader=train_loader,
    valid_loader=val_loader,
    test_loaders=test_loaders,
    criterion=criterion,
    device='cuda'
)

---
def save_results_multi_tests(
    test_results,
    train_time,
    total_time,
    prefix= None
):
    """
    test_results: list dict (mỗi dict là 1 test set)
    prefix: tiền tố tên file (ví dụ dl_LSTM_V4)
    """

    os.makedirs(prefix, exist_ok=True)

    # ===== Lưu tổng thời gian train =====
    df_time = pd.DataFrame([{
        "train_time_sec": train_time,
        "total_time_sec": total_time
    }])
    df_time.to_csv(f"{prefix}/time_overall.csv", index=False)

    # ===== Lưu từng test =====
    for res in test_results:
        test_id = res["test_id"]

        y_true = np.array(res["y_true"])
        y_pred = np.array(res["y_pred"])
        cm = np.array(res["confusion_matrix"])
        all_probs = np.array(res["probs"])
        test_time = res["test_time"]
        acc = res["accuracy"]

        tag = f"{prefix}_test{test_id}"

        # ---- predictions ----
        df_pred = pd.DataFrame({
            "y_true": y_true,
            "y_pred": y_pred
        })
        df_pred.to_csv(f"{prefix}/{tag}_predictions.csv", index=False)

        # ---- confusion matrix ----
        df_cm = pd.DataFrame(cm)
        df_cm.to_csv(f"{prefix}/{tag}_confusion_matrix.csv", index=False)

        # ---- probabilities ----
        df_probs = pd.DataFrame(
            all_probs,
            columns=[f"class_{i}_prob" for i in range(all_probs.shape[1])]
        )
        df_probs.to_csv(f"{prefix}/{tag}_all_probs.csv", index=False)

        # ---- test time + acc ----
        df_test_time = pd.DataFrame([{
            "test_id": test_id,
            "test_time_sec": test_time,
            "accuracy": acc
        }])
        df_test_time.to_csv(f"{prefix}/{tag}_time.csv", index=False)


---
save_results_multi_tests(
    test_results=test_results,
    train_time=train_time,
    total_time=total_time,
    prefix="dl_LSTM_V6"
)

---
class SimpleGRU(nn.Module):
    def __init__(self, input_size = None, hidden_size=128, num_layers=1, num_classes=3):
        super(SimpleGRU, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.gru(x, h0)      # (batch, seq_len, hidden_size)
        out = out[:, -1, :]  # flatten (batch, seq_len*hidden_size)
        out = self.fc(out)
        return out
---
def train_GRU(num_epochs=None, train_loader=None, valid_loader=None, test_loaders=None,
               criterion=None, device='cuda'):

    total_start = time.time()

    model = SimpleGRU(
        input_size=train_dataset.num_features,
        hidden_size=128,
        num_classes=3
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # ================= TRAIN =================
    train_start = time.time()
    for epoch in range(num_epochs):
        model.train()
        total_loss, total_correct = 0, 0

        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * batch_X.size(0)
            total_correct += (outputs.argmax(1) == batch_y).sum().item()

        train_loss = total_loss / len(train_loader.dataset)
        train_acc  = total_correct / len(train_loader.dataset)

        # =============== VALID =================
        model.eval()
        val_loss, val_correct = 0, 0

        with torch.no_grad():
            for batch_X, batch_y in valid_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)

                val_loss += loss.item() * batch_X.size(0)
                val_correct += (outputs.argmax(1) == batch_y).sum().item()

        val_loss /= len(valid_loader.dataset)
        val_acc = val_correct / len(valid_loader.dataset)

        print(
            f"Epoch {epoch+1}/{num_epochs} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
        )

    train_time = time.time() - train_start
    print(f"\n⏱ Thời gian huấn luyện: {train_time:.2f} giây")

    # ================= TEST (N tập) =================
    model.eval()
    test_results = []

    for idx, test_loader in enumerate(test_loaders):
        print(f"\n========== TEST SET {idx+1} ==========")

        test_start = time.time()
        test_correct = 0
        y_pred, y_true, all_probs = [], [], []

        with torch.no_grad():
            for batch_X, batch_y in test_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)

                preds = torch.argmax(outputs, dim=1)
                probs = torch.softmax(outputs, dim=1)

                y_pred.extend(preds.cpu().numpy())
                y_true.extend(batch_y.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())

                test_correct += (preds == batch_y).sum().item()

        test_time = time.time() - test_start
        test_acc = test_correct / len(test_loader.dataset)

        print(f"Test Accuracy: {test_acc:.4f}")
        print("Classification Report:")
        print(classification_report(y_true, y_pred))

        cm = confusion_matrix(y_true, y_pred)

        test_results.append({
            "test_id": idx + 1,
            "accuracy": test_acc,
            "y_pred": y_pred,
            "y_true": y_true,
            "confusion_matrix": cm,
            "probs": all_probs,
            "test_time": test_time
        })

    total_time = time.time() - total_start
    print(f"\n⏱ Tổng thời gian (train + all tests): {total_time:.2f} giây")

    return model, test_results, train_time, total_time

---
model_GRU, test_results_GRU, train_time_GRU, total_time_GRU = train_GRU(
    num_epochs=50,
    train_loader=train_loader,
    valid_loader=val_loader,
    test_loaders=test_loaders,
    criterion=criterion,
    device='cuda'
)

---
save_results_multi_tests(
    test_results=test_results_GRU,
    train_time=train_time_GRU,
    total_time=total_time_GRU,
    prefix="dl_GRU_V6"
)

---
class SimpleRNN(nn.Module):
    def __init__(self, input_size = None, hidden_size=256, num_layers=1, num_classes=3):
        super(SimpleRNN, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # RNN cơ bản
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True, nonlinearity='tanh')
        self.dropout = nn.Dropout(0.5)
        
        # fully-connected để phân loại
        self.fc1 = nn.Linear(hidden_size, num_classes)
        
    def forward(self, x):
        # hidden state ban đầu
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size, device=x.device)
        
        # out: [batch, seq_len, hidden_size]
        out, _ = self.rnn(x, h0)
        
        # lấy hidden state ở time-step cuối
        out = out[:, -1, :]   # [batch, hidden_size]
        
        # fully-connected
        out = self.fc1(out)   # [batch, num_classes]
        return out

---
def train_RNN(num_epochs=None, train_loader=None, valid_loader=None, test_loaders=None,
               criterion=None, device='cuda'):

    total_start = time.time()

    model = SimpleRNN(
        input_size=train_dataset.num_features,
        hidden_size=128,
        num_classes=3
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # ================= TRAIN =================
    train_start = time.time()
    for epoch in range(num_epochs):
        model.train()
        total_loss, total_correct = 0, 0

        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * batch_X.size(0)
            total_correct += (outputs.argmax(1) == batch_y).sum().item()

        train_loss = total_loss / len(train_loader.dataset)
        train_acc  = total_correct / len(train_loader.dataset)

        # =============== VALID =================
        model.eval()
        val_loss, val_correct = 0, 0

        with torch.no_grad():
            for batch_X, batch_y in valid_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)

                val_loss += loss.item() * batch_X.size(0)
                val_correct += (outputs.argmax(1) == batch_y).sum().item()

        val_loss /= len(valid_loader.dataset)
        val_acc = val_correct / len(valid_loader.dataset)

        print(
            f"Epoch {epoch+1}/{num_epochs} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
        )

    train_time = time.time() - train_start
    print(f"\n⏱ Thời gian huấn luyện: {train_time:.2f} giây")

    # ================= TEST (N tập) =================
    model.eval()
    test_results = []

    for idx, test_loader in enumerate(test_loaders):
        print(f"\n========== TEST SET {idx+1} ==========")

        test_start = time.time()
        test_correct = 0
        y_pred, y_true, all_probs = [], [], []

        with torch.no_grad():
            for batch_X, batch_y in test_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)

                preds = torch.argmax(outputs, dim=1)
                probs = torch.softmax(outputs, dim=1)

                y_pred.extend(preds.cpu().numpy())
                y_true.extend(batch_y.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())

                test_correct += (preds == batch_y).sum().item()

        test_time = time.time() - test_start
        test_acc = test_correct / len(test_loader.dataset)

        print(f"Test Accuracy: {test_acc:.4f}")
        print("Classification Report:")
        print(classification_report(y_true, y_pred))

        cm = confusion_matrix(y_true, y_pred)

        test_results.append({
            "test_id": idx + 1,
            "accuracy": test_acc,
            "y_pred": y_pred,
            "y_true": y_true,
            "confusion_matrix": cm,
            "probs": all_probs,
            "test_time": test_time
        })

    total_time = time.time() - total_start
    print(f"\n⏱ Tổng thời gian (train + all tests): {total_time:.2f} giây")

    return model, test_results, train_time, total_time

---
model_RNN, test_results_RNN, train_time_RNN, total_time_RNN = train_RNN(
    num_epochs=50,
    train_loader=train_loader,
    valid_loader=val_loader,
    test_loaders=test_loaders,
    criterion=criterion,
    device='cuda'
)

---
save_results_multi_tests(
    test_results=test_results_RNN,
    train_time=train_time_RNN,
    total_time=total_time_RNN,
    prefix="dl_RNN_V6"
)

---
class BiLSTM(nn.Module):
    def __init__(self, input_size=None, hidden_size=256, num_layers=1, num_classes=3):
        super(BiLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # BiLSTM (bidirectional=True)
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(0.5)
        
        # fully-connected: hidden_size * 2 (do bidirectional)
        self.fc1 = nn.Linear(hidden_size * 2, num_classes)
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # hidden state + cell state ban đầu
        h0 = torch.zeros(self.num_layers * 2, batch_size, self.hidden_size, device=x.device)  # ×2 vì BiLSTM
        c0 = torch.zeros(self.num_layers * 2, batch_size, self.hidden_size, device=x.device)
        
        # out: [batch, seq_len, hidden_size*2]
        out, _ = self.lstm(x, (h0, c0))
        
        # lấy hidden state ở timestep cuối
        out = out[:, -1, :]   # [batch, hidden_size*2]
        
        out = self.dropout(out)
        out = self.fc1(out)   # [batch, num_classes]
        return out
---
def train_BiLSTM(num_epochs=None, train_loader=None, valid_loader=None, test_loaders=None,
               criterion=None, device='cuda'):

    total_start = time.time()

    model = BiLSTM(
        input_size=train_dataset.num_features,
        hidden_size=128,
        num_classes=3
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # ================= TRAIN =================
    train_start = time.time()
    for epoch in range(num_epochs):
        model.train()
        total_loss, total_correct = 0, 0

        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * batch_X.size(0)
            total_correct += (outputs.argmax(1) == batch_y).sum().item()

        train_loss = total_loss / len(train_loader.dataset)
        train_acc  = total_correct / len(train_loader.dataset)

        # =============== VALID =================
        model.eval()
        val_loss, val_correct = 0, 0

        with torch.no_grad():
            for batch_X, batch_y in valid_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)

                val_loss += loss.item() * batch_X.size(0)
                val_correct += (outputs.argmax(1) == batch_y).sum().item()

        val_loss /= len(valid_loader.dataset)
        val_acc = val_correct / len(valid_loader.dataset)
        print(
            f"Epoch {epoch+1}/{num_epochs} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
        )

    train_time = time.time() - train_start
    print(f"\n⏱ Thời gian huấn luyện: {train_time:.2f} giây")

    # ================= TEST (N tập) =================
    model.eval()
    test_results = []

    for idx, test_loader in enumerate(test_loaders):
        print(f"\n========== TEST SET {idx+1} ==========")

        test_start = time.time()
        test_correct = 0
        y_pred, y_true, all_probs = [], [], []

        with torch.no_grad():
            for batch_X, batch_y in test_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)

                preds = torch.argmax(outputs, dim=1)
                probs = torch.softmax(outputs, dim=1)

                y_pred.extend(preds.cpu().numpy())
                y_true.extend(batch_y.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())

                test_correct += (preds == batch_y).sum().item()

        test_time = time.time() - test_start
        test_acc = test_correct / len(test_loader.dataset)

        print(f"Test Accuracy: {test_acc:.4f}")
        print("Classification Report:")
        print(classification_report(y_true, y_pred))

        cm = confusion_matrix(y_true, y_pred)

        test_results.append({
            "test_id": idx + 1,
            "accuracy": test_acc,
            "y_pred": y_pred,
            "y_true": y_true,
            "confusion_matrix": cm,
            "probs": all_probs,
            "test_time": test_time
        })

    total_time = time.time() - total_start
    print(f"\n⏱ Tổng thời gian (train + all tests): {total_time:.2f} giây")

    return model, test_results, train_time, total_time

---
model_BiLSTM, test_results_BiLSTM, train_time_BiLSTM, total_time_BiLSTM = train_BiLSTM(
    num_epochs=50,
    train_loader=train_loader,
    valid_loader=val_loader,
    test_loaders=test_loaders,
    criterion=criterion,
    device='cuda'
)

save_results_multi_tests(
    test_results=test_results_BiLSTM,
    train_time=train_time_BiLSTM,
    total_time=total_time_BiLSTM,
    prefix="dl_BiLSTM_V6"
)
