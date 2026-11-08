### What this PR does

Before this PR: Complete model files with a missing shared runtime showed only the generic “not downloaded” status.

After this PR:
- The status remains `not_downloaded`, with an optional `missing_shared_runtime` hint:
  ```ts
  { status: 'not_downloaded', hintCode: 'missing_shared_runtime' }
  ```
- The model card explains that the shared runtime is missing and keeps the download action available.
- The message is translated in all renderer locales.

### Why we need it and why it was done in this way

A generic status hid why existing model files could not be used. The optional hint makes the cause clear without adding a status value or changing existing download behavior.

The following tradeoffs were made:

- Keep `not_downloaded` and its existing consumer behavior; carry the explanation separately as `hintCode`.

The following alternatives were considered:

- A new status value, which would require updating consumers that branch on `not_downloaded`.

Links to places where the discussion took place: N/A

### Agent Note / Spec

Agent Note: N/A — preserves existing status and action semantics; adds diagnostic metadata.

Spec PR: N/A — local bug fix.

Acceptance criteria: N/A — no Spec ACs.

### Verification

- Regression — `BundleInstaller.test.ts`, `LocalModelService.test.ts`, and `localModel.test.ts`: 42 tests passed.
- Regression — `LocalModelsSection.test.tsx`: 13 tests passed.
- `pnpm i18n:check` and `pnpm docs:check` passed.

### Breaking changes

None.

### Special notes for your reviewer

The hint is included when bundle files are complete but a required shared artifact is missing.

### Checklist

This checklist is not enforcing, but it's a reminder of items that could be relevant to every PR.
Approvers are expected to review this list.

- [ ] Branch: This PR targets `main`
- [ ] PR: The PR description is expressive enough and will help future contributors
- [ ] Code: [Write code that humans can understand](https://en.wikiquote.org/wiki/Martin_Fowler#code-for-humans) and [Keep it simple](https://en.wikipedia.org/wiki/KISS_principle)
- [ ] Refactor: You have [left the code cleaner than you found it (Boy Scout Rule)](https://learning.oreilly.com/library/view/97-things-every/9780596809515/ch08.html)
- [ ] Upgrade: Impact of this change on upgrade flows was considered and addressed if required
- [ ] Documentation: A [user-guide update](https://docs.cherry-ai.com) was considered and is present (link) or not required. Check this only when the PR introduces or changes a user-facing feature or behavior.
- [ ] Self-review: I have reviewed my own code (e.g., via [`/gh-pr-review`](/.claude/skills/gh-pr-review/SKILL.md), `gh pr diff`, or GitHub UI) before requesting review from others

### Release note

```release-note
Local model cards now explain when model files are present but the shared runtime is missing.
```

<!-- START COPILOT CODING AGENT SUFFIX -->

- Fixes #23795