# Power Automate Authoring Skill

Agent Skill for safe Microsoft Power Automate cloud-flow authoring with Codex and Claude Code.

It helps agents modify Dataverse solution workflow JSON through an export/unpack/edit/pack/import loop, with guardrails for naming conventions, `runAfter`, connection references, TRY/CATCH logging, Power Automate expressions, SharePoint/Dataverse/SQL/HTTP connectors, runtime verification, and tenant-impacting commands.

## What It Is For

Use this skill when an agent needs to:

- create, modify, debug, harden, package, import, export, or review Power Automate cloud flows;
- work with Dataverse solution exports and `Workflows/*.json`;
- preserve connector contracts, connection references, trigger shapes, and action names;
- define or preserve flow, action, scope, variable, solution, connection reference, and environment variable naming conventions;
- add production-oriented TRY/CATCH logging and structured failure payloads;
- verify expressions, run-after paths, idempotency, retry behavior, and runtime tests;
- work from Codex, Claude Code, VS Code, or a local shell using `pac`, `m365`, `jq`, and `rg`.

This is not a tenant-admin policy guide or a licensing guide. It focuses on safe authoring and delivery of cloud-flow definitions.

## Repository Layout

```text
power-automate-authoring/
  SKILL.md
  agents/openai.yaml
  references/
docs/
  how-to-vscode-codex-claude-code.md
scripts/
  validate-skill.sh
  test-install.sh
  package-skill.sh
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
