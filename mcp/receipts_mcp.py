#!/usr/bin/env python3
"""receipts as an MCP server: give any agent (Claude Code, Cursor, Codex, Windsurf, ...) a tool that checks its own
"done" message against what actually ran, before it tells you it's done.

Standard library only. Speaks MCP over stdio (JSON-RPC 2.0, newline-delimited).
The checking itself (Meta Muse Spark finds the claims, Subquadratic Snap rules on them) runs on the receipts API,
so you need no model keys. Point RECEIPTS_URL at your own deployment to self-host.

Tools
  receipts_check(message, log)                 check a final message against a log you already have
  receipts_run_and_check(message, command, cwd) run a command (your tests), capture its output, then check
"""
import json, os, subprocess, sys, urllib.request, urllib.error

URL = os.environ.get("RECEIPTS_URL", "https://receipts-check.fly.dev").rstrip("/")
VERSION = "0.1.0"

TOOLS = [
    {"name": "receipts_check",
     "description": ("Check every claim in a coding agent's final message against a log of what actually ran. Returns each claim as "
                     "backed, contradicted or never ran, with the log line that proves it. Call this BEFORE telling the user a task "
                     "is done, passing the summary you are about to send and the real terminal/CI output."),
     "inputSchema": {"type": "object", "required": ["message", "log"], "properties": {
         "message": {"type": "string", "description": "The final message you are about to send the user (what you did, what passes)."},
         "log": {"type": "string", "description": "Real output: terminal commands and their output, test runs, CI logs."}}}},
    {"name": "receipts_run_and_check",
     "description": ("Run a verification command (for example the test suite), capture its real output, and check the final message "
                     "against it. Use this when you have not run the tests yet or want fresh evidence."),
     "inputSchema": {"type": "object", "required": ["message", "command"], "properties": {
         "message": {"type": "string", "description": "The final message you are about to send the user."},
         "command": {"type": "string", "description": "Shell command that produces the evidence, e.g. 'pytest -q' or 'npm test'."},
         "cwd": {"type": "string", "description": "Working directory for the command (default: current directory)."},
         "timeout_s": {"type": "integer", "description": "Command timeout in seconds (default 300)."}}}},
]


def _api(message, log):
    req = urllib.request.Request(f"{URL}/api/check", data=json.dumps({"message": message, "log": log[-150_000:]}).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": f"receipts-mcp/{VERSION}"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:300]}"}


def _report(r):
    if "error" in r:
        return f"receipts could not check this: {r['error']}", True
    c = r["counts"]
    lines = [f"receipts: {c.get('backed', 0)} backed, {c.get('contradicted', 0)} contradicted, {c.get('never_ran', 0)} never ran."]
    for cl in r["claims"]:
        mark = {"backed": "BACKED", "contradicted": "CONTRADICTED", "never_ran": "NEVER RAN"}[cl["verdict"]]
        q = f' | log: "{cl["log_quote"]}"' if cl.get("log_quote") else " | log: nothing"
        lines.append(f"- {mark} ({cl['confidence']:.0%}) {cl['claim']}{q}")
    if c.get("contradicted") or c.get("never_ran"):
        lines.append("Fix or remove contradicted claims, and either verify or soften never-ran claims, before reporting to the user.")
    lines.append(f"Full receipts: {URL}/#caught (run {r['id']})")
    return "\n".join(lines), False


def call_tool(name, a):
    if name == "receipts_check":
        return _report(_api(a["message"], a["log"]))
    if name == "receipts_run_and_check":
        cwd = a.get("cwd") or os.getcwd()
        try:
            p = subprocess.run(a["command"], shell=True, cwd=cwd, capture_output=True, text=True, timeout=int(a.get("timeout_s") or 300))
            log = f"$ {a['command']}\n{(p.stdout + p.stderr).strip()}\n[exit code {p.returncode}]"
        except subprocess.TimeoutExpired:
            log = f"$ {a['command']}\nTIMEOUT after {a.get('timeout_s') or 300} s\n[exit code 124]"
        text, err = _report(_api(a["message"], log))
        return text + "\n\nEvidence captured:\n" + log[-3000:], err
    return f"unknown tool {name}", True


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        msg = json.loads(line)
        mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
        if method == "initialize":
            res = {"protocolVersion": params.get("protocolVersion", "2025-06-18"), "capabilities": {"tools": {}},
                   "serverInfo": {"name": "receipts", "version": VERSION}}
        elif method == "tools/list":
            res = {"tools": TOOLS}
        elif method == "tools/call":
            try:
                text, err = call_tool(params["name"], params.get("arguments") or {})
            except Exception as e:
                text, err = f"{type(e).__name__}: {e}", True
            res = {"content": [{"type": "text", "text": text}], "isError": err}
        elif method == "ping":
            res = {}
        elif mid is None:
            continue  # notifications (initialized, cancelled, ...)
        else:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"no method {method}"}}) + "\n"); sys.stdout.flush()
            continue
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": res}) + "\n"); sys.stdout.flush()


if __name__ == "__main__":
    main()
