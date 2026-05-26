# AGENTS

This repository contains the `power-automate-authoring` Agent Skill.

## Working Rules

- Keep the installable skill folder at `power-automate-authoring/`.
- Keep changes narrow and directly related to Power Automate authoring, packaging, installation, validation, or documentation.
- Do not add tenant-specific values, private environment URLs, credentials, exported run payloads, client data, screenshots, or solution ZIPs.
- Use placeholders such as `<environment-url>`, `<solution-name>`, `<flow-name>`, and `<sharepoint-site-url>`.
- Update `README.md` and `CHANGELOG.md` when installation, packaging, validation, or skill behavior changes.

## Validation

Run before commit or release:

```bash
bash scripts/validate-skill.sh
bash scripts/test-install.sh
scripts/package-skill.sh --version test-package
git diff --check
```

## Release

Use version tags such as `v0.1.0`. The release workflow validates the skill, builds a zip, and uploads the zip plus its SHA-256 checksum.
