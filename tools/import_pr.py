"""Import a REAL public pull request written by a coding agent: the PR description is the agent's final message,
the failing CI job logs are the session log. Then receipts judges it (Muse claims, Snap rulings).
usage: python3 tools/import_pr.py https://github.com/OWNER/REPO/pull/N"""
import json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
import receipts
GH = os.environ.get("GH", "gh")


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True, timeout=120).stdout


def main(url):
    owner, repo, n = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", url).groups()
    d = json.loads(sh(GH, "pr", "view", url, "--json", "body,title,author,statusCheckRollup,headRefOid"))
    checks = d.get("statusCheckRollup") or []
    lines = [f"$ gh pr checks {url}"]
    for c in checks:
        lines.append(f"{(c.get('conclusion') or c.get('state') or c.get('status') or '').lower():10} {c.get('name') or c.get('context')}")
    for c in checks:
        if (c.get("conclusion") or c.get("state")) not in ("FAILURE", "ERROR"):
            continue
        m = re.search(r"/actions/runs/\d+/job/(\d+)", c.get("detailsUrl") or "")
        if not m:
            continue
        log = sh(GH, "run", "view", "-R", f"{owner}/{repo}", "--job", m.group(1), "--log-failed")
        keep = [l.split("\t", 2)[-1] for l in log.splitlines()]
        keep = [re.sub(r"^\S+Z ", "", l) for l in keep if re.search(r"FAIL|fail|Error|✗|×|expected|Tests? |passed|failed", l)][-60:]
        lines.append(f"\n$ gh run view --job {m.group(1)} --log-failed   # {c.get('name')}\n" + "\n".join(keep))
    rid = f"gh-{owner}-{repo}-{n}".lower()[:60]
    out = os.path.join(receipts.RUNS, rid); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "final_message.md"), "w").write((d.get("body") or "").strip())
    open(os.path.join(out, "session.log"), "w").write("\n".join(lines))
    json.dump({"source": "real public PR", "agent": f"{(d.get('author') or {}).get('login', 'agent')} (GitHub Copilot coding agent)",
               "task_title": f"{owner}/{repo}#{n}: {d['title']}", "spec": url, "url": url, "module": None},
              open(os.path.join(out, "meta.json"), "w"), indent=1)
    r = receipts.recheck(out)
    print(rid, r["counts"])
    for c in r["claims"]:
        print(f"  {c['verdict']:13} {c['confidence']:.2f} | {c['claim']} | {c.get('log_quote')}")


if __name__ == "__main__":
    for u in sys.argv[1:]:
        main(u)
