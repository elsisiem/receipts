<p align="center"><img src="docs/logo.svg" width="72" alt="receipts logo"></p>

<h1 align="center">receipts</h1>

<p align="center"><b>Your coding agent says “done, all tests pass.” Check the receipts.</b></p>

<p align="center">
  <a href="https://receipts-check.fly.dev"><b>Live: receipts-check.fly.dev</b></a> ·
  <a href="https://receipts-check.fly.dev/demo">Guided demo</a> ·
  <a href="docs/MCP.md">Add to your agent (MCP)</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#what-it-caught">What it caught</a> ·
  <a href="#run-it-yourself">Run it</a>
</p>

![receipts catching a GitHub Copilot coding-agent PR](docs/caught.png)

Coding agents finish every task with a confident summary: *"Implemented X. All 42 tests pass. Typecheck clean."* Most people merge on that message. **receipts** checks every claim in it against what actually ran and labels each one:

| verdict | meaning |
|---|---|
| **backed** | the log has output that proves it |
| **contradicted** | the log has output showing it is false |
| **never ran** | nothing in the log could prove it; the agent never ran anything that checks it |

## How it works

Four steps. The page animates each one live, so you can see which sponsor model is working and how long it takes.

| step | who | what it does | why it has to be this model |
|---|---|---|---|
| **01 Agent** | **Google Gemini** `gemini-3.8-flash` | Gets a ticket. Writes the code, its own tests, and the “done” message it would send you. | It is the coding agent being checked. Any agent works here; Gemini is the live one. |
| **02 Run** | sandbox `python -m unittest` | Actually executes the agent's tests. That output is the session log. | The log is the only evidence. Nobody takes the agent's word. |
| **03 Read** | **Meta** `muse-spark-1.3` | Reads the final message plus the **whole** log, lists every checkable claim, and quotes the exact log line behind each one. Quotes are checked word for word against the log. | Real CI logs are long (the GitHub case below is ~400 lines across 4 failed jobs). Muse takes the full log in one call, so nothing gets chunked and lost. |
| **04 Rule** | **Subquadratic** `subq-snap-1.1` | One call rules on every claim: backed, contradicted or never ran, with a probability for each. About 0.4 s. | Snap is a decision model: it returns a choice with calibrated probabilities, not prose. That's what a merge gate needs. |

## Add it to your agent (MCP)

receipts is also an MCP server, so your agent checks itself **before** it tells you it's done. It's one file with no dependencies and needs no model keys:

```bash
curl -o ~/receipts_mcp.py https://raw.githubusercontent.com/elsisiem/receipts/master/mcp/receipts_mcp.py
claude mcp add receipts -- python3 ~/receipts_mcp.py
```

Tools: `receipts_run_and_check(message, command)` runs your tests and checks the message against the real output. `receipts_check(message, log)` checks against a log you already have. Cursor, Windsurf, the automatic setup and the API are covered in **[docs/MCP.md](docs/MCP.md)**.

## Demo

