from unvibecode.client import Client
import json

c = Client()
try:
    s = c.status('58aaf7326d5442d88667ed1068aea767', 0)
    print("Status:", s.get("status"))
    events = s.get("presentation", [])
    print(f"Total events: {len(events)}")
    for i, ev in enumerate(events):
        text = ev.get("text", "")
        print(f"Event {i} kind={ev.get('kind')} final={ev.get('final')} text_len={len(text)} ends_with_newline={text.endswith(chr(10))}")
        print("--- TEXT PREVIEW ---")
        print(repr(text[:120]))
except Exception as e:
    print("Error:", e)

