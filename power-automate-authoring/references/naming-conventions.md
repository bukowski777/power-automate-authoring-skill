# Power Automate Naming Conventions

Use this reference when creating, renaming, reviewing, or documenting Power Automate cloud flows and solution components.

## Source Principles

Microsoft guidance recommends descriptive names, consistent separators such as camelCase or underscores, prefixes or tags by component type, conventions applied consistently across flows, and documenting the convention for the team.

For solution-aware flows, keep solution components portable across environments by using connection references and environment variables rather than embedding environment-specific values in workflow definitions.

For Dataverse solution projects, `pac solution init --publisher-prefix` requires a publisher prefix that is 2 to 8 alphanumeric characters, starts with a letter, and does not start with `mscrm`.

## First Rule

Preserve the project's existing convention first. Do not rename actions, scopes, variables, or connection references just to make them prettier. Renames can break:

- expressions that call action outputs by name;
- `runAfter` dependencies;
- TRY/CATCH `result('<scope>')` references;
- screenshots, runbooks, support notes, and client documentation.

Rename only when the requested change requires it, the dependency graph is inspected, and the rename is verified in the exported JSON.

## Recommended Shape

Use stable, descriptive names that are readable in both the Power Automate designer and exported `Workflows/*.json`.

| Component | Pattern | Example |
| --- | --- | --- |
| Flow display name | `<Domain> - <Event> - <Outcome>` | `Invoices - File uploaded - Create approval` |
| Trigger | `Trg_<event>` or descriptive text | `Trg_FileUploaded` |
| Init scope | `INIT_<domain>` | `INIT_invoice` |
| Main scope | `TRY_<domain>` | `TRY_invoice_import` |
| Catch scope | `CATCH_<domain>` | `CATCH_invoice_import` |
| Finally scope | `FINALLY_<domain>` | `FINALLY_invoice_import` |
| Variable | `var<BusinessMeaning>` | `varInvoiceId` |
| Compose | `Compose_<meaning>` | `Compose_LogPayload` |
| Parse JSON | `Parse_<payload>` | `Parse_SourcePayload` |
| Filter array | `Filter_<collection>` | `Filter_FailedActions` |
| Select | `Select_<shape>` | `Select_ErrorDetails` |
| Connector action | `<Verb>_<system>_<entity>` | `Create_Dataverse_Invoice` |
| Connection reference | `<prefix>_<connector>_<purpose>` | `cnts_SharePoint_Documents` |
| Environment variable | `<prefix>_<setting>` | `cnts_TargetSiteUrl` |
| Solution unique name | `<Publisher><Domain><Capability>` | `ContosoInvoiceAutomation` |

Use one separator style per flow. If the project uses underscores in action names, continue with underscores. If the project uses readable designer labels with spaces, preserve that style unless local JSON automation requires stable identifier-like names.

## Prefixes

Recommended action prefixes:

- `Trg_` for triggers.
- `INIT_`, `TRY_`, `CATCH_`, `FINALLY_` for scopes.
- `var` for variables.
- `Compose_`, `Parse_`, `Filter_`, `Select_` for data shaping.
- `Get_`, `List_`, `Create_`, `Update_`, `Delete_`, `Send_`, `Post_`, `Call_` for connector actions.

Avoid names such as `Action1`, `Compose 2`, `Variable`, `Scope`, `Test`, `New step`, or personal/client names that do not describe behavior.

## Solution-Aware Components

For solution-aware cloud flows:

- use a real publisher prefix for custom solution components;
- use connection references for connectors that move across environments;
- use environment variables for URLs, list names, table names, API endpoints, feature switches, and non-secret environment values;
- keep secrets in secure stores or connector configuration, not in flow names, environment variable names, docs, or exported examples;
- name parent/child flows with the same domain and capability vocabulary when they belong together.

## Review Checklist

- Existing naming convention identified before edits.
- New names are descriptive, stable, and tenant-neutral.
- Publisher prefix is valid for `pac solution init`.
- Connection reference and environment variable names include prefix plus purpose.
- Names do not include secrets, tenant IDs, private URLs, client personal data, or temporary debug language.
- Action/scope renames were checked against expressions, `runAfter`, `result('<scope>')`, docs, and tests.

## Sources

- Microsoft Learn: [Use consistent naming for flow components](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/use-consistent-naming-conventions)
- Microsoft Learn: [Understand the benefits of using solution-aware cloud flows](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/understand-benefits-solution-aware-flows)
- Microsoft Learn: [pac solution](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution)
- Microsoft Learn: [Use scopes to organize actions in cloud flows](https://learn.microsoft.com/en-us/power-automate/scopes)
- Microsoft Learn: [Employ robust error handling](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/error-handling)
