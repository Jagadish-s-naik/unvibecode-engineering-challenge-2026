# UnvibeCode Engineering Findings & Discrepancies Log

This document records all concrete discrepancies, bugs, and behavioral failures discovered during testing against independent ground truth.

---

## Finding 1: Cross-Language Standard Library Module Hijacking (Connected Code Map & Context Preparation)
- **Severity**: HIGH / CRITICAL
- **Component**: Linker Module Resolution (`LinkerResolutionModule` / `stem_fallback`)
- **Repro Rating**: 100% Deterministic (Verified on `fastapi/full-stack-fastapi-template` and synthetic minimal repo)
- **Evidence Files**:
  - `evidence/full-stack-fastapi-template/run_1/results/*/technical-logs/connected_code_map.log`
  - `evidence/full-stack-fastapi-template/run_1/results/*/*.zip` (`connections.jsonl`, `selections.jsonl`)
  - `evidence/test_cross_lang/results/*/*.zip` (`connections.jsonl`)
- **Observed Behavior**:
  In a repository containing Python and TypeScript/JavaScript, standard Python library imports (`import random`, `import json`, `import time`) are resolved to internal frontend TypeScript files (`frontend/tests/utils/random.ts`, `frontend/json.ts`, `frontend/time.ts`).
  Similarly, TypeScript relative symbol imports (e.g. `import { type Item, Main } from "./Main"`) are resolved across language boundaries to Python database classes (`backend/app/models.py:Item`).
- **Blast Radius & Impact**:
  Contaminates `selections.jsonl`:
  - Requesting Optimal (radius 1) or Wider (radius 2) context for a Python test file (`backend/tests/utils/utils.py`) bundles 7 frontend Playwright TypeScript specs (`frontend/tests/admin.spec.ts`, `login.spec.ts`, `items.spec.ts`, etc.) into the AI context window.
  - Requesting context for a React UI component (`AppSidebar.tsx`) bundles Alembic migrations, database models, and API routers into the frontend context.
- **Root Cause**:
  The module linker performs stem-based filename matching across the entire workspace (`Path(f).stem.lower() == module_name.lower()`) without restricting candidate files to the source file's language or extension, and without checking standard-library module registries.

---

## Finding 2: HTML Template Interpolation and Hyperlinks Extracted as Module Imports
- **Severity**: MEDIUM
- **Component**: HTML / Web Template Parser
- **Repro Rating**: 100% Deterministic (Verified on `marshmallow`, `flask`, `full-stack-fastapi-template`, `chardet`)
- **Evidence Files**:
  - `evidence/marshmallow/run_1/results/*/*.zip` (`unresolved_relationships.jsonl`)
  - `evidence/flask/run_1/results/*/*.zip` (`unresolved_relationships.jsonl`)
- **Observed Behavior**:
  In `.html` files (included via `archive.py:TEXT_SUFFIXES`), Jinja2 template tags (`{{ theme_donate_url }}`, `{{ url_for( ... ) }}`, `{{ link }}`) and HTTP URLs (`http://www.sol.sohu.com`, `https://img.shields.io/...`) are parsed as module import statements.
  They are recorded as `source_file: "docs/_templates/donate.html", module: "{{ theme_donate_url }}", reason: "unknown_symbol_or_external_module"` in `unresolved_relationships.jsonl`.
- **Impact**:
  Pollutes the unresolved dependency index with template syntax fragments and external URLs, distorting package boundary analysis.

---

## Finding 3: Complete Absence of Function Call / Invocation Edges in Connected Code Map
- **Severity**: HIGH
- **Component**: Code Graph Resolver / `connections.jsonl`
- **Repro Rating**: 100% Deterministic (Verified on all 5 repositories: 1,131 total connections analyzed)
- **Evidence Files**:
  - `evidence/ground_truth_metrics.json`
  - `evidence/*/run_1/results/*/*.zip` (`connections.jsonl`)
- **Observed Behavior**:
  Across all 5 test repositories, 100% of recorded connections in `connections.jsonl` are import relationships (`imports_symbol`: 615, `file_import`: 464, `imports_module`: 52). There is zero representation of function calls, method invocations, or runtime call relationships.
  Against an AST ground truth of 92 function/method calls across 24 sampled targets in Flask, Marshmallow, and Pluggy, UnvibeCode achieved only **5.4% recall** (5 true positives) and **2.6% precision**.

---

## Finding 4: Silent Omission of Business Risk Findings Under `DISABLED_BY_SERVER_POLICY`
- **Severity**: MEDIUM / UX
- **Component**: Hosted Analysis Engine & CLI Presentation
- **Repro Rating**: 100% Deterministic (Observed on all 5 public repos)
- **Evidence Files**:
  - `evidence/*/run_1/results/*/technical-logs/analysis-status.json`
- **Observed Behavior**:
  `analysis-status.json` records `"components": { "business_workflows": "COMPLETED", "risk_findings": "DISABLED" }` and `"review_outcome": "DISABLED_BY_SERVER_POLICY"`.
  However, the CLI terminal prints `UNVIBECODE REVIEW COMPLETE` with no warning, disclosure, or explanation to the developer about why Business Risk Findings was omitted.

---

## Finding 5: Business Path Compiler Crash on Pure Utility / Zero-Workflow Repositories
- **Severity**: HIGH
- **Component**: Stage 04 Business Path Compiler (`customer_runner.py:run_step_four`)
- **Repro Rating**: 100% Deterministic (Verified on `repos/test_cross_lang`)
- **Evidence Files**:
  - `evidence/test_cross_lang/results/*/technical-logs/business_workflow_review.log`
- **Observed Behavior**:
  When a codebase contains utility functions but zero high-level business workflow paths (`paths=0`), Stage 04 crashes with `CompilerError: No evidence-valid business path fragments are present` (exit code 1).
  Instead of producing an empty workflow report, the entire review terminates in `UNVIBECODE REVIEW PARTIAL` (exit code 1).

