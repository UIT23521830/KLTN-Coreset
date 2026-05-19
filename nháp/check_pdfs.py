import os

folder = r'C:\KLTN\paper\sota_papers'
if not os.path.exists(folder):
    print(f"Folder {folder} not found.")
else:
    files = os.listdir(folder)
    print(f"Found {len(files)} files in {folder}:")
    for f in files:
        path = os.path.join(folder, f)
        size = os.path.getsize(path) / 1024
        status = "OK" if size > 100 else "CORRUPTED"
        print(f"{f} - {size:.2f} KB - [{status}]")
