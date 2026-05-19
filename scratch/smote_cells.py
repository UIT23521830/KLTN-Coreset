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
!pip install -U scikit-learn==1.4.2 imbalanced-learn==0.12.2

---
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from imblearn.over_sampling import SMOTE

plt.rcParams["figure.figsize"] = (6, 4)

---
# =========================
# 2. Hàm vẽ biểu đồ + thống kê nhãn
# =========================
def describe_and_plot_labels(df, target_col: str, title_prefix: str):
    counts = df[target_col].value_counts().sort_index()
    
    print(f"\n=== {title_prefix} – thống kê nhãn ({target_col}) ===")
    print(counts)
    print("Tổng số mẫu:", counts.sum())
    
    if counts.min() > 0 and len(counts) > 1:
        maj = counts.max()
        mino = counts.min()
        print(f"Imbalance ratio (majority/minority): {maj/mino:.2f}")
    
    plt.figure()
    counts.plot(kind="bar")
    plt.title(f"{title_prefix} – phân bố nhãn")
    plt.xlabel("Label")
    plt.ylabel("Số mẫu")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()

---
# =========================
# 3. Hàm CDSMOTE cho multi-class (5 nhãn)
# =========================
def cdsmote_resample_multiclass(
    df: pd.DataFrame,
    feature_cols,
    target_col: str,
    k_clusters: int = 2,
    k_neighbors: int = 4,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    CDSMOTE cho bài toán multi-class (ví dụ 5 nhãn).
    Làm lần lượt one-vs-rest cho từng lớp thiểu số.
    """
    df = df.copy()
    X = df[feature_cols].values
    y = df[target_col].values

    classes, counts = np.unique(y, return_counts=True)
    class_counts = dict(zip(classes, counts))
    max_count = counts.max()

    print("=== CDSMOTE multi-class ===")
    print("Phân bố nhãn ban đầu:", class_counts)
    print("Max count (majority lớn nhất):", max_count)

    new_samples_per_class = []

    for cls in classes:
        n_cls = class_counts[cls]
        print(f"\n--- Xử lý class = {cls} ---")
        print(f"  - Số mẫu class {cls}: {n_cls}")

        # Bỏ qua class majority hoặc quá ít mẫu
        if n_cls >= max_count:
            print("  -> Đây là majority (hoặc gần bằng majority), bỏ qua oversampling.")
            continue
        if n_cls < 2:
            print("  -> Số mẫu < 2, không thể chạy SMOTE, bỏ qua.")
            continue

        # Minority = cls, Majority = các lớp khác
        idx_min = np.where(y == cls)[0]
        idx_maj = np.where(y != cls)[0]

        X_min = X[idx_min]
        X_maj = X[idx_maj]

        print(f"  - Số mẫu majority (y != {cls}): {X_maj.shape[0]}")

        # Không đủ majority để KMeans
        if X_maj.shape[0] < k_clusters:
            print("  -> Majority quá ít để KMeans, bỏ qua CDSMOTE cho class này.")
            continue

        # Decompose majority bằng KMeans
        kmeans = KMeans(
            n_clusters=k_clusters,
            random_state=random_state,
            n_init=10
        )
        maj_clusters = kmeans.fit_predict(X_maj)

        cluster_counts = np.bincount(maj_clusters, minlength=k_clusters)
        mean_maj = cluster_counts.mean()

        print(f"  - Số mẫu từng subclass majority: {cluster_counts.tolist()}")
        print(f"  - Mean size các subclass majority: {mean_maj:.2f}")

        # Nếu minority >= mean_maj thì không cần oversample class này
        if n_cls >= mean_maj:
            print("  -> Số mẫu class này >= mean_maj, không oversample.")
            continue

        # Chọn subclass gần mean nhất
        closest_cluster = np.argmin(np.abs(cluster_counts - mean_maj))
        print(f"  - Chọn subclass majority gần mean nhất: cluster {closest_cluster}")

        idx_maj_cluster = idx_maj[maj_clusters == closest_cluster]

        # SMOTE one-vs-rest:
        #  minority = 1, majority = 0
        X_smote = np.vstack([X_min, X[idx_maj_cluster]])
        y_smote = np.concatenate([
            np.ones(len(X_min), dtype=int),
            np.zeros(len(idx_maj_cluster), dtype=int),
        ])

        # Mục tiêu: class cls sau SMOTE ≈ mean_maj
        target_minority = int(round(mean_maj))
        print(f"  - Mục tiêu sau SMOTE: {target_minority} mẫu cho class {cls}")

        # Điều chỉnh k_neighbors cho hợp lệ
        k_eff = min(k_neighbors, len(X_min) - 1)
        if k_eff < 1:
            print("  -> Không đủ hàng xóm để SMOTE, bỏ qua.")
            continue

        smote = SMOTE(
            sampling_strategy={1: target_minority},
            k_neighbors=k_eff,
            random_state=random_state,
        )

        X_res, y_res = smote.fit_resample(X_smote, y_smote)

        # Lấy mẫu minority synthetic mới (label 1 trong y_res)
        n_minority_after = (y_res == 1).sum()
        n_new = n_minority_after - n_cls
        print(f"  - Số mẫu minority mới sinh thêm cho class {cls}: {n_new}")

        if n_new <= 0:
            print("  -> SMOTE không sinh thêm mẫu, bỏ qua.")
            continue

        idx_minority_res = np.where(y_res == 1)[0]
        idx_new = idx_minority_res[-n_new:]
        X_new = X_res[idx_new]

        df_new_cls = pd.DataFrame(X_new, columns=feature_cols)
        df_new_cls[target_col] = cls

        new_samples_per_class.append(df_new_cls)
         # Ghép tất cả sample mới vào dataset gốc
    if len(new_samples_per_class) > 0:
        df_aug = pd.concat(
            [df[feature_cols + [target_col]]] + new_samples_per_class,
            axis=0,
            ignore_index=True
        )
        print(f"\n=== Hoàn thành CDSMOTE multi-class ===")
        print(f"  - Shape trước: {df.shape}")
        print(f"  - Shape sau:   {df_aug.shape}")
    else:
        print("\n=== Không sinh thêm sample nào, trả về dữ liệu gốc ===")
        df_aug = df[feature_cols + [target_col]].copy()

    # In lại phân bố nhãn sau oversampling
    classes_after, counts_after = np.unique(df_aug[target_col].values, return_counts=True)
    print("Phân bố nhãn sau CDSMOTE:")
    print(dict(zip(classes_after, counts_after)))

    return df_aug

---
BASE_DIR = "/kaggle/input/mooccubex-data-cleaned/Train_val_test_split/corr_data"
LABEL_COL = "label_5_encoder"   # cột nhãn 5 lớp đã encode

phase1_path = os.path.join(BASE_DIR, "Phase_1", "train.csv")
df_phase1 = pd.read_csv(phase1_path)

print("Phase_1 – shape gốc:", df_phase1.shape)
print("Các cột trong file:")
print(df_phase1.columns.tolist())

# Chọn feature: TẤT CẢ cột numeric trừ cột nhãn
feature_cols_phase1 = [
    c for c in df_phase1.columns
    if c != LABEL_COL and pd.api.types.is_numeric_dtype(df_phase1[c])
]
print("Số feature dùng cho CDSMOTE (Phase_1):", len(feature_cols_phase1))

---
describe_and_plot_labels(
    df_phase1,
    target_col=LABEL_COL,
    title_prefix="Phase_1 (trước CDSMOTE)"
)

---
df_phase1_cd = cdsmote_resample_multiclass(
    df=df_phase1,
    feature_cols=feature_cols_phase1,
    target_col=LABEL_COL,
    k_clusters=2,
    k_neighbors=4,
    random_state=42,
)

print("Phase_1 – shape sau CDSMOTE:", df_phase1_cd.shape)

---
describe_and_plot_labels(
    df_phase1_cd,
    target_col=LABEL_COL,
    title_prefix="Phase_1 (sau CDSMOTE)"
)

---
out_dir = "/kaggle/working/cdsmote_trains"
os.makedirs(out_dir, exist_ok=True)

out_path1 = os.path.join(out_dir, "Phase_1_train_cdsmote.csv")
df_phase1_cd.to_csv(out_path1, index=False)

print("Đã lưu Phase_1 sau CDSMOTE tại:", out_path1)

---
BASE_DIR = "/kaggle/input/mooccubex-data-cleaned/Train_val_test_split/corr_data"
LABEL_COL = "label_5_encoder"   # cột nhãn 5 lớp đã encode

phase1_path = os.path.join(BASE_DIR, "Phase_2", "train.csv")
df_phase1 = pd.read_csv(phase1_path)

print("Phase_2 – shape gốc:", df_phase1.shape)
print("Các cột trong file:")
print(df_phase1.columns.tolist())

# Chọn feature: TẤT CẢ cột numeric trừ cột nhãn
feature_cols_phase1 = [
    c for c in df_phase1.columns
    if c != LABEL_COL and pd.api.types.is_numeric_dtype(df_phase1[c])
]
print("Số feature dùng cho CDSMOTE (Phase_2):", len(feature_cols_phase1))

---
describe_and_plot_labels(
    df_phase1,
    target_col=LABEL_COL,
    title_prefix="Phase_2 (trước CDSMOTE)"
)

---
df_phase1_cd = cdsmote_resample_multiclass(
    df=df_phase1,
    feature_cols=feature_cols_phase1,
    target_col=LABEL_COL,
    k_clusters=2,
    k_neighbors=4,
    random_state=42,
)

print("Phase_2 – shape sau CDSMOTE:", df_phase1_cd.shape)

---
df_phase1_cd = cdsmote_resample_multiclass(
    df=df_phase1,
    feature_cols=feature_cols_phase1,
    target_col=LABEL_COL,
    k_clusters=2,
    k_neighbors=4,
    random_state=42,
)

print("Phase_2 – shape sau CDSMOTE:", df_phase1_cd.shape)

---
describe_and_plot_labels(
    df_phase1_cd,
    target_col=LABEL_COL,
    title_prefix="Phase_2 (sau CDSMOTE)"
)

---
out_dir = "/kaggle/working/cdsmote_trains"
os.makedirs(out_dir, exist_ok=True)

out_path1 = os.path.join(out_dir, "Phase_2_train_cdsmote.csv")
df_phase1_cd.to_csv(out_path1, index=False)

print("Đã lưu Phase_2 sau CDSMOTE tại:", out_path1)

---
BASE_DIR = "/kaggle/input/mooccubex-data-cleaned/Train_val_test_split/corr_data"
LABEL_COL = "label_5_encoder"   # cột nhãn 5 lớp đã encode

phase3_path = os.path.join(BASE_DIR, "Phase_3", "train.csv")
df_phase3 = pd.read_csv(phase3_path)

print("Phase_3 – shape gốc:", df_phase3.shape)
print("Các cột trong file:")
print(df_phase3.columns.tolist())

# Chọn feature: TẤT CẢ cột numeric trừ cột nhãn
feature_cols_phase3 = [
    c for c in df_phase3.columns
    if c != LABEL_COL and pd.api.types.is_numeric_dtype(df_phase3[c])
]
print("Số feature dùng cho CDSMOTE (Phase_3):", len(feature_cols_phase3))

---
describe_and_plot_labels(
    df_phase3,
    target_col=LABEL_COL,
    title_prefix="Phase_3 (trước CDSMOTE)"
)

---
df_phase3_cd = cdsmote_resample_multiclass(
    df=df_phase3,
    feature_cols=feature_cols_phase3,
    target_col=LABEL_COL,
    k_clusters=2,
    k_neighbors=4,
    random_state=42,
)

print("Phase_3 – shape sau CDSMOTE:", df_phase3_cd.shape)

---
describe_and_plot_labels(
    df_phase3_cd,
    target_col=LABEL_COL,
    title_prefix="Phase_3 (sau CDSMOTE)"
)

---
out_dir = "/kaggle/working/cdsmote_trains"
os.makedirs(out_dir, exist_ok=True)

out_path3 = os.path.join(out_dir, "Phase_3_train_cdsmote.csv")
df_phase3_cd.to_csv(out_path3, index=False)

print("Đã lưu Phase_3 sau CDSMOTE tại:", out_path3)

---
BASE_DIR = "/kaggle/input/mooccubex-data-cleaned/Train_val_test_split/corr_data"
LABEL_COL = "label_5_encoder"

phase4_path = os.path.join(BASE_DIR, "Phase_4", "train.csv")
df_phase4 = pd.read_csv(phase4_path)

print("Phase_4 – shape gốc:", df_phase4.shape)
print("Các cột trong file:")
print(df_phase4.columns.tolist())

feature_cols_phase4 = [
    c for c in df_phase4.columns
    if c != LABEL_COL and pd.api.types.is_numeric_dtype(df_phase4[c])
]
print("Số feature dùng cho CDSMOTE (Phase_4):", len(feature_cols_phase4))

---
describe_and_plot_labels(
    df_phase4,
    target_col=LABEL_COL,
    title_prefix="Phase_4 (trước CDSMOTE)"
)

---
df_phase4_cd = cdsmote_resample_multiclass(
    df=df_phase4,
    feature_cols=feature_cols_phase4,
    target_col=LABEL_COL,
    k_clusters=2,
    k_neighbors=4,
    random_state=42,
)

print("Phase_4 – shape sau CDSMOTE:", df_phase4_cd.shape)

---
describe_and_plot_labels(
    df_phase4_cd,
    target_col=LABEL_COL,
    title_prefix="Phase_4 (sau CDSMOTE)"
)

---
out_dir = "/kaggle/working/cdsmote_trains"
os.makedirs(out_dir, exist_ok=True)

out_path4 = os.path.join(out_dir, "Phase_4_train_cdsmote.csv")
df_phase4_cd.to_csv(out_path4, index=False)

print("Đã lưu Phase_4 sau CDSMOTE tại:", out_path4)
