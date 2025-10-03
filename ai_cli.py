# SPDX-License-Identifier: Apache-2.0
#!/usr/bin/env python3
import argparse, json, os, subprocess, sys, shutil, glob, pathlib

REPORTS_DIR = "reports"

def ensure_reports():
    os.makedirs(REPORTS_DIR, exist_ok=True)

def which(cmd):
    return shutil.which(cmd) is not None

def detect_stacks():
    stacks = []
    cwd = pathlib.Path(".")
    if (cwd/"package.json").exists():
        stacks.append({"path": ".", "stack": "node"})
    if (cwd/"pyproject.toml").exists() or (cwd/"requirements.txt").exists():
        stacks.append({"path": ".", "stack": "python"})
    return stacks

def run_cmd(cmd, env=None):
    print(f"+ {cmd}", flush=True)
    result = subprocess.run(cmd, shell=True, env=env)
    return result.returncode

# Node adapter
def node_build(): return run_cmd("npm run build || npx -y typescript -p .")
def node_test():
    ensure_reports()
    run_cmd("npm i -D jest jest-junit --no-audit --no-fund || true")
    return run_cmd("npm test -- --reporters=default --reporters=jest-junit || npx -y jest --reporters=default --reporters=jest-junit")
def node_lint(): return run_cmd("npm run lint || npx -y eslint . || true")
def node_format(): return run_cmd("npm run format || npx -y prettier -w . || true")
def node_coverage():
    ensure_reports()
    return run_cmd("npm run coverage || npx -y jest --coverage --coverageReporters=cobertura,lcov || true")
def node_mutation(): return run_cmd("npx -y @stryker-mutator/core run || true")

# Python adapter
def py_build():
    if os.path.exists("pyproject.toml"):
        return run_cmd("python3 -m pip install -U pip && pip install -e . || true")
    elif os.path.exists("requirements.txt"):
        return run_cmd("python3 -m pip install -U pip && pip install -r requirements.txt || true")
    return 0
def py_test():
    ensure_reports()
    run_cmd("python3 -m pip install -q pytest pytest-junitxml || true")
    return run_cmd("pytest -q --junitxml=reports/junit.xml || true")
def py_lint():
    run_cmd("python3 -m pip install -q ruff || true")
    return run_cmd("ruff check . || true")
def py_format():
    run_cmd("python3 -m pip install -q ruff || true")
    return run_cmd("ruff format . || true")
def py_coverage():
    run_cmd("python3 -m pip install -q coverage pytest || true")
    ensure_reports()
    return run_cmd("coverage run -m pytest && coverage xml -o reports/coverage.xml || true")
def py_mutation():
    run_cmd("python3 -m pip install -q mutmut || true")
    return run_cmd("mutmut run || true")

def apply_patch(patch_path):
    if not os.path.exists(patch_path):
        print(f"patch file not found: {patch_path}", file=sys.stderr); return 1
    return run_cmd(f"git apply --index --reject {patch_path} || patch -p1 < {patch_path}")

def reports_upload():
    ensure_reports()
    files = glob.glob("reports/**/*", recursive=True)
    print(json.dumps({"reports": files}, indent=2))
    return 0

def main():
    parser = argparse.ArgumentParser(description="AI CLI (stack-agnostic)")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("detect")
    run_p = sub.add_parser("run"); run_p.add_argument("--task", required=True, choices=["build","test","lint","format","coverage","mutation"])
    ap = sub.add_parser("apply-patch"); ap.add_argument("--file", required=True)
    sub.add_parser("reports")
    args = parser.parse_args()

    if args.cmd == "detect":
        print(json.dumps({"stacks": detect_stacks()}, indent=2)); return 0

    stacks = detect_stacks(); stack = stacks[0]["stack"] if stacks else None
    if args.cmd == "run":
        if not stack: print("No stack detected", file=sys.stderr); return 2
        if stack == "node": fn = {"build": node_build, "test": node_test, "lint": node_lint, "format": node_format, "coverage": node_coverage, "mutation": node_mutation}[args.task]
        elif stack == "python": fn = {"build": py_build, "test": py_test, "lint": py_lint, "format": py_format, "coverage": py_coverage, "mutation": py_mutation}[args.task]
        else: print(f"Unsupported stack: {stack}", file=sys.stderr); return 3
        return fn()
    if args.cmd == "apply-patch": return apply_patch(args.file)
    if args.cmd == "reports": return reports_upload()
    parser.print_help(); return 0

if __name__ == "__main__":
    sys.exit(main())
