# UnvibeCode First-Time Developer UX Log

*Real-time log of friction points, timing, messages, and repeat-usage observations during testing.*

---

## 1. Installation & Environment Friction
- **Package Installation**: `pip install --upgrade unvibecode` installed seamlessly as a lightweight pure-Python wheel (`unvibecode-0.4.0-py3-none-any.whl`, ~10 KB). No heavy local binary compilation (C-extensions, Rust, or PyTorch) required.
- **Hosted Model Dependency**: The tool relies entirely on a hosted analysis engine (`https://shipready-api.alphashots.ai/analysis`) with a bundled preview bearer token. When offline, sandboxed, or behind corporate proxies, the CLI immediately crashes with `[STOPPED] Cannot reach API. Check the service and SSH tunnel.` rather than providing a graceful offline fallback or network diagnostic.
- **Tooling Friction**: GitHub CLI (`gh`) integration was required for repository interactions and challenge tracking. On Windows, installing via winget required an explicit PATH refresh or invoking `C:\Program Files\GitHub CLI\gh.exe`.

---

## 2. Time to First Useful Output
- **Fast Lane (Connected Code Map)**: 
  - Produces `*-interim.html` within **1.9 to 2.5 seconds**!
  - Provides instant feedback: files indexed, internal file edges, symbol edges, and downloadable context selections.
- **Deep Business Analysis (Workflow & Risk Engine)**:
  - Takes **35–45 seconds** on small repositories (e.g., 29 files, ~42k tokens in `pluggy`).
  - Progress streaming provides visible milestone updates: `● Business analysis Understanding business workflows -> 0 of 2 code areas reviewed -> 1 of 2 -> Building the business workflow map`.
- **Verdict**: Time to first visual feedback (interim report) is exceptionally good (~2s). Deep analysis time is acceptable for initial exploration, but too slow for interactive terminal commands (like git pre-commit hooks).

---

## 3. Confusing Messages & Interface Rough Edges
- **10-Second Countdown Pause**:
  - Upon completing the analysis, the CLI prints `Opening results page in 10 seconds…` and sleeps synchronously for 10 seconds before attempting `webbrowser.open_new_tab()`.
  - In automated scripts, remote SSH sessions, or headless CI/CD, this imposes a mandatory 10-second penalty unless the user discovers the hidden `--no-open-browser` flag (which is suppressed in `--help`).
- **Terminal Redraw in Non-TTY / Redirected Environments**:
  - `CustomerDashboardRenderer` attempts ANSI VT cursor movement (`\x1b[...A`). In non-standard consoles or redirected execution streams, this causes repeated duplicate status blocks to be printed rather than an in-place spinner or single-line progress bar.
- **Folder Collision Halts Execution**:
  - Running a review into an existing `--output` directory throws `ValueError: This report folder already exists. Choose another --output folder.` and aborts with exit code 1.
  - A developer re-running the command after modifying code is forced to manually delete the directory or invent arbitrary output folder names (`--output results_v2`).
- **Silent Omission of Risk Findings**:
  - In `pluggy`, the server returned `"risk_findings": "DISABLED"` and `"review_outcome": "DISABLED_BY_SERVER_POLICY"`.
  - The CLI terminal reported `UNVIBECODE REVIEW COMPLETE` and listed Business Workflow Map and Connected Code Map, but gave zero explanation as to why Business Risk Findings was omitted. A developer is left wondering if the codebase was completely risk-free or if the feature failed.

---

## 4. What a Developer Would Want Next
- **Terminal-Native Actionable Insights**:
  - Currently, the terminal output only reports completion and provides an HTML file path.
  - Developers want immediate terminal intelligence:
    - Number of workflows identified (with top entry points printed).
    - High-severity business risks (e.g., "1 critical risk detected in `auth.py:42`: Unhandled token expiration").
    - Missing/unresolved call boundaries.
- **Interactive Filtering & Search**:
  - Ability to query workflows directly from CLI: `unvibecode show workflow "Dispatch plugin"` or `unvibecode query --file pluggy/manager.py`.
- **Scoped Diff & Incremental Reviews**:
  - Developers rarely read an entire repository map every day. Once the codebase is understood, their daily unit of work is a **Git branch, diff, or Pull Request** (typically 3–10 modified files).
  - Running a 45-second full-repo review on every commit is impractical. Developers want: `unvibecode diff --staged` or `unvibecode review --diff origin/main`.

---

## 5. What Would Make a Developer Come Back Tomorrow
- **Daily Developer Loop Alignment**:
  - Developers do not open a standalone web dashboard every morning just to look at an unfamiliar codebase they already know.
  - The primary repeat trigger is **Risk & Impact Verification on Code Changes**:
    1. "What existing business workflows will my PR break?"
    2. "What downstream symbols are affected by my refactoring?"
    3. "Did I introduce any business logic edge-case violations?"
- **Visible Brand Presence Without Friction**:
  - A branded PR reviewer / GitHub Action ("UnvibeCode Blast Radius Bot") that automatically leaves a rich, beautifully formatted markdown comment on every PR with a link to an interactive visual diff map.
  - A VS Code extension / sidebar that shows the Business Workflow and Connected Symbols for the currently active editor file.

