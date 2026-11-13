### 1. Recommended Approach: Branded GitHub Action & PR Impact Bot ("UnvibeCode PR Blast Radius")
Introduce an official GitHub Action and CLI sub-command (`unvibecode diff --base main`) triggering automatically on Pull Requests. Instead of an invisible background assistant, it posts a prominent, branded PR comment titled **"UnvibeCode · PR Blast Radius & Workflow Impact"**, surfacing which business workflows, downstream symbols, and risk invariants are touched by the diff, with direct links to interactive visual HTML report artifacts.

### 2. Supporting Points
- **Seamless Fit in Daily Workflow with Diff-Scoped Speed:** In our trial across 5 public repositories (Flask, Pluggy, FastAPI, Marshmallow, Chardet), full reviews averaged ~90–120 seconds—too slow for local saves, but ideal for CI. Developers modify 2–4 files per task; scoping Connected Code mapping to git diffs cuts latency under 15 seconds while directly answering the reviewer's critical question: *"What business workflows could break if merged?"*
- **High-Visibility Brand Recall & Organic Team Virality:** Invisible MCP assistants hide product identity. A branded PR comment places UnvibeCode in front of authors, peer reviewers, and engineering leads on every pull request, making UnvibeCode the recognized standard for merge approval.
- **Natural Return Triggers:** Every code push or peer review triggers a fresh, context-specific architecture summary, creating a habitual return loop without requiring manual CLI invocations.

### 3. Implementation Plan
1. **Core Diff Engine & Action:** Build `unvibecode diff` to restrict graph resolution to changed files, packaged as `unvibecode/action@v1`.
2. **Sticky PR Bot Integration:** Generate sticky PR summary comments with impact tables and links to self-contained HTML artifacts.
3. **Repeat-Use Metric:** Track **Weekly Active Repositories (WAR)** and **PR Re-inspection Rate** (target: >40% of PRs where reviewers open the interactive workflow report).
