"""Inspect smolagents and django-payments sample risk findings."""
import re
from pathlib import Path

def inspect_file(path_str):
    p = Path(path_str)
    if not p.exists():
        print(f"File not found: {path_str}")
        return
    text = p.read_text(encoding="utf-8")
    headings = re.findall(r'<h[234][^>]*>(.*?)</h[234]>', text)
    code_refs = re.findall(r'(\b[\w\/\.\-]+\.py:\d+\b)', text)
    print(f"\n--- {p.name} ({p.parent.parent.name}) ---")
    print(f"Total lines: {len(text.splitlines())}")
    print("Headings:", headings[:8])
    print(f"Code references cited (e.g. file.py:line): {len(code_refs)}")
    for ref in code_refs[:10]:
        print("  -", ref)

if __name__ == "__main__":
    inspect_file("repos/unvibecode/docs/gitdocs/smolagents/2026-10-18/report-support/risk-findings.html")
    inspect_file("repos/unvibecode/docs/gitdocs/django-payments/2026-10-18/report-support/risk-findings.html")

