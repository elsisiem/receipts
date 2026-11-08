"""Record a captioned walkthrough of the live page (Chromium remote debugging on :9222), including one real live run.
usage: ~/aie-hack/.venv/bin/python tools/tour.py http://127.0.0.1:8790/  -> docs/receipts_walkthrough.mp4"""
import base64, json, os, subprocess, sys, time, urllib.request
import websocket, imageio_ffmpeg

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8790/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "receipts_walkthrough.mp4")
FR = "/tmp/receipts_tour"; os.makedirs(FR, exist_ok=True)
for f in os.listdir(FR):
    os.remove(os.path.join(FR, f))

tab = json.load(urllib.request.urlopen(urllib.request.Request(f"http://localhost:9222/json/new?{URL}", method="PUT")))
urllib.request.urlopen(f"http://localhost:9222/json/activate/{tab['id']}")
ws = websocket.create_connection(tab["webSocketDebuggerUrl"], suppress_origin=True, timeout=120)
_i = 0


def call(m, p=None):
    global _i
    _i += 1; ws.send(json.dumps({"id": _i, "method": m, "params": p or {}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == _i:
            return r.get("result", {})


def js(expr):
    return call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}).get("result", {}).get("value")


call("Emulation.setDeviceMetricsOverride", {"width": 1600, "height": 900, "deviceScaleFactor": 1, "mobile": False})
call("Page.navigate", {"url": URL}); time.sleep(4)

OVERLAY = r"""
(() => {
  if (document.getElementById('tour-cap')) return;
  const st = document.createElement('style');
  st.textContent = `#tour-cap{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);z-index:9999;max-width:1100px;width:calc(100% - 80px);
    background:#FBFFC9;color:#11110E;font-family:Satoshi,system-ui,sans-serif;font-size:26px;line-height:1.3;font-weight:500;padding:18px 26px;border-radius:8px;
    box-shadow:0 10px 40px rgba(0,0,0,.5);letter-spacing:-.01em}
    #tour-cap small{display:block;font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:.12em;text-transform:uppercase;opacity:.6;margin-bottom:4px}
    #tour-ring{position:fixed;z-index:9998;border:3px solid #FBFFC9;border-radius:10px;box-shadow:0 0 0 9999px rgba(0,0,0,.55);pointer-events:none;transition:all .35s cubic-bezier(.23,1,.32,1)}
    html{scroll-behavior:auto !important}`;
  document.head.appendChild(st);
  const c = document.createElement('div'); c.id = 'tour-cap'; document.body.appendChild(c);
  const r = document.createElement('div'); r.id = 'tour-ring'; r.style.display = 'none'; document.body.appendChild(r);
})()
"""


def caption(step, text):
    js(OVERLAY)
    js(f"document.getElementById('tour-cap').innerHTML = {json.dumps(f'<small>{step}</small>' + text)}")


def ring(selector, pad=10, scroll=True):
    js(OVERLAY)
    if selector is None:
        js("document.getElementById('tour-ring').style.display='none'"); return
    if scroll:
        js(f"(()=>{{const e=document.querySelector({json.dumps(selector)}); const r=e.getBoundingClientRect(); window.scrollTo(0, Math.max(0, r.top + scrollY - Math.max(90, (innerHeight - 200 - r.height) / 2)));}})()")
        time.sleep(.4)
    js(f"""(()=>{{const e=document.querySelector({json.dumps(selector)}); const r=e.getBoundingClientRect(); const g=document.getElementById('tour-ring');
        g.style.display='block'; g.style.left=(r.left-{pad})+'px'; g.style.top=(r.top-{pad})+'px'; g.style.width=(r.width+2*{pad})+'px'; g.style.height=(r.height+2*{pad})+'px';}})()""")
    time.sleep(.45)


frames = []


def shot(dur):
    d = call("Page.captureScreenshot", {"format": "png"})
    p = os.path.join(FR, f"f{len(frames):04d}.png"); open(p, "wb").write(base64.b64decode(d["data"]))
    frames.append((p, dur))


def hold(sec):
    shot(sec)


# 1. the problem
js("window.scrollTo(0,0)"); ring(None)
caption("the problem", "AI coding agents finish every task with a confident message: <b>“done, all tests pass.”</b> Most people merge on that message.")
hold(5)
caption("what receipts does", "receipts checks every claim in that message against <b>what actually ran</b>, and labels each one: <b>backed</b>, <b>contradicted</b> or <b>never ran</b>.")
hold(5)

# 2. a real catch
js("document.querySelector('#caught').scrollIntoView()"); time.sleep(.6)
ring(".runc")
caption("a real catch", "This is a real pull request by <b>GitHub's own Copilot coding agent</b>, in GitHub's own repo. Nothing planted. Let's open it.")
hold(5)
js("document.querySelector('.runc').click()"); time.sleep(1.5)

# 3. the four steps
for sel, step, text in [
    ('[data-st="agent"]', "step 1 · the agent", "An AI agent does the work and writes the “done” message. Here it is GitHub Copilot. In a live run, it's <b>Google Gemini</b>."),
    ('[data-st="run"]', "step 2 · the evidence", "The log of what <b>actually ran</b>: here, the PR's real CI checks and their failure logs."),
    ('[data-st="muse"]', "step 3 · meta muse spark", "<b>Meta Muse</b> reads the message and the whole log, finds every claim, and quotes the log line behind each one."),
    ('[data-st="snap"]', "step 4 · subquadratic snap", "<b>SubQ Snap</b> rules on every claim in one call, in about half a second: backed, contradicted or never ran."),
]:
    ring(sel); caption(step, text); hold(4.5)

# 4. the verdict
ring(".tally"); caption("the verdict", "2 claims are <b>contradicted</b> by the PR's own CI. 5 more were never checked by anything.")
hold(4.5)
ring('.msg mark.v-contradicted', 6)
caption("what the agent said", "The agent wrote: <b>“make agent-report-progress passed, including … impacted tests.”</b>")
hold(5)
js("document.querySelector('.claim').click()"); time.sleep(.6)
js("document.querySelector('#log').scrollIntoView({block:'center'})"); time.sleep(.3)
ring('#hl', 6, scroll=False)
caption("what actually happened", "The same PR's CI: <b>failure impacted-go-tests</b>. The agent's claim is false, and receipts shows the exact line.")
hold(5.5)

# 5. a live run, for real
js("window.scrollTo(0,0)"); time.sleep(.4)
js("document.querySelector('.task[data-k=\"business-days\"]').click()"); time.sleep(.3)
ring(".runbar", 8, scroll=False)
caption("now live", "Your turn: pick a ticket and press <b>Run it</b>. Gemini writes the code live, and receipts checks it.")
hold(4)
js("document.getElementById('go').click()"); time.sleep(1.2)
ring(None)
t0 = time.time(); last = None
labels = {"agent": "Gemini is writing the code, its tests and its “done” message…", "run": "Running the agent's tests for real…",
          "muse": "Meta Muse is reading the message and the log, finding every claim…", "snap": "SubQ Snap is ruling on every claim…"}
while time.time() - t0 < 240:
    active = js("(document.querySelector('.st.active')||{}).dataset?.st || ''")
    if active and active != last:
        last = active
    if active:
        ring(f'[data-st="{active}"]', 8, scroll=False)
        caption(f"live run · {int(time.time() - t0)} s (sped up)", labels[active])
        shot(0.35)
    elif js("document.getElementById('go').disabled") is False and last:
        break
    time.sleep(0.7)
time.sleep(1.5)
ring(".tally"); caption("live result", js("document.getElementById('big').innerText") + ". Every run, honest or not, is saved with its code, tests and log.")
hold(5)
ring(".runbar", 8)
caption("try it yourself", "Paste any agent's message and log under <b>Paste your own</b>. Live at <b>receipts-check.fly.dev</b>")
hold(5)

# assemble
lst = os.path.join(FR, "list.txt")
with open(lst, "w") as f:
    for p, d in frames:
        f.write(f"file '{p}'\nduration {d}\n")
    f.write(f"file '{frames[-1][0]}'\n")
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20", OUT],
               check=True, capture_output=True)
print(OUT, sum(d for _, d in frames), "s,", len(frames), "frames")
call("Page.close") if False else None
