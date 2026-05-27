# Power Automate Authoring Skill [![Validate skill](https://github.com/bukowski777/power-automate-authoring-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/bukowski777/power-automate-authoring-skill/actions/workflows/validate.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Agent Skill for safe Microsoft Power Automate cloud-flow DEV authoring with Codex and Claude Code.

It helps agents modify Dataverse solution workflow JSON through an export/unpack/edit/pack/import loop, with guardrails for naming conventions, `runAfter`, connection references, deployment settings, pre-import drift checks, TRY/CATCH logging, Power Automate expressions, SharePoint/Dataverse/SQL/HTTP connectors, runtime verification, and tenant-impacting commands.

## What It Is For

Use this skill when an agent needs to:

- create, modify, debug, harden, package, import, export, or review Power Automate cloud flows;
- work with Dataverse solution exports and `Workflows/*.json`;
- preserve connector contracts, connection references, trigger shapes, and action names;
- define or preserve flow, action, scope, variable, solution, connection reference, and environment variable naming conventions;
- add production-oriented TRY/CATCH logging and structured failure payloads;
- check for portal-side drift before import and avoid silently overwriting another maker's changes;
- verify expressions, run-after paths, idempotency, retry behavior, and runtime tests;
- work from Codex, Claude Code, VS Code, or a local shell using `pac`, `m365`, `jq`, and `rg`.

This is not a tenant-admin policy guide, licensing guide, or TEST/PROD managed-release guide. It focuses on safe DEV authoring, local validation, controlled DEV imports, and handoff to the project's ALM or release process.

## Repository Layout

```text
power-automate-authoring/
  SKILL.md
  agents/openai.yaml
  references/
docs/
  how-to-vscode-codex-claude-code.md
evals/
  001-fix-expression.md
  rubric.md
  ...
scripts/
  validate-skill.sh
  validate-workflow-json.py
  test-install.sh
  package-skill.sh
tests/
  test_validate_workflow_json.py
```

## Install

Install for Codex:

```bash
./install.sh
```

Install for Codex and Claude Code:

```bash
./install.sh --target all
```

Targets:

```text
~/.agents/skills/power-automate-authoring      # Codex user skills
~/.claude/skills/power-automate-authoring      # Claude Code personal skills
~/.codex/skills/power-automate-authoring       # legacy/local fallback only
```

For current Codex versions, prefer `~/.agents/skills`.

## Validate

```bash
bash scripts/validate-skill.sh
bash scripts/test-install.sh
python3 -m unittest discover -s tests
python3 scripts/validate-workflow-json.py path/to/Workflows/<workflow-file>.json
python3 scripts/validate-workflow-json.py --strict path/to/Workflows/<workflow-file>.json
```

## Package

Build a local release archive:

```bash
scripts/package-skill.sh --version v0.1.0
```

The archive is written to `dist/` and contains the installable `power-automate-authoring/` skill directory. A matching `.sha256` checksum is created next to the zip.

## Publish

Push a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The release workflow validates the skill, creates the zip, and attaches it to the hosted release.

## Related Guide

The full operational guide is in [docs/how-to-vscode-codex-claude-code.md](docs/how-to-vscode-codex-claude-code.md).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
