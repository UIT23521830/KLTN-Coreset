import arxiv
import os
from pypdf import PdfReader

queries = {
    "01_CoreTab.pdf": "CoreTab: Coreset-based Data-efficient Machine Learning over Tabular Data",
    "02_RECON.pdf": "Coresets over Multiple Tables for Feature-rich and Data-efficient Machine Learning",
    "04_TabCond.pdf": "Efficient Tabular Dataset Condensation",
    "05_C2TC.pdf": "C2TC: A Training-Free Framework for Efficient Tabular Data Condensation",
    "09_SubStrat.pdf": "SubStrat: A Subset-Based Optimization Strategy for Faster AutoML",
    "14_MMD-critic.pdf": "Examples are not enough, learn to criticize! Criticism for Interpretability"
}

client = arxiv.Client()
folder = r'C:\KLTN\paper\sota_papers'

for filename, title in queries.items():
    print(f"\nSearching for: {title}")
    search = arxiv.Search(query=f'ti:"{title}"', max_results=1)
    results = list(client.results(search))
    
    if results:
        paper = results[0]
        print(f"  Found: {paper.title} (ID: {paper.entry_id})")
        filepath = os.path.join(folder, filename)
        # Download
        paper.download_pdf(dirpath=folder, filename=filename)
        
        # Verify
        try:
            reader = PdfReader(filepath)
            text = reader.pages[0].extract_text()
            print(f"  Downloaded verification: {text[:50].replace(chr(10), ' ')}")
        except Exception as e:
            print(f"  Verify ERROR: {e}")
    else:
        print("  Not found on arXiv.")
        # Try broader search
        broad_search = arxiv.Search(query=f'all:"{title}"', max_results=1)
        broad_results = list(client.results(broad_search))
        if broad_results:
            paper = broad_results[0]
            print(f"  Found broadly: {paper.title} (ID: {paper.entry_id})")
            paper.download_pdf(dirpath=folder, filename=filename)
        else:
            print("  Still not found.")
