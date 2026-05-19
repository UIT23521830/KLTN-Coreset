import os
from pypdf import PdfReader

folder = r'C:\KLTN\paper\sota_papers'
files = [f for f in os.listdir(folder) if f.endswith('.pdf')]
files.sort()

for f in files:
    path = os.path.join(folder, f)
    try:
        reader = PdfReader(path)
        if len(reader.pages) > 0:
            text = reader.pages[0].extract_text()
            title = text.split('\n')[:3]  # Lấy 3 dòng đầu
            print(f"--- File: {f} ---")
            print(" ".join(title).strip())
        else:
            print(f"--- File: {f} ---")
            print("[EMPTY PDF]")
    except Exception as e:
        print(f"--- File: {f} ---")
        print(f"[ERROR READING PDF]: {e}")
