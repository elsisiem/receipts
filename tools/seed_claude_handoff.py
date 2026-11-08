"""Seed a REAL agent session: Claude (Claude Code, Opus) handing off the ONUS build on 2026-11-07.
The final message is copied verbatim from the session transcript. The log is produced here by actually running the
commands a reviewer would run, against a checkout of the repo at the exact commit the agent was describing (2ccf07e)."""
import json, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONUS = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/aie-hack/onus")
TRANSCRIPT = sys.argv[2] if len(sys.argv) > 2 else None
COMMIT = "2ccf07e"

msg = None
for line in open(TRANSCRIPT):
    d = json.loads(line); m = d.get("message", {})
    if m.get("role") == "assistant" and isinstance(m.get("content"), list):
        for c in m["content"]:
            if isinstance(c, dict) and c.get("text", "").startswith("Everything is committed: 12 atomic commits"):
                msg = c["text"]
msg = msg.split("## Why ONUS")[0].strip()

wt = tempfile.mkdtemp(prefix="receipts-wt-")
subprocess.run(["git", "-C", ONUS, "worktree", "add", "--detach", wt, COMMIT], check=True, capture_output=True)
os.makedirs(os.path.join(wt, "runs"), exist_ok=True)
os.symlink(os.path.join(ONUS, "runs", "vol3_paged.txt"), os.path.join(wt, "runs", "vol3_paged.txt"))
cmds = [
    ("git log --oneline | wc -l", wt),
    ("git log --oneline", wt),
    ("cd evidence/live/821d4106ab && python -m unittest -v test_impl", wt),
    ("python tools/verify.py", wt),
    ("openssl ts -reply -in law/sealed_suite.tsr -text | grep -i status", wt),
    ("python -c \"from onus import oracle, live_pr; r=oracle.run_sealed_external(lambda c: live_pr.run_cases('evidence/live/821d4106ab', c)); "
     "print('sealed failures:', [f['id'] for f in r['failed']])\"", wt),
]
log = []
env = {**os.environ, "PYTHONPATH": wt}
for cmd, cwd in cmds:
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=120, env=env,
                       executable="/bin/bash")
    out = (p.stdout + p.stderr).strip().replace(wt, "~/onus")
    log.append(f"$ {cmd}\n{out}\n[exit code {p.returncode}]")
subprocess.run(["git", "-C", ONUS, "worktree", "remove", "--force", wt], capture_output=True)

d = os.path.join(ROOT, "runs_evidence", "claude-onus-handoff"); os.makedirs(d, exist_ok=True)
open(os.path.join(d, "final_message.md"), "w").write(msg)
open(os.path.join(d, "session.log"), "w").write("\n\n".join(log))
json.dump({"source": "real agent session", "agent": "Claude Code (Opus), building ONUS",
           "task_title": "Real handoff message from the agent that built ONUS (github.com/elsisiem/onus)",
           "spec": f"Final message copied verbatim from the session transcript. Log = commands re-run by receipts on the repo at commit {COMMIT}, the commit the message describes.",
           "module": None}, open(os.path.join(d, "meta.json"), "w"), indent=1)
print("\n\n".join(log))
