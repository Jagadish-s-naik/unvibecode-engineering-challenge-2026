# UnvibeCode Engineering Challenge 2026 — Progress Notes

## Phase 0: Setup and Star
- Virtual environment created on Python 3.14.2 (Windows 11 AMD64).
- `unvibecode` package v0.4.0 installed from PyPI.
- GitHub CLI authenticated as `Jagadish-s-naik`.
- Pinned and verified star on `FinanceFlash/unvibecode` via GitHub API (HTTP 204).
- Target repository cloned and cataloged 737 issues/PRs to `notes/existing_issues.json`.
- Reverse-engineered client architecture in `notes/architecture.md`.

## Phase 1: Real Repositories & Determinism Trials
- Ran review twice across 5 public repositories (Flask, Pluggy, Marshmallow, Chardet, FastAPI).
- All logs, metadata, HTML reports, and context bundles preserved under `evidence/<repo>/run_1/` and `run_2/`.
- Evaluated determinism: 100% deterministic chunk counts and connection counts across runs.
- Documented friction and observations in `notes/ux_log.md`.

## Phase 2: Ground-Truth Comparison & Deep Auditing
- Built AST ground truth and benchmarked 24 sampled targets: identified 100% import-only edges and complete absence of function invocation edges in `connections.jsonl`.
- Verified chunk line bounds across 1,544 chunks with zero line count deviations.
- Identified and cataloged candidate discrepancies in `notes/findings.md`.

## Phase 3: Pick the Winning Issue & Root Cause Investigation
- Conducted duplicate search across all 737 open and closed issues.
- Selected winning issue: **CLI Presentation — Interleaved stream events desynchronize CustomerDashboardRenderer relative cursor, erasing interim report announcements and orphaning duplicate dashboard headers**.
- Pinpointed exact lines: `unvibecode/cli.py:lines 65–70` and `unvibecode/presentation.py:lines 50–74`.
- Validated minimal reproduction script with 100% hit rate across 3 automated trials (`evidence/terminal_cursor_desync_repro.txt`).
- Confirmed zero duplicates on GitHub issues up through latest #741.

## Phase 4: Track 1 Deliverable
- Authored `deliverables/issue.md` adhering strictly to the exact 9-section template.
- Authored 3-4 line summary in `deliverables/form_summary.md`.

## Phase 5: Track 2 Deliverable
- Authored `deliverables/track2.md` (279 words) covering:
  1. Recommended approach: Branded GitHub Action & PR Impact Bot ("UnvibeCode PR Blast Radius").
  2. 3 supporting points: Daily routine fit with fast diff scoping, visible brand attribution, organic return triggers.
  3. Implementation plan: Core diff engine, sticky PR comment integration, and repeat-use metrics (WAR and PR Re-inspection Rate).
- Created mock PR comment prototype in `deliverables/mock_pr_comment.md`.

## Phase 6: QA & Approval Gate
- Verified reproduction following ONLY `issue.md` instructions (100% success).
- Re-checked live GitHub issues up to #741: no collisions or duplicates.
- All evidence verified against files on disk. Awaiting user approval to proceed to Phase 7.
