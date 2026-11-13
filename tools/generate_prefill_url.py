import urllib.parse

base_url = "https://docs.google.com/forms/d/1an-hce3EQ8bUVArnZJnD1VwxQIxgmNzLKYQ8h814CVE/viewform?usp=pp_url"

with open("deliverables/track2.md", "r", encoding="utf-8") as f:
    track2_text = f.read()

feedback_text = (
    "The Connected Code Map interactive HTML visualizer worked exceptionally well—symbol relationship "
    "parsing and token estimation are smooth, and chunk-level line mappings matched ground truth across all test repos. "
    "What was confusing and needs improvement: (1) In interactive terminals, CustomerDashboardRenderer relative cursor "
    "movement desynchronizes during interim event streaming, causing interim report links to be wiped from view and "
    "orphaning duplicate headers in terminal scrollback. (2) Business Risk Findings are omitted under DISABLED_BY_SERVER_POLICY "
    "with no CLI-level warning. (3) --no-open-browser is suppressed in --help, leaving headless/CI users without clear guidance."
)

params = {
    "entry.933839510": "Jagadish Naik",
    # "entry.1675779955": email,
    "entry.1619819454": feedback_text,
    "entry.1407943535": "https://github.com/FinanceFlash/unvibecode/issues/748",
    "entry.1076182247": track2_text,
    "entry.1766598804": "Reconstruct code into business impact.",
    "entry.1757017662": "Yes",
    "entry.572063283": "https://github.com/Jagadish-s-naik",
    # "entry.1234415658": college_and_year,
    "entry.180204526": "NA",
}

query_string = urllib.parse.urlencode(params)
full_prefill_url = base_url + "&" + query_string

print("Generated pre-filled URL length:", len(full_prefill_url))
with open("deliverables/prefill_url.txt", "w", encoding="utf-8") as f:
    f.write(full_prefill_url)
print("Saved prefill URL to deliverables/prefill_url.txt")

