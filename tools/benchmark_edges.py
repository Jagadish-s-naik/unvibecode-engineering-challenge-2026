"""Benchmark edge precision and recall for >= 20 sampled functions/classes across repositories."""
import ast
import json
import zipfile
import glob
from pathlib import Path
from collections import defaultdict

SAMPLE_TARGETS = [
    # Flask (10 targets)
    {"repo": "flask", "file": "src/flask/app.py", "symbol": "Flask.dispatch_request", "type": "method"},
    {"repo": "flask", "file": "src/flask/app.py", "symbol": "Flask.full_dispatch_request", "type": "method"},
    {"repo": "flask", "file": "src/flask/app.py", "symbol": "Flask.make_response", "type": "method"},
    {"repo": "flask", "file": "src/flask/app.py", "symbol": "Flask.wsgi_app", "type": "method"},
    {"repo": "flask", "file": "src/flask/app.py", "symbol": "Flask.add_url_rule", "type": "method"},
    {"repo": "flask", "file": "src/flask/blueprints.py", "symbol": "Blueprint.route", "type": "method"},
    {"repo": "flask", "file": "src/flask/blueprints.py", "symbol": "Blueprint.add_url_rule", "type": "method"},
    {"repo": "flask", "file": "src/flask/templating.py", "symbol": "render_template", "type": "function"},
    {"repo": "flask", "file": "src/flask/helpers.py", "symbol": "url_for", "type": "function"},
    {"repo": "flask", "file": "src/flask/helpers.py", "symbol": "flash", "type": "function"},

    # Marshmallow (8 targets)
    {"repo": "marshmallow", "file": "src/marshmallow/schema.py", "symbol": "Schema.dump", "type": "method"},
    {"repo": "marshmallow", "file": "src/marshmallow/schema.py", "symbol": "Schema.load", "type": "method"},
    {"repo": "marshmallow", "file": "src/marshmallow/schema.py", "symbol": "Schema.validate", "type": "method"},
    {"repo": "marshmallow", "file": "src/marshmallow/fields.py", "symbol": "Field._serialize", "type": "method"},
    {"repo": "marshmallow", "file": "src/marshmallow/fields.py", "symbol": "Field._deserialize", "type": "method"},
    {"repo": "marshmallow", "file": "src/marshmallow/fields.py", "symbol": "Nested._serialize", "type": "method"},
    {"repo": "marshmallow", "file": "src/marshmallow/decorators.py", "symbol": "post_load", "type": "function"},
    {"repo": "marshmallow", "file": "src/marshmallow/decorators.py", "symbol": "pre_dump", "type": "function"},

    # Pluggy (6 targets)
    {"repo": "pluggy", "file": "src/pluggy/_manager.py", "symbol": "PluginManager.register", "type": "method"},
    {"repo": "pluggy", "file": "src/pluggy/_manager.py", "symbol": "PluginManager.unregister", "type": "method"},
    {"repo": "pluggy", "file": "src/pluggy/_hooks.py", "symbol": "HookCaller.__call__", "type": "method"},
    {"repo": "pluggy", "file": "src/pluggy/_hooks.py", "symbol": "HookCaller._hookexec", "type": "method"},
    {"repo": "pluggy", "file": "src/pluggy/_callers.py", "symbol": "_multicall", "type": "function"},
    {"repo": "pluggy", "file": "src/pluggy/_manager.py", "symbol": "PluginManager.get_plugins", "type": "method"},
]

def get_ast_calls(repo_name, filepath, symbol_name):
    full_path = Path(f"repos/{repo_name}") / filepath
    if not full_path.exists():
        return set()
    code = full_path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(code, filename=str(full_path))
    
    parts = symbol_name.split(".")
    target_node = None
    if len(parts) == 1:
        # Top level function
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == parts[0]:
                target_node = node
                break
    elif len(parts) == 2:
        # Class method
        cls_name, method_name = parts
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == cls_name:
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name == method_name:
                        target_node = sub
                        break
                        
    calls = set()
    if target_node:
        for n in ast.walk(target_node):
            if isinstance(n, ast.Call):
                try:
                    cname = ast.unparse(n.func)
                    # Extract simple name
                    simple = cname.split(".")[-1]
                    calls.add(simple)
                except Exception:
                    pass
    return calls

