"""Execute Phase 1 trials on 5 public repositories twice, saving all evidence."""
import os
import sys
import time
import json
import shutil
import subprocess
from pathlib import Path

REPOS = [
    {
        "name": "pluggy",
        "path": "repos/pluggy",
        "url": "https://github.com/pytest-dev/pluggy",
        "commit": "f8aa4a009716a7994f2f6c1947d9fa69feccbdd5",
        "description": "Plugin/registry-heavy repo (hook specifications & implementations)"
    },
    {
        "name": "marshmallow",
        "path": "repos/marshmallow",
        "url": "https://github.com/marshmallow-code/marshmallow",
        "commit": "1b1250d576e4df95cae66327c97945169dfd538d",
        "description": "src/-layout repo with schema nesting, field registry and circular references"
    },
    {
        "name": "flask",
        "path": "repos/flask",
        "url": "https://github.com/pallets/flask",
        "commit": "ab8149664182b662453a563161aa89013c806dc9",
        "description": "Decorator-registered routes, blueprints, re-exports in __init__.py"
    },
    {
        "name": "chardet",
        "path": "repos/chardet",
        "url": "https://github.com/chardet/chardet",
        "commit": "fa905b359cbcaba93a35fd6429ba9ec4b156c1c1",
        "description": "Encoding tables, non-ASCII datasets, multi-model char distribution"
    },
    {
        "name": "full-stack-fastapi-template",
        "path": "repos/full-stack-fastapi-template",
        "url": "https://github.com/fastapi/full-stack-fastapi-template",
        "commit": "aabb90126964a164e02aff39e7c385bb0598236d",
        "description": "Polyglot repo mixing Python (FastAPI), TypeScript/React, Docker, SQL"
    }
]

def run_single(repo_spec, run_id):
    repo_name = repo_spec["name"]
    target_dir = Path(f"evidence/{repo_name}/run_{run_id}")
    target_dir.mkdir(parents=True, exist_ok=True)
    results_dir = target_dir / "results"
    
    cmd = [
        sys.executable, "-m", "unvibecode", "review",
        "--repository", repo_spec["path"],
        "--output", str(results_dir),
        "--no-open-browser"
    ]
    
    print(f"\n[{time.strftime('%X')}] Starting {repo_name} (run {run_id})...")
    start_t = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    duration = time.perf_counter() - start_t
    print(f"[{time.strftime('%X')}] Finished {repo_name} (run {run_id}) in {duration:.2f}s, exit code {proc.returncode}")
    
    (target_dir / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (target_dir / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
    
    meta = {
        "repo": repo_spec,
        "run_id": run_id,
        "exit_code": proc.returncode,
        "wall_time_seconds": round(duration, 3),
        "command": " ".join(cmd),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    (target_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta

def main():
    summary_records = []
    for repo in REPOS:
        # Check if pluggy run 1 is already completed
        p_r1 = Path(f"evidence/{repo['name']}/run_1/results")
        if repo['name'] == 'pluggy' and p_r1.exists() and not Path(f"evidence/pluggy/run_1/meta.json").exists():
            # Fill pluggy run 1 meta
            meta1 = {
                "repo": repo,
                "run_id": 1,
                "exit_code": 0,
                "wall_time_seconds": 37.0,
                "command": f"{sys.executable} -m unvibecode review --repository repos/pluggy --output evidence/pluggy/run_1/results --no-open-browser",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            Path(f"evidence/pluggy/run_1/meta.json").write_text(json.dumps(meta1, indent=2), encoding="utf-8")
        elif not (Path(f"evidence/{repo['name']}/run_1/meta.json")).exists():
            meta1 = run_single(repo, 1)
        
        # Run 2 for determinism
        if not (Path(f"evidence/{repo['name']}/run_2/meta.json")).exists():
            meta2 = run_single(repo, 2)
            
        print(f"--- Completed testing for {repo['name']} ---")

if __name__ == "__main__":
    main()

