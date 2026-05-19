import os
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from .station_core import BaseDataStation

CONFIG = {
    "train_path": r"C:\KLTN\paper\datasets\CourseQuality\train_med.csv",
    "val_path":   r"C:\KLTN\paper\datasets\CourseQuality\val_med.csv",
    "test_paths": [
        r"C:\KLTN\paper\datasets\CourseQuality\test_med_1.csv",
        r"C:\KLTN\paper\datasets\CourseQuality\test_med_2.csv",
        r"C:\KLTN\paper\datasets\CourseQuality\test_med_3.csv",
        r"C:\KLTN\paper\datasets\CourseQuality\test_med_4.csv",
    ],
    "test_phases": [
        [1],
        [1, 2],
        [1, 2, 3],
        [1, 2, 3, 4]
    ],
    "target_col": "label_f",
    "label_mapping": {'excellent': 0, 'good': 1, 'average': 2},
    "meta_cols": [
        'user_id_enc', 'course_id_enc', 'school_id',
        'Rank', 'type_of_rank', 'teacher_id', 'label_f'
    ]
}

class CourseQualityStation(BaseDataStation):
    def __init__(self):
        super().__init__("CourseQuality")
        self.cfg = CONFIG
        self.target_col = self.cfg["target_col"]
        self.classes = ["excellent", "good", "average"]
        
        self.school_enc = LabelEncoder()
        self.teacher_enc = LabelEncoder()
        self.encoders = {
            "school_enc": self.school_enc,
            "teacher_enc": self.teacher_enc
        }

    def _split_chapter(self, df, col='chapter', max_level=3):
        """Tách cột chapter thành chapter_1, chapter_2, chapter_3"""
        if col not in df.columns:
            return df
            
        parts = df[col].astype(str).str.split('.', expand=True)
        for i in range(max_level):
            if i < parts.shape[1]:
                df[f'{col}_{i+1}'] = pd.to_numeric(parts[i], errors='coerce').fillna(0).astype(int)
            else:
                df[f'{col}_{i+1}'] = 0
                
        df = df.drop(columns=[col])
        return df

    def _process_test(self, df, keep_phases):
        """Mask data out of phases with -1 để chống Data Leakage"""
        if 'phase' not in df.columns:
            return df
            
        df['phase'] = df['phase'].astype(int)
        protected_cols = self.cfg["meta_cols"] + ['phase']
        other_cols = [c for c in df.columns if c not in protected_cols]
        
        mask = ~df['phase'].isin(keep_phases)
        df.loc[mask, other_cols] = -1
        
        return df.drop(columns='phase')
        
    def _encode_and_fill(self, df, is_train=False):
        """Label Encode, drop label, fillna(0)"""
        # Xóa nhãn trung gian (label) để tránh rò rỉ
        if 'label' in df.columns:
            df = df.drop(columns='label')
            
        # LOẠI BỎ CÁC CỘT ID (user_id, course_id)
        # Rất quan trọng: Nếu giữ ID, Cây Quyết Định (CoreTab/XGBoost) sẽ bị overfit 100%
        # tạo ra các leaf size = 1, làm phá vỡ hoàn toàn nguyên lý hoạt động của thuật toán.
        id_cols = ['user_id', 'course_id', 'user_id_enc', 'course_id_enc']
        df = df.drop(columns=[c for c in id_cols if c in df.columns], errors='ignore')
            
        # Ánh xạ nhãn đích (label_f) sang 0, 1, 2
        if df[self.target_col].dtype == 'object':
            df[self.target_col] = df[self.target_col].map(self.cfg["label_mapping"])
            
        # Encode school_id
        if 'school_id' in df.columns and df['school_id'].dtype == 'object':
            if is_train:
                df['school_id'] = self.school_enc.fit_transform(df['school_id'].astype(str))
            else:
                df['school_id'] = df['school_id'].map(
                    lambda x: self.school_enc.transform([str(x)])[0] 
                    if str(x) in self.school_enc.classes_ else -1
                )
                
        # Encode teacher_id
        if 'teacher_id' in df.columns and df['teacher_id'].dtype == 'object':
            if is_train:
                df['teacher_id'] = self.teacher_enc.fit_transform(df['teacher_id'].astype(str))
            else:
                df['teacher_id'] = df['teacher_id'].map(
                    lambda x: self.teacher_enc.transform([str(x)])[0] 
                    if str(x) in self.teacher_enc.classes_ else -1
                )
                
        # Ép về dạng số nguyên/thực và điền 0 cho khoảng trống
        for col in df.columns:
            if col != self.target_col:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        df = df.fillna(0)
        return df
    
    def process_train(self, df_train):
        print(f"  [1/4] Splitting chapters...")
        df_train = self._split_chapter(df_train)
        
        print(f"  [2/4] Encoding and filling NaNs (Train)...")
        df_train = self._encode_and_fill(df_train, is_train=True)
        
        y = df_train[self.target_col].values.astype(np.int64)
        X = df_train.drop(columns=[self.target_col])
        
        self.feature_names = list(X.columns)
        
        print(f"  [3/4] Done! X shape: {X.shape}")
        return X.values.astype(np.float32), y
        
    def process_val(self, df_val):
        df_val = self._split_chapter(df_val)
        df_val = self._encode_and_fill(df_val, is_train=False)
        
        y = df_val[self.target_col].values.astype(np.int64)
        X = df_val.drop(columns=[self.target_col])
        
        # Đảm bảo cột đúng thứ tự
        X = X[self.feature_names]
        return X.values.astype(np.float32), y
        
    def process_test_file(self, df_test, keep_phases):
        df_test = self._split_chapter(df_test) 
        df_test = self._process_test(df_test, keep_phases)
        df_test = self._encode_and_fill(df_test, is_train=False)
        
        y = df_test[self.target_col].values.astype(np.int64)
        X = df_test.drop(columns=[self.target_col])
        
        X = X[self.feature_names]
        return X.values.astype(np.float32), y

    def run_pipeline(self):
        print("=" * 60)
        print("DATASTATION: Processing CourseQuality (Author's Methodology)")
        print("=" * 60)
        
        # --- TRAIN ---
        t0 = time.time()
        print(f"\n📥 Loading TRAIN: {self.cfg['train_path']}")
        df_train = pd.read_csv(self.cfg["train_path"])
        X_train, y_train = self.process_train(df_train)
        print(f"   Train processed in {time.time()-t0:.1f}s")
        del df_train
        
        # --- VAL ---
        t0 = time.time()
        print(f"\n📥 Loading VAL: {self.cfg['val_path']}")
        df_val = pd.read_csv(self.cfg["val_path"])
        X_val, y_val = self.process_val(df_val)
        print(f"   Val processed in {time.time()-t0:.1f}s")
        del df_val
        
        # --- TESTS ---
        X_tests, y_tests = [], []
        for i, tpath in enumerate(self.cfg["test_paths"]):
            t0 = time.time()
            print(f"\n📥 Loading TEST {i+1}: {tpath}")
            df_test = pd.read_csv(tpath)
            keep_phases = self.cfg["test_phases"][i]
            
            Xt, yt = self.process_test_file(df_test, keep_phases)
            X_tests.append(Xt)
            y_tests.append(yt)
            print(f"   Test {i+1} processed in {time.time()-t0:.1f}s")
            del df_test
        
        # --- SAVE ---
        self.save(X_train, y_train, X_val, y_val, X_tests, y_tests)
        print("\n✅ HOÀN TẤT PILELINE!")

if __name__ == "__main__":
    station = CourseQualityStation()
    station.run_pipeline()
