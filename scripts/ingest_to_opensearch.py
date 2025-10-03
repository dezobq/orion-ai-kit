#!/usr/bin/env python3
import os, sys, json, glob, requests
OS_URL = os.environ.get("OS_URL", "http://localhost:9200")
INDEX = os.environ.get("OS_INDEX", "docs")
def create_index():
    import requests
    requests.put(f"{OS_URL}/{INDEX}", json={
        "settings": {"number_of_shards": 1},
        "mappings": {"properties": {"path": {"type": "keyword"}, "text": {"type": "text"}}}
    })
def index_folder(folder="docs"):
    files = glob.glob(os.path.join(folder, "**/*"), recursive=True)
    for p in files:
        if os.path.isdir(p): continue
        try:
            txt = open(p, "r", errors="ignore").read()
        except Exception:
            continue
        import requests
        requests.post(f"{OS_URL}/{INDEX}/_doc", json={"path": p, "text": txt})
if __name__ == "__main__":
    create_index()
    index_folder(sys.argv[1] if len(sys.argv)>1 else "docs")
    print("Done.")
