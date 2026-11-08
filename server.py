"""receipts web: python3 server.py -> shows every recorded agent run and its claim-by-claim verdicts."""
import json, os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
ROOT = os.path.dirname(os.path.abspath(__file__)); RUNS = os.path.join(ROOT, "runs_evidence")

def runs():
    out = []
    for x in os.listdir(RUNS):
        p = os.path.join(RUNS, x, "receipts.json")
        if os.path.exists(p):
            d = json.load(open(p)); d["_bad"] = d["counts"].get("contradicted", 0) + d["counts"].get("never_ran", 0); out.append(d)
    return sorted(out, key=lambda d: (-d["_bad"], d["checked_at"]))

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/runs"):
            b = json.dumps(runs()).encode(); t = "application/json"
        else:
            b = open(os.path.join(ROOT, "index.html"), "rb").read(); t = "text/html; charset=utf-8"
        self.send_response(200); self.send_header("Content-Type", t); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

if __name__ == "__main__":
    ThreadingHTTPServer((os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8790"))), H).serve_forever()
