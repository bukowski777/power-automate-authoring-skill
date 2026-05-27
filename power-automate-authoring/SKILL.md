---
name: power-automate-authoring
description: Use when creating, modifying, debugging, hardening, importing/exporting, packaging, or reviewing Microsoft Power Automate cloud flows, Dataverse solution workflow JSON, Power Platform CLI pac workflows, Microsoft 365 CLI checks, TRY/CATCH logging, runAfter paths, connection references, or Power Automate expressions from Codex, Claude Code, VS Code, or a local shell.
---

# Power Automate Authoring

## Mission

Modify Power Automate cloud flows through exported Dataverse solution definitions in a way that is reviewable, reversible, tenant-safe, and verifiable.

Use the language of the user's prompt or current conversation. Do not force French or English.

## When to Use

Use this skill when a Power Automate change depends on solution packaging, workflow JSON, connector contracts, environment safety, or runtime verification.

Typical triggers:

- create, modify, debug, harden, import, export, package, or review cloud flows;
- work with Dataverse solution exports, `Workflows/*.json`, connection references, environment variables, or solution components;
- edit `runAfter`, scopes, trigger/action definitions, connector inputs, or Power Automate expressions;
- define or review flow, action, scope, variable, solution, publisher prefix, connection reference, and environment variable naming conventions;
- add or review production TRY/CATCH logging, alerting, or structured failure payloads;
- use `pac`, `m365`, `jq`, `rg`, VS Code, Codex, or Claude Code for flow authoring;
- verify SharePoint, Dataverse, Outlook, SQL, HTTP, OCR, or AI Builder connector behavior after a flow change.

## When Not to Use

Do not load the whole skill for a short conceptual Power Automate answer that does not touch a flow definition, tenant, solution package, connector contract, or runtime verification. For desktop flows, tenant governance, licensing, or admin policy questions, use only the relevant parts unless cloud-flow JSON authoring is involved.

This skill is primarily for DEV authoring, local validation, and controlled DEV imports. Do not use it as the primary TEST/PROD release or managed-solution promotion guide. For TEST/PROD deployment, hand off to the project's ALM, pipeline, release, or governance process.

## Operating Defaults

Work from a fresh Dataverse solution export. Do not edit stale ZIPs or old unpacked folders unless the user explicitly asks for forensic review.

Default to DEV authoring and local validation. Treat import as a controlled DEV operation that requires explicit authorization, a pre-import drift check, and a rollback or recovery option.

For a new cloud flow, prefer a portal-created skeleton first: create the flow in the target Power Platform solution, add the trigger and connector actions needed to create connection references, save it, then export/unpack and continue locally. Creating a full flow JSON from scratch is fragile.

Use the full command workflow in [references/solution-workflow.md](references/solution-workflow.md) when executing export, unpack, pack, import, and verification steps.

Use [references/try-catch-logging.md](references/try-catch-logging.md) when adding or reviewing CATCH logs. It contains reusable Power Automate action JSON and expressions for `result('TRY_<domain>')`, failed-action filtering, log payload creation, and email body generation.

Use [references/naming-conventions.md](references/naming-conventions.md) when creating, renaming, reviewing, or documenting flow components. Preserve the project convention first; introduce a new convention only when none exists.

Use [references/connector-contracts.md](references/connector-contracts.md) when a change touches SharePoint, Dataverse, SQL, HTTP, Outlook, Teams, OCR, or AI Builder connector behavior.

Before changing anything, identify the tenant/environment, solution, flow, allowed scope, connection account, deployment path, rollback option, whether a deployment settings file is required, whether another maker may edit the flow during the change window, whether the flow must remain enabled after import, whether failed business processing must terminate the flow as `Failed`, and whether import/publish is explicitly authorized.

Never store secrets, tokens, tenant credentials, private URLs, personal data, exported run payloads, or connector-specific sensitive values in docs, commits, screenshots, logs, or reusable examples.

Ask before running tenant-impacting commands such as import, publish, enable, disable, remove, or connection changes unless the user explicitly requested that operation in the current task.

## Workflow

