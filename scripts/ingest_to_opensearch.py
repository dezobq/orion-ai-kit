#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import os, sys, json, hashlib, subprocess, time
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# deps stdlib + requests/tqdm
try:
    import requests  # type: ignore
except Exception:
    print("ERROR: pip install requests first", file=sys.stderr); sys.exit(1)
try:
    from tqdm import tqdm  # type: ignore
except Exception:
    def tqdm(x, **k): return x  # no-op

USE_EMB = os.environ.get("WITH_EMBEDDINGS", "0") in ("1","true","yes")

if USE_EMB:
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        EMB_MODEL_NAME = os.environ.get("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        _emb_model = SentenceTransformer(EMB_MODEL_NAME)
        EMB_DIM = len(_emb_model.encode("test"))
    except Exception as e:
        print(f"WARNING: embeddings disabled ({e})"); USE_EMB = False; _emb_model = None; EMB_DIM = 0

ROOT = Path(os.environ.get("ROOT", "/workspace")).resolve()
OS_URL = os.environ.get("OS_URL", "https://localhost:9200").rstrip("/")
OS_USER = os.environ.get("OS_USER", "admin")
OS_PASS = os.environ.get("OS_PASS", "MyS3curePassw0rd!2025")
INDEX  = os.environ.get("INDEX", "code-chunks")

INCLUDE_GLOBS = [
    "src/**/*.*", "lib/**/*.*", "apps/**/*.*", "services/**/*.*",
    "*.js", "*.ts", "*.py", "*.java", "*.go", "*.cs", "*.rb", "*.php", "*.rs"
]
EXCLUDE_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", ".stryker-tmp"}

WINDOW = int(os.environ.get("CHUNK_LINES", "80"))
OVERLP = int(os.environ.get("CHUNK_OVERLAP", "20"))

def git(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT).decode().strip()

def repo_sha() -> str:
    try: return git(["git", "rev-parse", "HEAD"])
    except Exception: return "NO_GIT_SHA"

def file_blob_sha(p: Path) -> str:
    try: return git(["git", "hash-object", str(p)])
    except Exception:
        h = hashlib.sha1(p.read_bytes()).hexdigest()
        return f"sha1:{h}"

def detect_lang(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return {"js":"javascript","ts":"typescript","py":"python","java":"java","go":"go",
            "cs":"csharp","rb":"ruby","php":"php","rs":"rust"}.get(ext, ext or "text")

def iter_files() -> List[Path]:
    files: List[Path] = []
    for pat in INCLUDE_GLOBS:
        for p in ROOT.glob(pat):
            if p.is_file() and not any(part in EXCLUDE_DIRS for part in p.parts):
                files.append(p)
    # de-dup
    uniq = []
    seen = set()
    for p in files:
        q = str(p.resolve())
        if q not in seen:
            uniq.append(p); seen.add(q)
    return uniq

def chunk_lines(lines: List[str], window: int, overlap: int) -> List[Tuple[int,int,str]]:
    n = len(lines)
    out = []
    i = 0
    while i < n:
        j = min(i+window, n)
        text = "".join(lines[i:j])
        out.append((i+1, j, text))
        if j == n: break
        i = j - overlap
        if i < 0: i = 0
    return out

def bulk_post(actions: List[Dict]):
    if not actions: return
    ndjson = "\n".join(json.dumps(a, ensure_ascii=False) for a in actions) + "\n"
    r = requests.post(f"{OS_URL}/_bulk", data=ndjson.encode("utf-8"),
                      headers={"Content-Type":"application/x-ndjson"},
                      verify=False, auth=(OS_USER, OS_PASS), timeout=60)
    r.raise_for_status()
    resp = r.json()
    if resp.get("errors"):
        errs = [it for it in resp.get("items", []) if it.get("index",{}).get("error")]
        print(json.dumps(errs[:3], indent=2, ensure_ascii=False), file=sys.stderr)
        raise RuntimeError("bulk had errors")

def main():
    sha_repo = repo_sha()
    files = iter_files()
    print(f"repo={sha_repo} files={len(files)} root={ROOT}")
    t0 = time.time()
    batch = []
    total = 0

    for fp in tqdm(files, desc="ingesting"):
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lines = txt.splitlines(keepends=True)
        chunks = chunk_lines(lines, WINDOW, OVERLP)
        lang = detect_lang(fp)
        sha_blob = file_blob_sha(fp)
        for (start, end, content) in chunks:
            doc = {
                "repo_sha": sha_repo,
                "path": str(fp.relative_to(ROOT)).replace("\\","/"),
                "lang": lang,
                "symbol": None,  # placeholder: podemos enriquecer depois (ctags/tree-sitter)
                "start_line": start,
                "end_line": end,
                "sha_blob": sha_blob,
                "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "content": content
            }
            if USE_EMB and _emb_model:
                vec = _emb_model.encode(content, normalize_embeddings=True).tolist()
                doc["embedding"] = vec
            # id estável = hash(repo_sha + path + start_line + sha_blob)
            uid = hashlib.sha1(f"{sha_repo}|{doc['path']}|{start}|{sha_blob}".encode()).hexdigest()
            meta = {"index": {"_index": INDEX, "_id": uid}}
            batch.append(meta); batch.append(doc)
            if len(batch) >= 1000*2:  # 1000 docs por bulk
                bulk_post(batch); total += 500; batch = []
    if batch: bulk_post(batch); total += len(batch)//2
    dt = time.time() - t0
    print(f"done: {total} chunks in {dt:.1f}s (avg {total/max(dt,1):.1f} docs/s)")

if __name__ == "__main__":
    main()
