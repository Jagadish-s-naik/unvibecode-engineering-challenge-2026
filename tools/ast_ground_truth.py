"""Independent AST-based ground-truth extraction and comparison tool for UnvibeCode."""
import ast
import os
import sys
import json
import zipfile
from pathlib import Path
from collections import defaultdict

class CodebaseInspector(ast.NodeVisitor):
    def __init__(self, filepath, rel_path):
        self.filepath = filepath
        self.rel_path = rel_path.replace("\\", "/")
        self.definitions = {} # symbol -> {type, line, decorators}
        self.calls = []       # {caller, target, line}
        self.imports = []     # {module, name, alias, line, is_from}
        self.all_exports = None
        self.current_scope = [self.rel_path]

    def visit_ClassDef(self, node):
        scope_name = "::".join(self.current_scope)
        full_name = f"{scope_name}::{node.name}"
        decs = [ast.unparse(d) for d in node.decorator_list]
        self.definitions[full_name] = {"type": "class", "name": node.name, "line": node.lineno, "decorators": decs, "file": self.rel_path}
        self.current_scope.append(node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_FunctionDef(self, node):
        self._handle_func(node)

    def visit_AsyncFunctionDef(self, node):
        self._handle_func(node)

    def _handle_func(self, node):
        scope_name = "::".join(self.current_scope)
        full_name = f"{scope_name}::{node.name}"
        decs = [ast.unparse(d) for d in node.decorator_list]
        self.definitions[full_name] = {"type": "function", "name": node.name, "line": node.lineno, "decorators": decs, "file": self.rel_path}
        self.current_scope.append(node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_Call(self, node):
        caller = "::".join(self.current_scope)
        try:
            target_expr = ast.unparse(node.func)
        except Exception:
            target_expr = "<unparsed>"
        self.calls.append({"caller": caller, "target": target_expr, "line": node.lineno, "file": self.rel_path})
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({"module": alias.name, "name": None, "asname": alias.asname, "line": node.lineno, "is_from": False, "file": self.rel_path})

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.append({"module": node.module, "name": alias.name, "asname": alias.asname, "level": node.level, "line": node.lineno, "is_from": True, "file": self.rel_path})

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                try:
                    if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                        self.all_exports = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
                except Exception:
                    pass
        self.generic_visit(node)

def analyze_repo(repo_dir):
    repo_dir = Path(repo_dir).resolve()
    results = {
        "definitions": {},
        "calls": [],
        "imports": [],
        "all_exports": {},
        "files": []
    }
    for base, _, files in os.walk(repo_dir):
        for f in files:
            if f.endswith(".py"):
                full_path = Path(base) / f
                rel_path = full_path.relative_to(repo_dir).as_posix()
                results["files"].append(rel_path)
                try:
                    code = full_path.read_text(encoding="utf-8", errors="replace")
                    tree = ast.parse(code, filename=str(full_path))
                    inspector = CodebaseInspector(full_path, rel_path)
                    inspector.visit(tree)
                    results["definitions"].update(inspector.definitions)
                    results["calls"].extend(inspector.calls)
                    results["imports"].extend(inspector.imports)
                    if inspector.all_exports is not None:
                        results["all_exports"][rel_path] = inspector.all_exports
                except Exception as e:
                    print(f"Error parsing {rel_path}: {e}")
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = analyze_repo(sys.argv[1])
        print(f"Analyzed {len(data['files'])} Python files.")
        print(f"Total definitions: {len(data['definitions'])}")
        print(f"Total calls: {len(data['calls'])}")
        print(f"Total imports: {len(data['imports'])}")
        print(f"Modules with __all__: {len(data['all_exports'])}")