1. Identify the target environment, solution name, flow name, allowed scope, and connection account.
2. Inspect `git status --short` and keep temporary exports, ZIPs, logs, and unpacked solution folders out of version control.
3. Check local tools: `pac`, `m365`, `jq`, `rg`, Git, and Node/npm if `m365` is needed.
4. Export the current solution with `pac solution export`.
5. Unpack with `pac solution unpack` into a temporary ignored folder.
6. Locate the workflow JSON under `Workflows/`.
7. Inspect existing naming conventions, actions, `runAfter`, connection references, expressions, variables, trigger shape, and solution dependencies before editing.
8. Patch only the required workflow and actions.
9. Run `jq empty` on edited workflow JSON.
10. Run semantic workflow checks when available, such as `python3 scripts/validate-workflow-json.py "$PA_WORK_DIR/unpacked/Workflows/<workflow-file>.json"`.
11. Pack with `pac solution pack`.
12. Create and review a deployment settings file when connection references or environment variables must be supplied during import.
13. Re-export before import and compare against the initial baseline to detect portal-side drift.
14. Import with `pac solution import --publish-changes --force-overwrite` only after explaining tenant impact and rollback/recovery options.
15. Re-export and inspect the deployed definition.
16. Recommend or run real flow tests, including at least one error path for logging changes.

## Editing Rules

- Preserve `connectionName`, `operationId`, `apiId`, connection references, trigger shape, and existing action names unless intentionally changing them.
- Treat `runAfter` as high-risk. After every edit, verify success, failure, timeout, and skipped paths still make sense.
- Keep changes narrow; avoid formatting whole workflow JSON if it creates noisy diffs.
- Use `rg` and `jq` for inspection rather than manually reading huge JSON.
- Compare related flows that reuse the same expression or pattern.
- Preserve existing names unless renaming is part of the requested change. Renaming actions, scopes, or variables can break expressions, `runAfter`, and documentation references.
- For new components, use the project's naming convention or `references/naming-conventions.md`.
- Preserve idempotency and retry behavior when a flow creates, updates, deletes, or sends external records/messages.
- Do not hardcode environment-specific IDs, URLs, emails, list names, queue names, or log destinations in the generic skill; use project configuration or placeholders.

## Nomenclature / Naming

Prefer descriptive, stable, tenant-neutral names that make exported workflow JSON readable without opening the designer.

- Flow display names: `<Domain> - <Event> - <Outcome>` such as `Invoices - File uploaded - Create approval`.
- Scopes: `INIT_<domain>`, `TRY_<domain>`, `CATCH_<domain>`, `FINALLY_<domain>`, or project-equivalent names.
- Variables: `var<BusinessMeaning>` such as `varInvoiceId`, `varLogBusinessKey`, or `varSourceFileName`.
- Compose/parse/filter/select actions: `Compose_<meaning>`, `Parse_<payload>`, `Filter_<collection>`, `Select_<shape>`.
- Connector actions: `<Verb>_<system>_<entity>` such as `Get_SharePoint_FileMetadata` or `Create_Dataverse_Invoice`.
- Connection references and environment variables: keep publisher prefix and project vocabulary explicit, for example `<prefix>_SharePointDocuments` or `<prefix>_TargetSiteUrl`.

Choose camelCase or underscores according to the project convention and apply it consistently. Do not mix styles within the same flow unless preserving existing names.

## TRY/CATCH Pattern

For production flows, add or preserve:

- `TRY_<domain>` scope containing business actions.
- `CATCH_<domain>` scope configured to run after failure or timeout of the TRY scope; add skipped only when that is an intentional alert path.
- Error collection from `result('TRY_<domain>')`.
- Filter/select actions that extract failed action name, status, code, message, timings, and tracking ID from the TRY result.
- A structured log payload before any email or log-store action.
- A readable error summary with flow name, environment, run ID, business context, item/file/entity, action name, status, code, message, timestamps, and tracking ID when available.
- No raw TRY result in email by default; keep raw details truncated and only in an approved log destination.
- A `Terminate_Failed` action after the final log/alert action unless success-after-catch is an explicit business requirement.
- Logging destination defined by the project, not hardcoded from this generic skill.

## Expression Guardrails

