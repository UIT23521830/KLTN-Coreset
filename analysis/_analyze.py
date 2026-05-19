import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
import os

base = r"C:\KLTN\paper\CourseQuality"

# Train
print("=== TRAIN (train_med.csv) ===")
df = pd.read_csv(os.path.join(base, "train_med.csv"), nrows=5)
print(f"  Columns: {len(df.columns)}")
print(f"  Dtypes: {dict(df.dtypes.value_counts())}")
print(f"  Object cols: {list(df.select_dtypes('object').columns)}")
print(f"  Target 'label_f' values: {df['label_f'].tolist()}")
print(f"  Target 'label' values:   {df['label'].tolist()}")

# Count full rows
for fname, label in [("train_med.csv","TRAIN"), ("val_med.csv","VAL"), 
                      ("test_med_1.csv","TEST1"), ("test_med_2.csv","TEST2"),
                      ("test_med_3.csv","TEST3"), ("test_med_4.csv","TEST4")]:
    path = os.path.join(base, fname)
    # Count lines (fast)
    with open(path, 'r', encoding='utf-8') as f:
        n = sum(1 for _ in f) - 1  # minus header
    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"\n=== {label} ({fname}) ===")
    print(f"  Rows: {n:,}  |  Size: {size_mb:.1f} MB")

# Check columns match
print("\n=== COLUMN CONSISTENCY ===")
train_cols = list(pd.read_csv(os.path.join(base, "train_med.csv"), nrows=0).columns)
for fname in ["val_med.csv", "test_med_1.csv", "test_med_2.csv", "test_med_3.csv", "test_med_4.csv"]:
    other_cols = list(pd.read_csv(os.path.join(base, fname), nrows=0).columns)
    match = train_cols == other_cols
    print(f"  {fname}: {'✅ MATCH' if match else '❌ MISMATCH'} ({len(other_cols)} cols)")

# Class distribution in train
print("\n=== CLASS DISTRIBUTION (train, first 50K rows) ===")
df_sample = pd.read_csv(os.path.join(base, "train_med.csv"), nrows=50000)
print(df_sample['label_f'].value_counts().to_string())
print(f"\n  label vs label_f same? {(df_sample['label'] == df_sample['label_f']).all()}")
