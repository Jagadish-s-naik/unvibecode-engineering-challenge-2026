import urllib.request
import re
import json

url = 'https://docs.google.com/forms/d/1an-hce3EQ8bUVArnZJnD1VwxQIxgmNzLKYQ8h814CVE/viewform'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

data_match = re.search(r'FB_PUBLIC_LOAD_DATA_\s*=\s*(.*?);</script>', html)
if data_match:
    raw_json = data_match.group(1)
    data = json.loads(raw_json)
    form_items = data[1][1]
    print(f"Total fields found: {len(form_items)}")
    for item in form_items:
        title = item[1]
        desc = item[2]
        field_id = item[0]
        field_type = item[3]
        entry_info = item[4]
        # entry_id is usually entry_info[0][0]
        entry_id = entry_info[0][0] if entry_info and len(entry_info) > 0 else "N/A"
        required = entry_info[0][2] == 1 if entry_info and len(entry_info[0]) > 2 else False
        print(f"\n--- Field: {title} ---")
        print(f"Entry ID: entry.{entry_id}")
        print(f"Required: {required}")
        print(f"Type: {field_type}")
        if desc:
            print(f"Description: {desc[:100]}...")

