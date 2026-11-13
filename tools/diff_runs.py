"""Diff Run 1 vs Run 2 across all 5 repositories to evaluate determinism."""
import glob
import json
import re
import zipfile
from pathlib import Path

REPOS = ["pluggy", "marshmallow", "flask", "chardet", "full-stack-fastapi-template"]

def clean_stdout(text):
    # Remove timestamps, paths, dates, durations, job IDs
    text = re.sub(r"\d{4}\d{2}\d{2}_\d{6}", "<TIMESTAMP>", text)
    text = re.sub(r"[0-9a-f]{32}", "<JOB_ID>", text)
    text = re.sub(r"\b\d+(\.\d+)?s\b", "<DURATION>", text)
    text = re.sub(r"C:\\.*?(?=\s|$)", "<PATH>", text)
    text = re.sub(r"/opt/.*?(?=\s|$)", "<REMOTE_PATH>", text)
    return text

def compare_repo(repo):
    r1_dir = Path(f"evidence/{repo}/run_1")
    r2_dir = Path(f"evidence/{repo}/run_2")
    
    out1 = clean_stdout((r1_dir / "stdout.txt").read_text(encoding="utf-8", errors="replace")) if (r1_dir / "stdout.txt").exists() else ""
    out2 = clean_stdout((r2_dir / "stdout.txt").read_text(encoding="utf-8", errors="replace")) if (r2_dir / "stdout.txt").exists() else ""
    stdout_identical = (out1 == out2)
    
    # Compare zips
    z1_paths = glob.glob(f"evidence/{repo}/run_1/results/*/*.zip")
    z2_paths = glob.glob(f"evidence/{repo}/run_2/results/*/*.zip")
    
    zip_stats = {}
    if z1_paths and z2_paths:
        z1 = zipfile.ZipFile(z1_paths[0])
        z2 = zipfile.ZipFile(z2_paths[0])
        
        # Chunks
        chunks1 = [json.loads(line) for line in z1.read("chunks.jsonl").decode("utf-8").splitlines()]
        chunks2 = [json.loads(line) for line in z2.read("chunks.jsonl").decode("utf-8").splitlines()]
        
        # Connections
        conns1 = [json.loads(line) for line in z1.read("connections.jsonl").decode("utf-8").splitlines()]
        conns2 = [json.loads(line) for line in z2.read("connections.jsonl").decode("utf-8").splitlines()]
        
        zip_stats = {
            "chunks_count_r1": len(chunks1),
            "chunks_count_r2": len(chunks2),
            "chunks_identical": len(chunks1) == len(chunks2),
            "conns_count_r1": len(conns1),
            "conns_count_r2": len(conns2),
            "conns_identical": len(conns1) == len(conns2)
        }
    
    return {
        "repo": repo,
        "stdout_deterministic": stdout_identical,
        "zip_stats": zip_stats
    }

def main():
    report = []
    print("=== DETERMINISM ANALYSIS (RUN 1 VS RUN 2) ===")
    for r in REPOS:
        res = compare_repo(r)
        report.append(res)
        print(f"\n[{r.upper()}]")
        print(f"  Cleaned Terminal Output Identical: {res['stdout_deterministic']}")
        if res["zip_stats"]:
            print(f"  Chunks count: R1={res['zip_stats']['chunks_count_r1']}, R2={res['zip_stats']['chunks_count_r2']} (Equal: {res['zip_stats']['chunks_identical']})")
            print(f"  Connections count: R1={res['zip_stats']['conns_count_r1']}, R2={res['zip_stats']['conns_count_r2']} (Equal: {res['zip_stats']['conns_identical']})")
            
    Path("evidence/determinism_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nSaved determinism report to evidence/determinism_summary.json")

if __name__ == "__main__":
    main()

