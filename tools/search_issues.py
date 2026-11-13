"""Search existing_issues.json for duplicate detection and competitive ranking."""
import json
import re
import sys

def search_issues(query, max_results=10):
    issues = json.load(open("notes/existing_issues.json", encoding="utf-8"))
    q_words = [w.lower() for w in re.findall(r"\w+", query)]
    
    scored = []
    for item in issues:
        title = item.get("title") or ""
        body = item.get("body") or ""
        text = (title + " " + body).lower()
        
        # Calculate keyword match score
        score = sum(text.count(w) for w in q_words)
        title_score = sum(title.lower().count(w) * 5 for w in q_words)
        total_score = score + title_score
        
        if total_score > 0:
            scored.append((total_score, item))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:max_results]

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "cross language import"
    results = search_issues(q)
    print(f"Top {len(results)} matches for '{q}':\n")
    for score, item in results:
        print(f"[{item['state'].upper()}] #{item['number']}: {item['title']} (Score: {score})")
        print(f"URL: {item.get('html_url')}")
        snippet = (item.get('body') or '').replace('\n', ' ')[:160]
        print(f"Snippet: {snippet}...\n")

