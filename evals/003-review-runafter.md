# Eval: Review runAfter Safety

## User request

Review this workflow change for `runAfter` mistakes before import.

## Expected behavior

- Inspect every edited action's `runAfter`.
- Verify dependencies point to actions or scopes at the same level.
- Reject invalid statuses such as `Cancelled`.
- Explain success, failure, timeout, and skipped paths affected by the change.
- Use the semantic validator if available.

## Must not

- Treat `jq empty` as sufficient semantic validation.
- Ignore nested scopes, switch cases, or conditional branches.
- Import the solution during review.

## Pass/fail criteria

Pass if missing dependencies, invalid statuses, and risky path changes are identified with exact action names.
