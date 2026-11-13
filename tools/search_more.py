import json

issues = json.load(open("notes/existing_issues.json", encoding="utf-8"))

keywords = ["scrollback", "ghost", "interleaved", "desync", "relative cursor", "cuu", "clear()", "render(event)"]

print("Searching for keywords:", keywords)
found = 0
for it in issues:
    text = ((it.get("title") or "") + " " + (it.get("body") or "")).lower()
    for kw in keywords:
        if kw in text:
            print(f"Match #{it['number']} [{it['state']}]: {it['title']} (keyword: {kw})")
            found += 1
            break

print(f"Total found: {found}")

