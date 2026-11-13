"""Analyze business workflows across all 5 repos against actual source code using standard library."""
import glob
import re
from pathlib import Path

REPOS = {
    "pluggy": "repos/pluggy",
    "marshmallow": "repos/marshmallow",
    "flask": "repos/flask",
    "chardet": "repos/chardet",
    "full-stack-fastapi-template": "repos/full-stack-fastapi-template"
}

def analyze_repo(repo_name, repo_path):
    html_files = glob.glob(f"evidence/{repo_name}/run_1/results/*/report-support/business-workflows.html")
    if not html_files:
        print(f"No business-workflows.html for {repo_name}")
        return
    
    text = Path(html_files[0]).read_text(encoding="utf-8", errors="replace")
    
    cards = re.split(r'<article\s+class="workflow-card"[^>]*>', text)[1:]
    print(f"\n==================================================")
    print(f"REPO: {repo_name} ({len(cards)} workflow cards found)")
    print(f"==================================================")
    
    total_locations = 0
    valid_locations = 0
    missing_files = 0
    out_of_bounds_lines = 0
    
    for idx, card in enumerate(cards, 1):
        title_m = re.search(r'<h3[^>]*class="workflow-title"[^>]*>(.*?)</h3>', card, re.S)
        title_text = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else f"Workflow {idx}"
        print(f"\n[Workflow {idx}] {title_text}")
        
        # Check implementation locations
        locs = re.findall(r'<span[^>]*class="implementation-location"[^>]*>(.*?)</span>', card, re.S)
        items = re.findall(r'<li[^>]*class="implementation-item"[^>]*>(.*?)</li>', card, re.S)
        
        for item in items:
            total_locations += 1
            item_text = re.sub(r'<[^>]+>', '', item).strip()
            # Match pattern: SymbolName path/to/file.py · lines 10–50
            m = re.search(r'([\w\/\.\-]+)\s*·\s*lines?\s*(\d+)(?:[–\-](\d+))?', item_text)
            if m:
                filepath, start_l, end_l = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
                real_file = Path(repo_path) / filepath
                if not real_file.exists():
                    print(f"    [FAIL] CITED NONEXISTENT FILE: {filepath}")
                    missing_files += 1
                else:
                    lines = real_file.read_text(encoding="utf-8", errors="replace").splitlines()
                    if start_l > len(lines):
                        print(f"    [FAIL] LINE OUT OF BOUNDS: {filepath}:{start_l} (file has {len(lines)} lines)")
                        out_of_bounds_lines += 1
                    else:
                        valid_locations += 1
            else:
                print(f"    [WARN] Could not parse location string: {item_text}")
                
    print(f"\nSummary for {repo_name}: {valid_locations}/{total_locations} verified valid locations. Missing files: {missing_files}, Line errors: {out_of_bounds_lines}")

if __name__ == "__main__":
    for r, p in REPOS.items():
        analyze_repo(r, p)