def evaluate_sample():
    results = []
    
    # Load connections for all repos
    repo_conns = {}
    for repo_name in ["flask", "marshmallow", "pluggy"]:
        zips = glob.glob(f"evidence/{repo_name}/run_1/results/*/*.zip")
        if zips:
            z = zipfile.ZipFile(zips[0])
            conns = [json.loads(line) for line in z.read("connections.jsonl").decode("utf-8").splitlines()]
            repo_conns[repo_name] = conns
            
    print(f"Sampled {len(SAMPLE_TARGETS)} functions/classes across Flask, Marshmallow, and Pluggy:\n")
    
    total_gt = 0
    total_uvc = 0
    total_true_pos = 0
    
    for t in SAMPLE_TARGETS:
        repo = t["repo"]
        filepath = t["file"]
        symbol = t["symbol"]
        
        # AST ground truth called symbols
        gt_calls = get_ast_calls(repo, filepath, symbol)
        
        # UnvibeCode connections from this file
        conns = repo_conns.get(repo, [])
        uvc_edges = set()
        for c in conns:
            if c.get("source_file") == filepath:
                sym = c.get("symbol")
                if sym:
                    uvc_edges.add(sym.split(".")[-1])
                    
        # Match intersection
        tp = gt_calls.intersection(uvc_edges)
        fp = uvc_edges - gt_calls
        fn = gt_calls - uvc_edges
        
        prec = len(tp) / len(uvc_edges) if uvc_edges else 1.0
        rec = len(tp) / len(gt_calls) if gt_calls else 0.0
        
        total_gt += len(gt_calls)
        total_uvc += len(uvc_edges)
        total_true_pos += len(tp)
        
        res_record = {
            "repo": repo,
            "target": f"{filepath}::{symbol}",
            "gt_calls_count": len(gt_calls),
            "uvc_edges_from_file": len(uvc_edges),
            "matched_true_positives": len(tp),
            "precision": round(prec, 3),
            "recall": round(rec, 3),
            "sample_missed_calls": list(fn)[:3]
        }
        results.append(res_record)
        print(f"[{repo}] {filepath}::{symbol}")
        print(f"  Ground truth calls: {len(gt_calls)} | UVC edges from file: {len(uvc_edges)} | Matched: {len(tp)}")
        print(f"  Precision: {prec:.1%} | Recall: {rec:.1%}")
        if fn:
            print(f"  Sample missed calls (False Negatives): {list(fn)[:4]}")
        print()
        
    overall_prec = total_true_pos / total_uvc if total_uvc else 0
    overall_rec = total_true_pos / total_gt if total_gt else 0
    print(f"=== OVERALL METRICS ACROSS {len(SAMPLE_TARGETS)} TARGETS ===")
    print(f"Total Ground-Truth Calls: {total_gt}")
    print(f"Total UnvibeCode Edges Extracted: {total_uvc}")
    print(f"True Positives: {total_true_pos}")
    print(f"Macro Precision: {overall_prec:.1%}")
    print(f"Macro Recall: {overall_rec:.1%}")
    
    Path("evidence/ground_truth_metrics.json").write_text(json.dumps({
        "overall_precision": round(overall_prec, 4),
        "overall_recall": round(overall_rec, 4),
        "total_targets_sampled": len(SAMPLE_TARGETS),
        "targets": results
    }, indent=2), encoding="utf-8")
    print("\nSaved ground-truth evaluation to evidence/ground_truth_metrics.json")

if __name__ == "__main__":
    evaluate_sample()

