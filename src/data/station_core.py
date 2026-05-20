import os
import json
import numpy as np
import pandas as pd
import joblib

class BaseDataStation:
    """
    Base Class for Data Preprocessing.
    Handles standard saving logic (both .npy for fast loading and .csv for C++ compat).
    """
    def __init__(self, dataset_name, out_dir_base="processed"):
        self.name = dataset_name
        self.out_dir = os.path.join(out_dir_base, dataset_name)
        os.makedirs(self.out_dir, exist_ok=True)
        
        self.feature_names = None
        self.classes = None
        self.encoders = {}
        
    def _save_npy(self, X, y, prefix):
        """Save as numpy arrays for speed"""
        np.save(os.path.join(self.out_dir, f"X_{prefix}.npy"), X)
        np.save(os.path.join(self.out_dir, f"y_{prefix}.npy"), y)
        
    def _save_csv(self, X, y, prefix):
        """Save as CSV for universal compatibility (e.g. C++ RECON)"""
        if self.feature_names is None:
            raise ValueError("feature_names must be set before saving to CSV")
            
        df = pd.DataFrame(X, columns=self.feature_names)
        df['target'] = y
        df.to_csv(os.path.join(self.out_dir, f"{prefix}.csv"), index=False)
        
    def save(self, X_train, y_train, X_val, y_val, X_tests, y_tests):
        """
        Saves the processed data into two formats:
        1. .npy for PyTorch/Sklearn (Fast)
        2. .csv for C++/External algorithms
        """
        print(f"\n  [DataStation] Saving data to {self.out_dir}...")
        
        # 1. Train
        self._save_npy(X_train, y_train, "train")
        self._save_csv(X_train, y_train, "train")
        
        # 2. Val
        self._save_npy(X_val, y_val, "val")
        self._save_csv(X_val, y_val, "val")
        
        # 3. Tests
        test_shapes = []
        for i, (Xt, yt) in enumerate(zip(X_tests, y_tests)):
            test_prefix = f"test_{i+1}"
            self._save_npy(Xt, yt, test_prefix)
            self._save_csv(Xt, yt, test_prefix)
            test_shapes.append(list(Xt.shape))
            
        # 4. Metadata
        metadata = {
            "dataset": self.name,
            "feature_names": self.feature_names,
            "classes": self.classes,
            "n_classes": len(self.classes) if self.classes else 0,
            "n_features": len(self.feature_names) if self.feature_names else 0,
            "train_shape": list(X_train.shape),
            "val_shape": list(X_val.shape),
            "test_shapes": test_shapes,
        }
        
        with open(os.path.join(self.out_dir, "metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        # 5. Encoders
        if self.encoders:
            joblib.dump(self.encoders, os.path.join(self.out_dir, "encoders.pkl"))
            
        print("  ✅ Successfully saved (.npy, .csv, .pkl, .json)!")
