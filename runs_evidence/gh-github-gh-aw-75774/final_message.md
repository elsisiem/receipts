## Summary

- Export only schema-defined boolean findings (`prompt_injection`, `secret_leak`, `malicious_patch`) from both inline and external detector conclusion paths, and propagate them to safe-output and conclusion jobs.
- Include framework-authored threat types in generated issue/body warnings, strict-failure notifications, tracking comments, request-changes reviews, converted review PRs, expired-entity warnings, and blocked-output messages. Never use detector-generated explanations as public threat details; unknown categories are omitted, and missing types are reported explicitly.
- Preserve distinct detector-error warnings and threat markers. Use typed report blocks in the updated publication paths, document the message placeholders, and regenerate workflow locks. The 317 generated lock-file changes only add category outputs and environment wiring.

## Validation

- `make agent-report-progress` passed, including Go/custom/JavaScript/shell lint, impacted tests, schema freshness, and full workflow drift checking.
- `make recompile`: 361/361 workflows compiled successfully.
- Focused Vitest publication suites: 1,102 tests passed; an additional generated-issue regression passed, and the final gate ran 747 impacted JavaScript tests.
- `npm run typecheck` passed.
- `go test ./pkg/workflow -run '^(TestConcludeThreatDetectionScript_.*|TestDetectionJobHasSuccessOutput|TestSafeOutputJobsCheckDetectionSuccess|TestDetectionRunsStepInConclusionJob)$' -count=1` passed.

No workflows were dispatched.