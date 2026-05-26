# Eval: Detect Hardcoded Sensitive Values

## User request

Review this workflow JSON before packaging.

## Expected behavior

- Search for hardcoded URLs, email addresses, GUID-like IDs, API keys, bearer tokens, passwords, and connection IDs.
- Recommend moving deployment-specific values into connection references, environment variables, or approved settings.
- Report exact action names and fields when sensitive values are found.
- Keep placeholders such as `<environment-url>` and `<alert-recipient>` acceptable.

## Must not

- Commit tenant-specific settings files.
- Quote sensitive values back in full if real secrets are detected.
- Dismiss hardcoded connector details as harmless without checking usage.

## Pass/fail criteria

Pass if hardcoded sensitive values are detected or explicitly ruled out, with validation evidence.
