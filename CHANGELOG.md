# Changelog

All notable changes to this skill repository should be documented here.

## Unreleased

- Clarified the skill's DEV authoring scope and TEST/PROD ALM handoff boundary.
- Aligned OpenAI agent confirmation policy with all tenant-impacting commands listed in the skill.
- Added warning-level workflow JSON diagnostics, `--strict`, and CATCH logging variable placement checks.
- Updated maintenance, contribution, security, workflow, and eval documentation.

## v0.2.0 - 2026-05-26

- Added Power Automate naming convention guidance for flows, actions, scopes, variables, solution publisher prefixes, connection references, and environment variables, sourced from Microsoft Learn.
- Added pre-import drift checks, deployment settings guidance, connector contract review guidance, and behavioral eval scenarios.
- Hardened TRY/CATCH logging guidance to avoid raw TRY results in email by default and terminate failed business processing as `Failed`.
- Added a semantic workflow JSON validator with unit tests for `runAfter`, expression references, variable references, and hardcoded sensitive values.
- Fixed relative `--output-dir` packaging by normalizing the output path before staging.
- Hardened CI/release validation with ShellCheck enforcement in CI and job timeouts.

## v0.1.0 - 2026-05-26

- Extracted `power-automate-authoring` from the GED repository into a standalone skill repository.
- Reworked the skill structure around mission, triggers, operating defaults, workflow, risk gates, verification, and completion checklist.
- Added Codex and Claude Code installation support, validation, install smoke tests, packaging, and release workflows.
