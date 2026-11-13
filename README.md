# UnvibeCode Engineering Challenge 2026 (Cohort 3) — Evaluation Submission

Candidate: **Jagadish Naik**  
GitHub: [@Jagadish-s-naik](https://github.com/Jagadish-s-naik)  
Target Package: `unvibecode` (v0.4.0)

---

## 📌 Track 1: Engineering Issue Investigation
- **Published Issue:** [FinanceFlash/unvibecode#748](https://github.com/FinanceFlash/unvibecode/issues/748)
- **Title:** `[Bug] CLI Presentation — Interleaved stream events desynchronize CustomerDashboardRenderer relative cursor, erasing interim report announcements and orphaning duplicate dashboard headers`
- **Root Cause:** In interactive terminals (`can_redraw is True`), `CustomerDashboardRenderer` computes ANSI `CUU` cursor displacement solely from its own rendered line count. Asynchronous non-dashboard events streamed from the server (e.g. interim report announcements) are printed directly via `cli.py:render()` without clearing the active live dashboard first, advancing the cursor down 3+ rows. Subsequent refreshes move up too few rows, erasing the interim announcement URL and leaving ghost duplicate headers permanently frozen in terminal scrollback.
- **Verification:** 100% deterministic reproduction across 3 trials (`tools/repro_dashboard_cursor_desync.py`).
- **Deliverable:** [`deliverables/issue.md`](deliverables/issue.md)

---

## 💡 Track 2: Developer Adoption & Repeat-Usage Strategy
- **Recommended Approach:** Branded GitHub Action & PR Impact Bot ("UnvibeCode PR Blast Radius")
- **Mechanism:** Automates `unvibecode diff --base main` on Pull Requests to generate high-visibility, sticky PR summary comments detailing affected business workflows, blast radius matrices, and links to interactive visual reports.
- **Trial Evidence:** Full repo analysis on Flask / FastAPI takes ~90–120s (too slow for pre-commit); scoping Connected Code analysis to git diff boundaries drops latency under 15 seconds, fitting seamlessly into daily developer PR review workflows.
- **Deliverable:** [`deliverables/track2.md`](deliverables/track2.md)
- **Interactive Mock:** [`deliverables/mock_pr_comment.md`](deliverables/mock_pr_comment.md)

---

## 🛠️ Repository Structure
- `deliverables/`: Final submissions (GitHub issue markdown, Track 2 proposal, Google Form summary, receipt).
- `evidence/`: Raw stdout, stderr, run metadata, determinism benchmarks, and context bundles across 5 pinned public repositories (`pallets/flask`, `pytest-dev/pluggy`, `marshmallow-code/marshmallow`, `chardet/chardet`, `fastapi/full-stack-fastapi-template`).
- `notes/`: Architecture reverse-engineering, catalog of all 741 existing issues, UX friction logs, and candidate discrepancy logs.
- `tools/`: Independent AST ground-truth tools, duplicate issue search engine, and deterministic repro scripts.