- **[/demo](https://receipts-check.fly.dev/demo)**: a keyboard-driven walkthrough of the live site. Press → / space to advance. Each step scrolls to the exact spot, spotlights it, and shows one line to say. Step 8 is the moment GitHub's agent gets caught. N hides the notes, Esc exits.
- **[docs/receipts_walkthrough.mp4](docs/receipts_walkthrough.mp4)**: a 65 s captioned recording with a real live run, made by `tools/tour.py`.

There are three ways to use it:
- **Live agent:** pick a ticket and watch Gemini write the code, then watch receipts check it.
- **Paste your own:** paste any agent's final message and its log (Claude Code, Cursor, Copilot, Devin). receipts skips steps 01–02.
- **Import a real PR:** `python3 tools/import_pr.py <github PR url>` uses the PR description as the message and the failed CI job logs as the log.

## What it caught

Every run in the gallery really happened; nothing is planted. Results so far:

**A GitHub Copilot coding-agent PR in GitHub's own repo** ([github/gh-aw#75774](https://github.com/github/gh-aw/pull/75774)):

> “`make agent-report-progress` passed, including Go/custom/JavaScript/shell lint, **impacted tests**, …”

The same PR's CI shows `failure impacted-go-tests` with `FAIL github.com/github/gh-aw/pkg/workflow`. receipts ruled the claim **contradicted** (82%). It also flagged five other claims as **never ran**: CI has no output for "361/361 workflows compiled", "1,102 Vitest tests passed" and similar.
*Fairness note:* Snap also ruled a narrowly filtered `go test -run '^(...)$'` claim contradicted. The failing CI test was a different test in the same package, so that ruling is debatable. The agent may have run those tests locally, which makes the claim **never ran** on this evidence, not proven false.

**A Copilot PR in CherryHQ/cherry-studio** ([#23837](https://github.com/CherryHQ/cherry-studio/pull/23837)): it claims "42 tests pass" and "13 tests passed" while CI's `renderer-test` job failed. All 7 claims were ruled **never ran**: none of the test counts it quotes appear in any CI output.

**Live Gemini runs:** six runs over three tickets. Gemini was honest about its tests every time. All tests ran and passed, and receipts backed those claims. In three runs it also claimed things nobody checked ("uses only the standard library", "tax rate is 8.25%"), and receipts marked those **never ran**. When the agent is honest, receipts says so.

## Run it yourself

Standard library only. Python 3.10+.

```bash
git clone https://github.com/elsisiem/receipts && cd receipts
printf "META_API_KEY=...\nSUBQ_API_KEY=...\nGEMINI_API_KEY=...\n" > .env
python3 server.py                 # http://127.0.0.1:8790
python3 receipts.py --task checkout-hard        # one live run from the terminal
python3 tools/import_pr.py https://github.com/OWNER/REPO/pull/N   # needs the gh CLI
```

Each run is saved under `runs_evidence/<id>/` with `final_message.md`, `session.log`, the code and tests (live runs) and `receipts.json`.

| file | what |
|---|---|
| `receipts.py` | the pipeline: Gemini agent, sandbox run, Muse claims, Snap rulings, streamed as events |
| `server.py` | stdlib HTTP server; `POST /api/run` streams each step to the page (server-sent events); `POST /api/check` returns JSON for the MCP server; `/demo` is presenter mode |
| `index.html` | the page |
| `tools/import_pr.py` | import a real agent-written PR and its CI logs |
| `mcp/receipts_mcp.py` | the MCP server (stdio, standard library only) |
| `tools/tour.py` | records the captioned walkthrough video |
| `runs_evidence/` | every recorded run |

**Deploy:** `fly deploy`. The keys are Fly secrets. The public site allows two live runs at a time and one run per visitor every 20 s, because every run spends real API credits.

## Limits, honestly

- Rulings are only as good as the log. If the agent ran something on its own machine and didn't share the output, receipts says **never ran**, not "false".
- Snap sometimes misses a line that does back a claim. One example: "`npm run typecheck` passed" was ruled never ran, although CI shows `success js-typecheck`. The quoted log line is always shown next to the verdict so a human can check it in a second.
- Live agent code runs in a subprocess with a 30 s timeout inside a throwaway container, not a hardened sandbox.

## Also built today: ONUS

We started the day on **[ONUS](https://github.com/elsisiem/onus)** ([live](https://onus-registry.fly.dev)), a merge gate for AI-written code that implements law. It used the same idea: never trust the agent's own tests, check against an independent source. The example (Australia's Robodebt) was too niche, so we pivoted to receipts, which applies that idea to every coding agent.

<sub>Built at the AIE Code Summit 2026 Hackathon (Cerebral Valley), 7 Nov 2026. Agent: Google Gemini. Claims: Meta Muse Spark. Rulings: Subquadratic Snap.</sub>
