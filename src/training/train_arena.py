import os
import time
import json
import glob
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, precision_score, 
                             recall_score, f1_score, roc_auc_score, matthews_corrcoef, cohen_kappa_score)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

try:
    from imblearn.metrics import geometric_mean_score
    HAS_IMBLEARN = True
except ImportError:
    HAS_IMBLEARN = False

# Thử import LightGBM
try:
    from lightgbm import LGBMClassifier
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

# Thử import CatBoost
try:
    from catboost import CatBoostClassifier
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False

# Thử import TabNet
try:
    from pytorch_tabnet.tab_model import TabNetClassifier
    HAS_TABNET = True
except ImportError:
    HAS_TABNET = False

# Thử import TabPFN (SOTA Foundation Model cho Tabular 2023)
try:
    from tabpfn import TabPFNClassifier
    HAS_TABPFN = True
except ImportError:
    HAS_TABPFN = False

class TrainingArena:
    """
    Đấu trường Huấn luyện (Giai đoạn 3).
    Huấn luyện và xuất 20+ chỉ số đo lường ra file JSON thô.
    """
    def __init__(self, processed_dir="processed", coresets_dir="coresets", results_dir="results"):
        self.processed_dir = processed_dir
        self.coresets_dir = coresets_dir
        self.results_dir = results_dir
        self.raw_metrics_dir = os.path.join(self.results_dir, "raw_metrics")
        self.checkpoints_dir = os.path.join(self.results_dir, "checkpoints")
        
        os.makedirs(self.raw_metrics_dir, exist_ok=True)
        os.makedirs(self.checkpoints_dir, exist_ok=True)
            
        # Khởi tạo mô hình giám khảo (Evaluators)
        self.models = {
            "LR": LogisticRegression(max_iter=1000, random_state=42),
            "SVM": LinearSVC(random_state=42, dual=False),
            "RF": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
            "XGB": XGBClassifier(n_estimators=100, max_depth=6, random_state=42, use_label_encoder=False, eval_metric="logloss"),
            "HGB": HistGradientBoostingClassifier(max_iter=100, random_state=42),
            "MLP": MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42), # Thêm DL Baseline
            "KNN": KNeighborsClassifier(n_neighbors=5, n_jobs=-1),
            "NB": GaussianNB()
        }
        if HAS_LIGHTGBM:
            self.models["LGBM"] = LGBMClassifier(n_estimators=100, max_depth=6, random_state=42, verbose=-1)
        if HAS_CATBOOST:
            self.models["CAT"] = CatBoostClassifier(iterations=100, depth=6, random_seed=42, verbose=0)
        if HAS_TABNET:
            self.models["TABNET"] = TabNetClassifier(verbose=0, seed=42)
        if HAS_TABPFN:
            self.models["TABPFN"] = TabPFNClassifier()

    def save_raw_metrics(self, dataset, method, budget, seed, model_name, phase, metrics):
        # Save as JSON
        filename = f"{dataset}_{method}_{budget}_seed{seed}_{model_name}_phase{phase}.json"
        filepath = os.path.join(self.raw_metrics_dir, filename)
        
        data = {
            "Dataset": dataset,
            "Method": method,
            "Budget": budget,
            "Seed": seed,
            "Model": model_name,
            "Phase": phase,
            "Metrics": metrics
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def evaluate_model_already_fitted(self, model, t_train, X_test, y_test):
        if model.__class__.__name__ == "TabNetClassifier":
            X_test_eval = X_test.astype(np.float32)
        else:
            X_test_eval = X_test
        
        t1 = time.time()
        y_pred = model.predict(X_test_eval)
        t_predict = time.time() - t1
        
        # Toàn cục
        acc = accuracy_score(y_test, y_pred)
        bal_acc = balanced_accuracy_score(y_test, y_pred)
        
        prec_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
        prec_weight = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        
        rec_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
        rec_weight = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
        f1_weight = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        mcc = matthews_corrcoef(y_test, y_pred)
        kappa = cohen_kappa_score(y_test, y_pred)
        
        gmean = geometric_mean_score(y_test, y_pred) if HAS_IMBLEARN else 0.0
        
        # Per-class
        prec_class = precision_score(y_test, y_pred, average=None, zero_division=0)
        rec_class = recall_score(y_test, y_pred, average=None, zero_division=0)
        f1_class = f1_score(y_test, y_pred, average=None, zero_division=0)
        
        # Tạm lưu per-class theo list
        metrics = {
            "Train_Time": t_train,
            "Predict_Time": t_predict,
            "Accuracy": acc,
            "BalancedAcc": bal_acc,
            "Precision_Macro": prec_macro,
            "Precision_Weighted": prec_weight,
            "Recall_Macro": rec_macro,
            "Recall_Weighted": rec_weight,
            "F1_Macro": f1_macro,
            "F1_Weighted": f1_weight,
            "GMean": gmean,
            "MCC": mcc,
            "Kappa": kappa,
            "PerClass_Precision": prec_class.tolist(),
            "PerClass_Recall": rec_class.tolist(),
            "PerClass_F1": f1_class.tolist()
        }
        return metrics

    def run_arena(self, dataset_name="CourseQuality"):
        print("="*60)
        print(f"⚔️ TRAINING ARENA - DATASET: {dataset_name}")
        print("="*60)
        
        data_path = os.path.join(self.processed_dir, dataset_name)
        
        print("[+] Đang tải các tập Test (Phases)...")
        test_phases = []
        phase = 1
        while True:
            xt_path = os.path.join(data_path, f"X_test_{phase}.npy")
            yt_path = os.path.join(data_path, f"y_test_{phase}.npy")
            if os.path.exists(xt_path) and os.path.exists(yt_path):
                test_phases.append({
                    'phase': str(phase),
                    'X': np.load(xt_path),
                    'y': np.load(yt_path)
                })
                print(f"    - Phase {phase} loaded: {test_phases[-1]['X'].shape[0]} samples")
                phase += 1
            else:
                break
                
        # Nếu không có X_test_1, fallback về X_test gốc
        if len(test_phases) == 0:
            test_phases.append({
                'phase': 'all',
                'X': np.load(os.path.join(data_path, "X_test.npy")),
                'y': np.load(os.path.join(data_path, "y_test.npy"))
            })
            print("    - Single test set loaded.")
        
        print("\n[+] Đang huấn luyện Baseline (Ngân sách 100%)...")
        X_train_full = np.load(os.path.join(data_path, "X_train.npy"))
        y_train_full = np.load(os.path.join(data_path, "y_train.npy"))
        
        for model_name, model in self.models.items():
            # Huấn luyện 1 lần
            t0 = time.time()
            if model.__class__.__name__ == "TabNetClassifier":
                model.fit(X_train_full.astype(np.float32), y_train_full, eval_metric=['auc'])
            else:
                model.fit(X_train_full, y_train_full)
            t_train = time.time() - t0
            
            # Đánh giá trên nhiều tập Test
            for tp in test_phases:
                metrics = self.evaluate_model_already_fitted(model, t_train, tp['X'], tp['y'])
                print(f"    - Baseline {model_name} (Phase {tp['phase']}): Acc={metrics['Accuracy']:.4f} | F1={metrics['F1_Macro']:.4f}")
                self.save_raw_metrics(dataset_name, "Baseline", "100pct", "NA", model_name, tp['phase'], metrics)

        dataset_coresets_path = os.path.join(self.coresets_dir)
        if not os.path.exists(dataset_coresets_path):
            print(f"[-] Không tìm thấy thư mục {dataset_coresets_path}. Bạn đã chạy Giai đoạn 2 chưa?")
            return
            
        print("\n[+] Bắt đầu chấm điểm các phương pháp SOTA...")
        search_pattern = os.path.join(self.coresets_dir, "*", dataset_name, "budget_*pct", "seed_*.csv")
        all_csv_files = glob.glob(search_pattern)
        
        if len(all_csv_files) == 0:
            print("[-] Không có file CSV nào để đánh giá!")
            return
            
        for csv_file in all_csv_files:
            parts = os.path.normpath(csv_file).split(os.sep)
            method = parts[-4]
            budget = parts[-2].replace('budget_', '')
            seed = parts[-1].replace('seed_', '').replace('.csv', '')
            
            try:
                df = pd.read_csv(csv_file)
                if 'Error' in df.columns and df['Error'].iloc[0] == 'OOM':
                    for model_name in self.models.keys():
                        self.save_raw_metrics(dataset_name, method, budget, seed, model_name, {"Error": "OOM"})
                    continue
                
                y_c = df['target'].values
                X_c = df.drop(columns=['target']).values
                
                for model_name, model in self.models.items():
                    # Huấn luyện 1 lần
                    t0 = time.time()
                    if model.__class__.__name__ == "TabNetClassifier":
                        model.fit(X_c.astype(np.float32), y_c, eval_metric=['auc'])
                    else:
                        model.fit(X_c, y_c)
                    t_train = time.time() - t0
                    
                    # Lưu Checkpoint mô hình
                    ckpt_name = f"{dataset_name}_{method}_{budget}_seed{seed}_{model_name}.pkl"
                    joblib.dump(model, os.path.join(self.checkpoints_dir, ckpt_name))
                    
                    # Đánh giá trên nhiều tập test
                    for tp in test_phases:
                        metrics = self.evaluate_model_already_fitted(model, t_train, tp['X'], tp['y'])
                        self.save_raw_metrics(dataset_name, method, budget, seed, model_name, tp['phase'], metrics)
                    
            except Exception as e:
                print(f"[ERROR] Lỗi file {csv_file}: {e}")
                
        print(f"\n✅ Hoàn tất! Dữ liệu thô lưu tại: {self.raw_metrics_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', type=str, default='ALL', help='Comma-separated list of models to run (e.g. XGB,RF,MLP)')
    args = parser.parse_args()
    
    arena = TrainingArena()
    if args.models != 'ALL':
        allowed = args.models.split(',')
        arena.models = {k: v for k, v in arena.models.items() if k in allowed}
        print(f"[*] Đang chạy phân tán với các mô hình: {list(arena.models.keys())}")
        
    arena.run_arena()
