# receipts

checks every claim a coding agent makes in its "done" message against what actually ran.

- gemini (gemini-3.8-flash) is the coding agent: writes the code, its tests, and its final message
- the tests are actually run; that output is the session log
- meta muse spark reads the final message + the full log and pulls out each claim, quoting the log line behind it (quotes checked word for word)
- subq snap 1.1 rules on every claim in one call: backed / contradicted / never ran, with probabilities (~0.4 s)

## run

```
printf "META_API_KEY=...\nSUBQ_API_KEY=...\nGEMINI_API_KEY=...\n" > .env
python3 receipts.py
```

results land in `runs_evidence/<id>/` (code, tests, final_message.md, session.log, receipts.json). stdlib only.

## first real run (runs_evidence/ef05668dae)

gemini's message made 7 claims. all 7 were backed by the log (10 tests ran, all ok). nothing planted: when the agent is honest, receipts says so.

sister project: https://github.com/elsisiem/onus
