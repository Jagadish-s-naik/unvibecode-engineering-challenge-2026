import json
import re

issues = json.load(open("notes/existing_issues.json", encoding="utf-8"))
matches = []

check_terms = [
    "rendered_line_count",
    "interim results available here",
    "orphaned",
    "cursor up",
    "interim results ready",
    "dashboard.clear",
    "can_redraw",
    "visual_rows",
    "erase everything below",
]

for item in issues:
    text = ((item.get("title") or "") + " " + (item.get("body") or "")).lower()
    for term in check_terms:
        if term in text:
            matches.append((item['number'], item['title'], term, item['state']))
            break

print(f"Total matches found: {len(matches)}")
for num, title, term, state in matches:
    print(f"[{state.upper()}] #{num}: {title} (matched: '{term}')")

