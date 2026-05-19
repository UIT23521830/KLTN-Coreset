import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd

base = r"C:\KLTN\paper\datasets\CourseQuality"
train_path = os.path.join(base, "train_med.csv")

print("Đang tải dữ liệu...")
# Load a subset for fast analysis, but randomly sampled
df = pd.read_csv(train_path, usecols=['label', 'label_f'])

print("\n" + "="*50)
print("PHÂN TÍCH LABEL vs LABEL_F (Train Set)")
print("="*50)

print(f"\nTổng số mẫu trong Train: {len(df):,}")

# 1. Phân bố độc lập
print("\n[1] Phân bố của 'label':")
print(df['label'].value_counts(normalize=True).mul(100).round(2).astype(str) + '%')

print("\n[2] Phân bố của 'label_f' (Target thực sự):")
print(df['label_f'].value_counts(normalize=True).mul(100).round(2).astype(str) + '%')

# 2. Tỷ lệ giống/khác nhau
match_count = (df['label'] == df['label_f']).sum()
mismatch_count = len(df) - match_count
print(f"\n[3] Tỷ lệ khớp nhau: {match_count:,} ({match_count/len(df)*100:.2f}%)")
print(f"    Tỷ lệ sai lệch:   {mismatch_count:,} ({mismatch_count/len(df)*100:.2f}%)")

# 3. Ma trận chuyển đổi (Crosstab)
print("\n[4] Ma trận chuyển đổi (Cross-tabulation):")
print("Hàng: label (Nhãn trung gian) | Cột: label_f (Nhãn cuối cùng)")
ct = pd.crosstab(df['label'], df['label_f'], margins=True)
print(ct)

print("\nPhần trăm chuyển đổi từ label -> label_f:")
ct_pct = pd.crosstab(df['label'], df['label_f'], normalize='index').mul(100).round(1)
print(ct_pct)