- Normalize OCR or user text before numeric conversion.
- Prefer `formatNumber(mul(<amount>, 100), '0')` over `int(mul(...))` for cent amounts.
- Protect optional values with `coalesce()` and `empty()`.
- Avoid `formatDateTime()` on non-ISO strings such as raw `AM/PM` OCR text.
- Treat a valid JSON file as necessary but not sufficient; Power Automate expressions can still fail only at runtime.
- Validate array/object assumptions before using `first()`, `items()`, nested properties, or connector outputs that may be empty.
- Prefer explicit parsing and fallback behavior over expressions that silently return blank operational data.

## Risk Gates

Use a stronger review path when a change touches:

- production flows, business-critical automations, approvals, billing, notifications, or data sync;
- connector authentication, connection references, environment variables, service accounts, or permissions;
- SharePoint, Dataverse, SQL, HTTP, Outlook, Teams, OCR, AI Builder, or external system contracts;
- `runAfter`, retry policies, parallel branches, concurrency control, pagination, limits, or idempotency;
- create/update/delete actions, duplicate prevention, watermarks, or business keys;
- logging, alert recipients, personal data, run payloads, exports, or screenshots.

## Command Safety

Safe inspection commands:

- `pac auth list`
- `pac solution list`
- `pac solution export ...`
- `pac solution unpack ...`
- `jq empty ...`
- `python3 scripts/validate-workflow-json.py ...`
- `rg ...`
- `git diff --check`

Impacting commands:

- `pac solution import --publish-changes --force-overwrite`
- `pac solution import --stage-and-upgrade`
- `pac solution import --skip-dependency-check`
- `pac solution publish`
- `pac solution delete`
- `pac solution upgrade`
- `pac solution sync`
- `pac solution add-solution-component`
- `pac auth select` when followed by tenant-impacting commands
- `m365 flow enable`
- `m365 flow disable`
- `m365 flow remove`

Before running impacting commands, state the expected tenant/environment/solution impact and verify afterward with a re-export or status check.

Use `--force-overwrite` only for controlled DEV imports after explicit user authorization, a pre-import drift check, a rollback or recovery option, and target environment confirmation. Do not present it as a generic TEST/PROD deployment command.

## Verification Standard

When reporting completion, separate:

- changed files, flows, actions, expressions, and solution components;
- validation actually run, such as `jq empty`, `pac solution pack`, re-export inspection, and real flow tests;
- deployment settings file used or skipped;
- pre-import drift check result;
- whether the deployed flow remained enabled;
- whether CATCH terminates as `Failed` or intentionally allows success;
- tenant-impacting commands actually run, with environment and solution names;
- checks skipped and why;
- residual risk, rollback/recovery path, and owner action.

Never imply import, publish, deployment, re-export, or runtime flow tests were done when they were not.

## Reference Router

- Export, unpack, inspect, edit, pack, import, and re-export: read `references/solution-workflow.md`.
- Flow, action, scope, variable, solution, publisher prefix, connection reference, and environment variable naming: read `references/naming-conventions.md`.
- TRY/CATCH scopes, failed-action filtering, structured payloads, and email body expressions: read `references/try-catch-logging.md`.
- SharePoint, Dataverse, SQL, HTTP, Outlook, Teams, OCR, and AI Builder connector checks: read `references/connector-contracts.md`.

Use specialized skills when relevant and available, especially Power Automate expression validation, n8n/expression syntax, client delivery guardrails, TDD, diagnosis, GitHub CI, and documentation handover skills. Load only what is needed.

## Documentation

After a significant flow change, update project docs that describe flow behavior, test expectations, and operational runbooks. Commit only versioned source/docs; keep solution ZIPs, unpacked exports, logs, and temporary OCR/debug files ignored unless the project explicitly versions them.

## Completion Checklist

- Worktree inspected.
- Target tenant/environment/solution/flow identified.
- Scope, connection account, and import/publish authorization clear.
- Fresh export used unless forensic review was explicitly requested.
- Naming convention preserved or documented.
- Workflow JSON patched narrowly.
- `jq empty` run on edited workflow JSON.
- Semantic workflow checks run when available.
- Pre-import drift checked before overwriting a target flow.
- Pack/import/re-export/runtime checks run or explicitly skipped with reason.
- Error path tested when TRY/CATCH or logging changed.
- No secrets, tenant credentials, private payloads, or personal data added.
- Docs/runbooks updated when behavior, operations, or verification changed.
