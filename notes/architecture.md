# UnvibeCode System Architecture

## Overview
UnvibeCode is a hybrid local-remote codebase intelligence platform designed to reverse-engineer software repositories into high-level business workflows, connected dependency graphs, evidence-backed risk findings, and LLM-ready context packages.

---

## 1. System Components & Pipeline

```
[Local Workspace]
       │
       ▼ (archive.py: source_files -> pack)
[Sanitized ZIP Archive (<= 50 MiB, <= 10k files)]
       │
       ▼ (client.py: POST /jobs)
[Hosted Engine: shipready-api.alphashots.ai/analysis]
       │
       ├─► Static AST & Tree-Sitter Parsers (Python, Go, JS/TS, etc.)
       ├─► Code Graph Resolver (Package Edges & Call/Symbol Edges)
       ├─► Context Chunking & Selection Engine (Narrow 30k / Optimal 45k / Wider 75k)
       └─► LLM Workflow & Business Risk Synthesis Engine (<= 2M token repos)
       │
       ▼ (client.py: GET /jobs/<id>/download)
[results.zip]
       │
       ▼ (archive.py: extract_safe)
[Generated Artifacts in output directory]
       ├── 00_unvibecode_results.html (Portal)
       ├── 01_connected_code_map_for_llm.html (Vis.js interactive graph)
       ├── 02_business_workflow_map.html (Workflow journey & code anchors)
       ├── 03_business_risk_findings.html (Evidence-based risk reports)
       └── complete_repository_context_for_llm.zip (Normalized chunks & manifest)
```

---

## 2. CLI Entrypoint & Client (`unvibecode`)
- **Version**: `0.4.0` (as of November 2026).
- **Entrypoint**: `cli.py:main()`, invoked via `python -m unvibecode review --repository "<path>"`.
- **Commands**:
  - `health`: Tests connection to `https://shipready-api.alphashots.ai/analysis/health`.
  - `review`: Packages repository, submits job, polls for events, downloads interim & final results, extracts reports, launches browser.
  - `resume <job_id>`: Resumes polling and report download for a previously submitted job.
- **CLI Options**:
  - `--repository`: Required local repository path.
  - `--dry-run`: Scans and prints all matched files without packing or uploading.
  - `--output`: Destination directory for reports (default: `unvibecode_results`).
  - `--no-open-browser`: Suppresses launching default browser upon review completion.

---

## 3. Local File Ingestion & Filtering (`archive.py`)
- **Traversal**: `os.walk(followlinks=False)` traversing directories sorted deterministically.
- **Directory Exclusions (`SKIP_DIRS`)**:
  `.git`, `.venv`, `venv`, `env`, `node_modules`, `__pycache__`, `.next`, `dist`, `build`, `unvibecode_results`, `.idea`, `.vscode`.
- **File Pattern Exclusions (`SKIP_FILES`)**:
  `.env*`, `*credentials*`, `*secret*`, `*token*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa*`, `id_ed25519*`, `*.log`.
- **Supported Text Extensions (`TEXT_SUFFIXES`)**:
  `.py`, `.pyi`, `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs`, `.go`, `.rs`, `.java`, `.kt`, `.kts`, `.c`, `.h`, `.cpp`, `.hpp`, `.cs`, `.rb`, `.php`, `.swift`, `.scala`, `.sh`, `.sql`, `.html`, `.css`, `.scss`, `.vue`, `.svelte`, `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.xml`, `.md`, `.txt`, `.graphql`, `.proto`, `.r`, `.dart`, `.ex`, `.exs`, plus standalone `dockerfile` and `makefile`.
- **Hard Guardrails & Limits**:
  - Maximum single file size: 10 MiB (`10 * 1024 * 1024` bytes).
  - Maximum cumulative uncompressed source: 200 MiB (`200 * 1024 * 1024` bytes).
  - Maximum file count: 10,000 files.
  - Maximum upload ZIP size: 50 MiB (`50 * 1024 * 1024` bytes).

---

## 4. Extraction & Safety Constraints (`archive.py:extract_safe`)
- Validates extracted ZIP paths to prevent Zip Slip directory traversal vulnerabilities:
  - Disallows absolute paths, `..`, `.`, backslashes `\`, colons `:`.
  - Rejects Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`).
  - Blocks symlinks (`stat.S_ISLNK`) and encrypted members.
  - Case-insensitive duplicate member detection.
  - Maximum extracted bytes: 200 MiB (or 1 GiB for results archive).

---

## 5. Hosted Backend Engine & Processing
- **Endpoint**: Hosted REST API at `https://shipready-api.alphashots.ai/analysis`.
- **Authentication**: Bearer token (`PUBLIC_PREVIEW_TOKEN = "unvibecode-public-analysis-preview-v1-2026"`).
- **Parsing Strategy**:
  - Multi-language AST and Tree-Sitter parsers.
  - AST analysis extracts function declarations, classes, imports, call expressions, decorator usages, variable assignments, and type annotations.
- **Code Graph Resolver**:
  - Two edge types: Package Edges (from module import dependencies) and File/Symbol Edges (from statically resolved call sites).
  - Resolution rules: Unambiguous target definitions, qualifier scope match, no variable shadowing.
  - Explicit boundaries: Dynamic calls, interface dispatch, runtime reflection, and dynamic imports are treated as unresolved rather than speculated.
- **Repository Size Tiering**:
  - `<= 2,000,000 estimated tokens`: Receives full 4-pillar review (Connected Code Map, Repository Context, Business Workflow Map, Business Risk Findings).
  - `> 2,000,000 estimated tokens`: Receives Connected Code Map + Repository Context only, to avoid API timeout cliffs.
- **Presentation & Real-Time Streaming**:
  - Job status polling (`/jobs/<job_id>?after=<cursor>`) returning structured presentation event stream (`dashboard`, `clear`, text).
  - Interim results download support when available.

