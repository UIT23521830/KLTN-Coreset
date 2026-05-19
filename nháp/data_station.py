import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import StratifiedShuffleSplit
import joblib

class DataStation:
    def __init__(self, dataset_name, raw_path, target_col):
        self.dataset_name = dataset_name
        self.raw_path = raw_path
        self.target_col = target_col
        self.data = None
        self.X = None
        self.y = None
        self.processed_dir = "processed_data"
        
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

    def load_data(self, nrows=None):
        print(f"[*] Loading {self.dataset_name} from {self.raw_path}...")
        self.data = pd.read_csv(self.raw_path, nrows=nrows)
        # Drop duplicates if any
        self.data = self.data.drop_duplicates()
        print(f"[+] Loaded {len(self.data)} rows.")

    def preprocess(self):
        print("[*] Preprocessing data...")
        df = self.data.copy()
        
        # Handle Missing Values - Simple Imputation
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype == 'object':
                    df[col] = df[col].fillna(df[col].mode()[0])
                else:
                    df[col] = df[col].fillna(df[col].median())

        # Separate Features and Target
        self.y = df[self.target_col]
        self.X = df.drop(columns=[self.target_col])
        
        # Identify Column Types
        categorical_cols = self.X.select_dtypes(include=['object']).columns
        numerical_cols = self.X.select_dtypes(exclude=['object']).columns
        
        print(f"    - Categorical columns: {len(categorical_cols)}")
        print(f"    - Numerical columns: {len(numerical_cols)}")

        # Encode Categorical
        le_dict = {}
        for col in categorical_cols:
            le = LabelEncoder()
            self.X[col] = le.fit_transform(self.X[col].astype(str))
            le_dict[col] = le
            
        # Target Encoding
        target_le = LabelEncoder()
        self.y = target_le.fit_transform(self.y.astype(str))
        
        # Scale Numerical
        scaler = StandardScaler()
        if len(numerical_cols) > 0:
            self.X[numerical_cols] = scaler.fit_transform(self.X[numerical_cols])
            
        # Save Encoders/Scalers
        meta_path = os.path.join(self.processed_dir, f"{self.dataset_name}_metadata.pkl")
        joblib.dump({'le_dict': le_dict, 'target_le': target_le, 'scaler': scaler}, meta_path)
        print(f"[+] Metadata saved to {meta_path}")

    def split_and_save(self, test_size=0.2):
        print(f"[*] Splitting data (test_size={test_size})...")
        sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
        
        for train_index, test_index in sss.split(self.X, self.y):
            X_train, X_test = self.X.iloc[train_index], self.X.iloc[test_index]
            y_train, y_test = self.y[train_index], self.y[test_index]
            
        # Save as npz for efficiency (can use CSV too if needed for some SOTAs)
        train_path = os.path.join(self.processed_dir, f"{self.dataset_name}_train.npz")
        test_path = os.path.join(self.processed_dir, f"{self.dataset_name}_test.npz")
        
        np.savez(train_path, X=X_train.values, y=y_train, cols=self.X.columns.values)
        np.savez(test_path, X=X_test.values, y=y_test)
        
        print(f"[+] Processed data saved at {self.processed_dir}/")

if __name__ == "__main__":
    # Example for CourseQuality
    # Note: File is 1GB, we might want to run it on the full data later
    station = DataStation(
        dataset_name="CourseQuality",
        raw_path=r"C:\KLTN\paper\CourseQuality\train_med.csv",
        target_col="label_f"
    )
    
    # For initial test, load only 100k rows
    station.load_data(nrows=100000)
    station.preprocess()
    station.split_and_save()
