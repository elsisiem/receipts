"""receipts web: python3 server.py -> http://127.0.0.1:8790
GET  /                 the page
GET  /api/runs         every recorded run, lies first
GET  /api/tasks        tasks the live agent can be given
POST /api/run          streams one event per pipeline step (text/event-stream)
     {"mode": "agent", "task": "checkout"}  or  {"mode": "paste", "message": "...", "log": "..."}"""
import json, os, threading, time, traceback
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import receipts

ROOT = os.path.dirname(os.path.abspath(__file__))
BUSY = threading.Semaphore(2)          # at most two live runs at once (they spend real API credits)
LAST_BY_IP, COOLDOWN = {}, 20


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        print("[receipts]", fmt % a, flush=True)

    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/api/runs"):
            return self._send(200, receipts.runs())
        if self.path.startswith("/api/tasks"):
            return self._send(200, {k: {"title": v["title"], "spec": v["spec"]} for k, v in receipts.TASKS.items()})
        if self.path in ("/", "/index.html"):
            return self._send(200, open(os.path.join(ROOT, "index.html"), "rb").read(), "text/html; charset=utf-8")
        if self.path in ("/logo.svg", "/docs/logo.svg"):
            return self._send(200, open(os.path.join(ROOT, "docs", "logo.svg"), "rb").read(), "image/svg+xml")
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/run":
            return self._send(404, {"error": "not found"})
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(min(n, 400_000)) or b"{}")
        except ValueError:
            return self._send(400, {"error": "bad json"})
        mode = body.get("mode", "agent")
        if mode == "agent" and body.get("task", "checkout") not in receipts.TASKS:
            return self._send(400, {"error": "unknown task"})
        if mode == "paste" and not (body.get("message", "").strip() and body.get("log", "").strip()):
            return self._send(400, {"error": "paste both the agent's final message and the log"})
        ip = self.headers.get("Fly-Client-IP") or self.client_address[0]
        if time.time() - LAST_BY_IP.get(ip, 0) < COOLDOWN:
            return self._send(429, {"error": f"one run every {COOLDOWN} s, please wait"})
        if not BUSY.acquire(blocking=False):
            return self._send(429, {"error": "two runs are already in progress, try again in a minute"})
        LAST_BY_IP[ip] = time.time()
        try:
            self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.send_header("Cache-Control", "no-store")
            self.send_header("X-Accel-Buffering", "no"); self.end_headers()
            gen = receipts.stream(mode, body.get("task", "checkout"), body.get("message"), body.get("log"))
            try:
                for ev in gen:
                    self.wfile.write(f"data: {json.dumps(ev)}\n\n".encode()); self.wfile.flush()
            except Exception as e:
                traceback.print_exc()
                self.wfile.write(f"data: {json.dumps({'stage': 'error', 'error': f'{type(e).__name__}: {e}'[:300]})}\n\n".encode())
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            BUSY.release()


if __name__ == "__main__":
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8790"))
    print(f"receipts on http://{host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), H).serve_forever()
