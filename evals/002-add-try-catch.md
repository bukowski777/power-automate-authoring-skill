# Eval: Add TRY/CATCH Logging

## User request

Add operational TRY/CATCH logging to this Power Automate flow.

## Expected behavior

- Identify the target environment, solution, flow, and logging destination.
- Inspect existing action names and naming conventions before adding scopes.
- Add `TRY_<domain>` and `CATCH_<domain>` without renaming unrelated actions.
- Build a structured log payload with failed action name, status, code, message, timestamps, and tracking ID when available.
- Exclude raw TRY results from email by default.
- Add `Terminate_Failed` unless the user explicitly wants the run to succeed after CATCH.

## Must not

- Hardcode tenant URLs, personal emails, connection IDs, or production configuration.
- Build CATCH context from outputs of actions that may have failed.
- Claim runtime tests were run if they were not.

## Pass/fail criteria

Pass if the patch is narrow, the catch path is verifiable, and the final response names skipped tenant/runtime checks.
