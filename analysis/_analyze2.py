import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
import os

base = r"C:\KLTN\paper\CourseQuality"

train_cols = list(pd.read_csv(os.path.join(base, "train_med.csv"), nrows=0).columns)
test_cols = list(pd.read_csv(os.path.join(base, "test_med_1.csv"), nrows=0).columns)

# Find extra columns in test
extra_in_test = [c for c in test_cols if c not in train_cols]
missing_in_test = [c for c in train_cols if c not in test_cols]

print("=== COLUMNS ONLY IN TEST (not in train) ===")
for c in extra_in_test:
    print(f"  + {c}")

print(f"\n=== COLUMNS ONLY IN TRAIN (not in test) ===")
for c in missing_in_test:
    print(f"  - {c}")

# Check label vs label_f
print("\n=== label vs label_f (first 20 rows of train) ===")
df = pd.read_csv(os.path.join(base, "train_med.csv"), nrows=20, usecols=['label','label_f'])
for i, row in df.iterrows():
    match = "✅" if row['label'] == row['label_f'] else "❌"
    print(f"  Row {i}: label={row['label']:12s}  label_f={row['label_f']:12s}  {match}")

# Check test file targets
print("\n=== TEST file targets ===")
dt = pd.read_csv(os.path.join(base, "test_med_1.csv"), nrows=5)
for col in ['label', 'label_f']:
    if col in dt.columns:
        print(f"  {col} in test: {dt[col].tolist()}")
    else:
        print(f"  {col} NOT in test")
