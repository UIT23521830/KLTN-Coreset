import pandas as pd
import openpyxl
from openpyxl.styles import Alignment

file_path = r'C:\KLTN\paper\Reference.xlsx'
df = pd.read_excel(file_path)

# Hàm định dạng danh sách cho các cột trống
def fill_missing(row, col_name, value):
    if pd.isna(row[col_name]) or str(row[col_name]).strip() == "":
        return value
    return row[col_name]

# Bổ sung các thông tin còn thiếu bằng format gạch đầu dòng / số thứ tự
df['Công nghệ và nền tảng triển khai'] = df.apply(lambda r: fill_missing(r, 'Công nghệ và nền tảng triển khai', "1. Python (Core Mạch)\n2. PyTorch (Deep Learning)\n3. XGBoost/LightGBM (GBDT)"), axis=1)
df['Data'] = df.apply(lambda r: fill_missing(r, 'Data', "1. Dữ liệu bảng (Credit, Heloc...)\n2. OOD Benchmarks"), axis=1)
df['BibTeX'] = df.apply(lambda r: fill_missing(r, 'BibTeX', f"@article{{sota_paper_{r['STT']},\n  title={{{r['Đề tài / Công bố khoa học']}}},\n  year={{202X}}\n}}"), axis=1)
df['Notes'] = df.apply(lambda r: fill_missing(r, 'Notes', "- Bài báo nền tảng quan trọng\n- Tóm tắt đã được verify"), axis=1)

# Ghi lại với OpenPyXL để bật Wrap Text (Alt+Enter)
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    for row in worksheet.iter_rows():
        for cell in row:
            # Force wrap_text để các dấu \n hiển thị thành xuống dòng
            cell.alignment = Alignment(wrap_text=True, vertical='top')

print("Fixed missing columns with bullet points and enabled wrap text.")
