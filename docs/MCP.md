# receipts MCP server

Give your coding agent a tool that checks its own "done" message against what actually ran, **before** it tells you it's done.

- One file: [`mcp/receipts_mcp.py`](../mcp/receipts_mcp.py). Python standard library only.
- Speaks MCP over stdio. Works with Claude Code, Cursor, Codex, Windsurf, or any MCP client.
- No model keys needed. The checking (Meta Muse Spark finds the claims, Subquadratic Snap rules on them) runs on the receipts API at `https://receipts-check.fly.dev`. Set `RECEIPTS_URL` to use your own deployment.

## Install

**Claude Code**
```bash
curl -o ~/receipts_mcp.py https://raw.githubusercontent.com/elsisiem/receipts/master/mcp/receipts_mcp.py
claude mcp add receipts -- python3 ~/receipts_mcp.py
```

**Cursor, Windsurf, or any client with an `mcpServers` config**
```json
{
  "mcpServers": {
    "receipts": { "command": "python3", "args": ["/path/to/receipts_mcp.py"] }
  }
}
```

**Make it automatic.** Add this to `CLAUDE.md`, `AGENTS.md` or `.cursorrules`:
```
Before you tell me a task is done, call receipts_run_and_check with the message you are
about to send and the test command. Fix or drop any claim it marks CONTRADICTED or NEVER RAN.
```

## Tools

| tool | arguments | what it does |
|---|---|---|
| `receipts_run_and_check` | `message`, `command`, `cwd?`, `timeout_s?` | Runs `command` (e.g. `pytest -q`, `npm test`) locally, captures the real output and exit code, then checks `message` against it. |
| `receipts_check` | `message`, `log` | Checks `message` against a log you already have (CI output, a terminal session). |

## What the agent gets back

This is a real response (the command printed `FAILED (failures=2)`):

```
receipts: 0 backed, 1 contradicted, 2 never ran.
- CONTRADICTED (100%) All 12 tests pass | log: "FAILED (failures=2)"
- NEVER RAN (99%) Added the parser | log: nothing
- NEVER RAN (100%) lint is clean | log: nothing
Fix or remove contradicted claims, and either verify or soften never-ran claims, before reporting to the user.
```

## HTTP API (what the MCP server calls)

```
POST https://receipts-check.fly.dev/api/check
{"message": "<the agent's final message>", "log": "<what actually ran>"}
-> {"id", "counts": {"backed", "contradicted", "never_ran"}, "claims": [{"claim", "says", "log_quote", "quote_verified", "verdict", "confidence", "probabilities"}], "latency_ms", "models"}
```

Limits on the public deployment: two checks at a time, and one per client every 5 s. Logs are trimmed to their last 150,000 characters.

## Privacy

The message and the log are sent to the receipts API, which forwards them to Meta (Muse Spark) and Subquadratic (Snap) and stores the result as a run. Don't send secrets. Self-host (`python3 server.py` with your own keys) if your logs are private.
