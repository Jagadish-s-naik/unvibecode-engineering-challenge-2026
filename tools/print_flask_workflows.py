import glob
import re
from pathlib import Path

p = glob.glob('evidence/flask/run_1/results/*/report-support/business-workflows.html')[0]
text = Path(p).read_text(encoding='utf-8')
cards = re.split(r'<article\s+class="workflow-card"[^>]*>', text)[1:]
for i, c in enumerate(cards, 1):
    title = re.search(r'<h3[^>]*class="workflow-title"[^>]*>(.*?)</h3>', c, re.S).group(1).strip()
    locs = re.findall(r'<li[^>]*class="implementation-item"[^>]*>(.*?)</li>', c, re.S)
    print(f"Workflow {i}: {title}")
    for loc in locs:
        print("  -", re.sub(r'<[^>]+>', '', loc).strip())

