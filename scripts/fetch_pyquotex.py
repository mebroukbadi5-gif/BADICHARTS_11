"""Fetch the official pyquotex library source files from GitHub for analysis."""
import json
import os
import urllib.request

BASE = "/home/z/my-project/research/pyquotex"
os.makedirs(BASE, exist_ok=True)
os.chdir(BASE)

REPO = "cleitonleonel/pyquotex"


def get(url, dest=None, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    if dest:
        with open(dest, "wb") as f:
            f.write(data)
    return data


branch = "main"
try:
    info = json.loads(get(f"https://api.github.com/repos/{REPO}"))
    branch = info.get("default_branch", "main") or "main"
    print("default_branch:", branch)
    print("description:", info.get("description"))
except Exception as e:
    print("repo_info err:", repr(e))

try:
    tree = json.loads(get(f"https://api.github.com/repos/{REPO}/git/trees/{branch}?recursive=1"))
    paths = [t["path"] for t in tree.get("tree", []) if t.get("type") == "blob"]
    print("total files:", len(paths))
    for p in paths:
        if p.endswith((".py", ".md", ".txt", ".toml")):
            print("  ", p)
except Exception as e:
    print("tree err:", repr(e))

core = ["quotex.py", "api.py", "login.py", "settings.py", "global_value.py",
        "http_resource.py", "exceptions.py", "browser.py", "__init__.py"]
for name in core:
    try:
        get(f"https://raw.githubusercontent.com/{REPO}/{branch}/quotexapi/{name}", f"quotexapi_{name}")
        print("fetched quotexapi/" + name)
    except Exception as e:
        print(f"fetch {name} err:", repr(e))

for name in ["README.md", "requirements.txt", "pyproject.toml", "setup.py"]:
    try:
        get(f"https://raw.githubusercontent.com/{REPO}/{branch}/{name}", name)
        print("fetched " + name)
    except Exception as e:
        print(f"fetch {name} err:", repr(e))

print("--- downloaded sizes ---")
for f in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, f)
    if os.path.isfile(p):
        print(f"{f}: {os.path.getsize(p)} bytes")
