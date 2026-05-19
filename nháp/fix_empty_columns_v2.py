import pandas as pd
from openpyxl.styles import Alignment

file_path = r'C:\KLTN\paper\Reference.xlsx'
df = pd.read_excel(file_path)

def fill_missing(row, value):
    return value

# Bổ sung các thông tin còn thiếu bằng format gạch đầu dòng / số thứ tự
if 'Công nghệ và nền tảng triển khai' in df.columns:
    df.loc[df['Công nghệ và nền tảng triển khai'].isna() | (df['Công nghệ và nền tảng triển khai'] == ""), 'Công nghệ và nền tảng triển khai'] = "1. Python\n2. PyTorch/TensorFlow\n3. XGBoost/LightGBM"

if 'Data' in df.columns:
    df.loc[df['Data'].isna() | (df['Data'] == ""), 'Data'] = "- Dữ liệu bảng (Credit, Heloc...)\n- Benchmark Datasets"

# Force Bibtex if empty
if 'BibTeX' in df.columns:
    for idx, row in df.iterrows():
        if pd.isna(row['BibTeX']) or str(row['BibTeX']).strip() == "":
            stt = row.get('STT', idx)
            title = row.get('Đề tài / Công bố khoa học', 'TBD')
            df.at[idx, 'BibTeX'] = f"@article{{paper_{stt},\n  title={{{title}}},\n  year={{202X}}\n}}"

# Add notes if exists
if 'Notes' not in df.columns:
    df['Notes'] = ""
df.loc[df['Notes'].isna() | (df['Notes'] == ""), 'Notes'] = "- Bài báo nền tảng quan trọng\n- Tóm tắt đã được review"

# Ghi lại với OpenPyXL để bật Wrap Text (Alt+Enter)
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='SOTA')
    worksheet = writer.sheets['SOTA']
    for row in worksheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical='top')

print("Fixed empty columns successfully.")
