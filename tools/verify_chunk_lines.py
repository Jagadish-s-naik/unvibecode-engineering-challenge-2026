"""Verify line numbers in chunks.jsonl against disk files across all repositories."""
import glob
import zipfile
import json
from pathlib import Path

REPOS = {
    "pluggy": "repos/pluggy",
    "marshmallow": "repos/marshmallow",
    "flask": "repos/flask",
    "chardet": "repos/chardet",
    "full-stack-fastapi-template": "repos/full-stack-fastapi-template"
}

def verify_chunks():
    for repo, rpath in REPOS.items():
        zips = glob.glob(f"evidence/{repo}/run_1/results/*/*.zip")
        if not zips:
            continue
        z = zipfile.ZipFile(zips[0])
        chunks = [json.loads(l) for l in z.read("chunks.jsonl").decode("utf-8").splitlines()]
        
        mismatches = 0
        total = 0
        for c in chunks:
            total += 1
            f = c.get("file")
            lr = c.get("line_range")
            if not lr:
                continue
            s_line = lr["start_line"]
            e_line = lr["end_line"]
            real_file = Path(rpath) / f
            if not real_file.exists():
                continue
            real_lines = real_file.read_text(encoding="utf-8", errors="replace").splitlines()
            expected_slice = real_lines[s_line - 1 : e_line]
            
            # Extract lines from numbered_code
            chunk_lines = [re_l.split(" | ", 1)[-1] if " | " in re_l else re_l for re_l in c.get("numbered_code", "").splitlines()]
            
            # Check length
            if len(chunk_lines) != len(expected_slice):
                mismatches += 1
                if mismatches <= 3:
                    print(f"[{repo}] {f} line count mismatch: chunk says {s_line}-{e_line} ({len(chunk_lines)} lines), real file slice has {len(expected_slice)} lines")
                    
        print(f"[{repo}] Checked {total} chunks: {mismatches} line slice length mismatches")

if __name__ == "__main__":
    verify_chunks()

