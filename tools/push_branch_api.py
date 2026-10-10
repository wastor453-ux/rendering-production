#!/usr/bin/env python3
"""Push the current branch's new commit(s) via the Git Data API.

Used because this environment has no git HTTPS credential; the
established pattern (push_p40_branch.py) uses the skill credential.
Pushes ONLY the files changed in local commits ahead of the remote
branch, onto p4-4-complete-preproduction-closure (never main).
"""
import sys, os, json, base64, urllib.request, urllib.error

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

REPO = "wastor453-ux/rendering-production"
BASE = "https://api.github.com"
ALLOWED = ["api.github.com"]
BRANCH = "p4-4-complete-preproduction-closure"
WORKDIR = os.path.expanduser("~/workspace/crackit/demo-video")


def api(method, path, payload=None, timeout=60, retries=4):
    import time
    body = json.dumps(payload).encode() if payload is not None else None
    last_err = None
    for attempt in range(retries):
        req = urllib.request.Request(BASE + path, data=body, method=method)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "cosmo-branch-sync")
        if body:
            req.add_header("Content-Type", "application/json")
        add_surrogate_to_request(req, "custom.github", allowed_hosts=ALLOWED)
        try:
            return read_json_response(urllib.request.urlopen(req, timeout=timeout))
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code} on {method} {path}: {e.read().decode()[:500]}",
                  file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            last_err = e
            wait = 2 ** attempt
            print(f"  retry {attempt+1}/{retries} after {e.__class__.__name__} ({wait}s)",
                  file=sys.stderr)
            time.sleep(wait)
    print(f"FATAL: {method} {path} failed after {retries} retries: {last_err}",
          file=sys.stderr)
    sys.exit(1)


def main():
    os.chdir(WORKDIR)
    # Files changed in local commits ahead of remote branch
    import subprocess
    diff = subprocess.run(
        ["git", "log", f"origin/{BRANCH}..HEAD", "--name-only", "--format="],
        capture_output=True, text=True)
    # Fallback: if origin ref unknown locally, use the HEAD commit's files
    files = sorted(set(f for f in diff.stdout.splitlines() if f.strip()))
    if not files:
        out = subprocess.run(["git", "show", "--name-only", "--format=", "HEAD"],
                             capture_output=True, text=True)
        files = sorted(set(f for f in out.stdout.splitlines() if f.strip()))
    # Never push bytecode/caches
    files = [f for f in files if "__pycache__" not in f and not f.endswith(".pyc")]
    print(f"Pushing {len(files)} files to {BRANCH}")

    ref = api("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}")
    base_sha = ref["object"]["sha"]
    base_commit = api("GET", f"/repos/{REPO}/git/commits/{base_sha}")
    base_tree = base_commit["tree"]["sha"]
    print(f"Remote {BRANCH}: {base_sha[:8]}")

    tree_entries = []
    for f in files:
        path = os.path.join(WORKDIR, f)
        # Handle deletions
        if not os.path.isfile(path):
            tree_entries.append({"path": f, "mode": "100644", "type": "blob", "sha": None})
            print(f"  delete {f}")
            continue
        with open(path, "rb") as fh:
            content = fh.read()
        blob = api("POST", f"/repos/{REPO}/git/blobs",
                   {"content": base64.b64encode(content).decode(), "encoding": "base64"},
                   timeout=300 if len(content) > 10*1024*1024 else 60)
        # Preserve executable bit for scripts
        mode = "100755" if os.access(path, os.X_OK) and f.endswith(".sh") else "100644"
        tree_entries.append({"path": f, "mode": mode, "type": "blob", "sha": blob["sha"]})
        print(f"  blob {f}: {blob['sha'][:8]}")

    # Get local commit message
    msg = subprocess.run(["git", "log", "-1", "--format=%B", "HEAD"],
                         capture_output=True, text=True).stdout.strip()

    new_tree = api("POST", f"/repos/{REPO}/git/trees",
                   {"base_tree": base_tree, "tree": tree_entries})
    new_commit = api("POST", f"/repos/{REPO}/git/commits",
                     {"message": msg, "tree": new_tree["sha"], "parents": [base_sha]})
    api("PATCH", f"/repos/{REPO}/git/refs/heads/{BRANCH}", {"sha": new_commit["sha"]})
    print(f"Branch {BRANCH} updated: {new_commit['sha'][:8]}")


if __name__ == "__main__":
    main()
