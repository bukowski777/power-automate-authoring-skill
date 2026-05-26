# Power Automate Connector Contracts

Use this checklist when a workflow change touches connector behavior, inputs, outputs, retry behavior, or downstream side effects. Preserve project-specific contracts first; these are generic prompts for review.

| Connector | Risks to verify |
|---|---|
| SharePoint | Site URL, list/library reference, pagination, `$top`, folder/file paths, list titles with spaces, internal column names, item ID assumptions, attachment limits. |
| Dataverse | Logical names, plural entity set names, lookup bindings, alternate keys, option-set values, ownership, solution dependencies, row-level permissions. |
| SQL | Gateway dependency, timeout, retry policy, transaction boundaries, idempotency keys, null handling, decimal/date formats, stored procedure contract. |
| HTTP | Secret/API key placement, retry policy, expected status codes, non-2xx error body shape, pagination, throttling headers, idempotency, endpoint configurability. |
| Outlook | Recipients, shared mailbox permissions, PII exposure, attachment size, retry behavior, duplicate-send prevention, HTML escaping. |
| Teams | Channel/chat target, mention formatting, payload size, PII exposure, duplicate notifications, connector identity, retry behavior. |
| AI Builder/OCR | Null values, confidence threshold, currency and decimal separators, non-ISO dates, multi-page documents, language assumptions, manual-review fallback. |

## Review Rules

- Do not hardcode tenant URLs, list IDs, connection IDs, email addresses, API endpoints, or secrets in reusable examples.
- Prefer connection references and environment variables for values that vary by tenant, workspace, or deployment target.
- Verify whether a connector action can return an empty array, null object, throttling response, timeout, or partial success.
- Preserve existing pagination, retry, concurrency, and timeout settings unless the requested change requires altering them.
- Confirm downstream actions are idempotent before adding retries around create, send, approve, delete, or update operations.
- When changing a connector output path, search for all dependent expressions such as `outputs('...')`, `body('...')`, `items('...')`, and `result('...')`.
