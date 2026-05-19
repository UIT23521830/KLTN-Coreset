import os
import json
import time
import numpy as np
import pandas as pd
from src.coreset.methods import METHOD_REGISTRY

class CoresetFactory:
    """
    Nhà máy trung tâm điều phối quá trình nén dữ liệu (Giai đoạn 2).
    Đã được tối ưu x4 tốc độ bằng kỹ thuật List Slicing.
    """
    def __init__(self, processed_dir="processed", out_dir="coresets", log_file="factory_execution_log.csv"):
        self.processed_dir = processed_dir
        self.out_dir = out_dir
        self.log_file = log_file
        
        # Tạo file log nếu chưa có
        if not os.path.exists(self.log_file):
            pd.DataFrame(columns=["Method", "Seed", "Budget", "Core_Time_Sec", "Search_Time_Sec", "Total_Time_Sec", "Status"]).to_csv(self.log_file, index=False)
            
    def log_time(self, method, seed, budget, core_time, search_time, total_time, status):
        df = pd.DataFrame([{
            "Method": method, 
            "Seed": seed, 
            "Budget": budget,
            "Core_Time_Sec": round(core_time, 4), 
            "Search_Time_Sec": round(search_time, 4),
            "Total_Time_Sec": round(total_time, 4),
            "Status": status
        }])
        df.to_csv(self.log_file, mode='a', header=False, index=False)

    def run_experiment(self, dataset_name, budgets=[0.01, 0.05, 0.10, 0.20], n_seeds=10, methods=None):
        print("="*60)
        print(f"🏭 CORESET FACTORY - DATASET: {dataset_name} (KAGGLE OPTIMIZED)")
        print("="*60)
        
        data_path = os.path.join(self.processed_dir, dataset_name)
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Không tìm thấy thư mục {data_path}")
            
        print("[+] Đang tải ma trận Numpy...")
        X_train = np.load(os.path.join(data_path, "X_train.npy"))
        y_train = np.load(os.path.join(data_path, "y_train.npy"))
        
        with open(os.path.join(data_path, "metadata.json"), 'r', encoding='utf-8') as f:
            meta = json.load(f)
        feature_names = meta.get("feature_names", [f"F_{i}" for i in range(X_train.shape[1])])
        
        total_samples = len(X_train)
        print(f"    - Original Shape: {X_train.shape}")
        
        if methods is None:
            methods = list(METHOD_REGISTRY.keys())
            
        max_budget = max(budgets)
            
        for method_name in methods:
            print(f"\n🚀 Đang chạy phương pháp: {method_name}")
            
            SelectorClass = METHOD_REGISTRY[method_name]
            
            for seed in range(n_seeds):
                print(f"   ➔ Seed {seed}: ", end="", flush=True)
                t0 = time.time()
                
                try:
                    selector = SelectorClass(random_seed=seed)
                    
                    if method_name == "M03_CoreTab":
                        # M03_CoreTab không hỗ trợ Slicing do cơ chế cây quyết định tĩnh
                        for budget in budgets:
                            selected_idx = selector.select(X_train, y_train, budget)
                            budget_str = f"budget_{int(budget*100):02d}pct"
                            
                            c_time = getattr(selector, 'last_core_time', 0.0)
                            s_time = getattr(selector, 'last_search_time', 0.0)
                            self.log_time(method_name, seed, budget, c_time, s_time, c_time + s_time, "Success")
                            
                            save_dir = os.path.join(self.out_dir, method_name, dataset_name, budget_str)
                            os.makedirs(save_dir, exist_ok=True)
                            
                            X_subset = X_train[selected_idx]
                            y_subset = y_train[selected_idx]
                            
                            df = pd.DataFrame(X_subset, columns=feature_names)
                            df['target'] = y_subset
                            save_path = os.path.join(save_dir, f"seed_{seed}.csv")
                            df.to_csv(save_path, index=False)
                    else:
                        # Tối ưu x4: Các thuật toán Ranked List hỗ trợ cắt lát (Slicing)
                        master_idx = selector.select(X_train, y_train, max_budget)
                        c_time = time.time() - t0
                        
                        for budget in budgets:
                            target_n = int(total_samples * budget)
                            selected_idx = master_idx[:target_n] # Slicing
                            
                            budget_str = f"budget_{int(budget*100):02d}pct"
                            
                            self.log_time(method_name, seed, budget, c_time, 0.0, c_time, "Success")
                            
                            save_dir = os.path.join(self.out_dir, method_name, dataset_name, budget_str)
                            os.makedirs(save_dir, exist_ok=True)
                            
                            X_subset = X_train[selected_idx]
                            y_subset = y_train[selected_idx]
                            
                            df = pd.DataFrame(X_subset, columns=feature_names)
                            df['target'] = y_subset
                            save_path = os.path.join(save_dir, f"seed_{seed}.csv")
                            df.to_csv(save_path, index=False)
                            
                    t_total = time.time() - t0
                    print(f"Xong toàn bộ budgets ({t_total:.1f}s)")
                    
                except Exception as e:
                    t_total = time.time() - t0
                    if "Memory" in str(type(e).__name__) or "alloc" in str(e).lower():
                        print(f"[OOM] ({t_total:.1f}s)")
                        # Ghi file OOM giả cho các budget để Pipeline sau biết mà bỏ qua
                        for budget in budgets:
                            self.log_time(method_name, seed, budget, 0.0, 0.0, t_total, "OOM")
                            budget_str = f"budget_{int(budget*100):02d}pct"
                            save_dir = os.path.join(self.out_dir, method_name, dataset_name, budget_str)
                            os.makedirs(save_dir, exist_ok=True)
                            pd.DataFrame([{"Error": "OOM"}]).to_csv(os.path.join(save_dir, f"seed_{seed}.csv"), index=False)
                    else:
                        print(f"[LỖI: {str(e)}]")
                        for budget in budgets:
                            self.log_time(method_name, seed, budget, 0.0, 0.0, t_total, f"Error: {str(e)}")

if __name__ == "__main__":
    factory = CoresetFactory()
    
    # TIER 1: Nhanh (O(N) - Chạy đầu tiên)
    tier_1_fast = ["M01_Random", "M11_ModerateDS"]
    
    # TIER 2: Deep Learning (O(N * Epochs) - Cắt lát tự động)
    tier_2_neural = ["M08_DataMaps", "M09_Forgetting", "M10_SVP", "M14_TDColER"]
    
    # TIER 3: Tràn (O(N^2) / O(NK) - Nặng nhất, ưu tiên OOM và Timeout cuối cùng)
    tier_3_heavy = ["M03_CoreTab", "M04_SubStrat", "M05_CRAIG", "M06_GradMatch", "M07_GLISTER", "M12_DC", "M13_DM"]
    
    ordered_methods = tier_1_fast + tier_2_neural + tier_3_heavy

    factory.run_experiment(
        dataset_name="CourseQuality", 
        budgets=[0.20], # Sử dụng 1 budget 20% theo yêu cầu
        n_seeds=10,     # Chạy 10 seeds để đảm bảo tính ổn định thống kê
        methods=ordered_methods
    )
    print("\n✅ HOÀN TẤT THỬ NGHIỆM FACTORY!")
