# Contributing

Contributions should keep the skill practical, safe, and tenant-neutral.

## Scope

Good changes include:

- clearer Power Automate workflow JSON authoring guidance;
- safer `pac` or `m365` command recipes;
- better TRY/CATCH logging patterns;
- expression guardrails and runtime verification checks;
- installer, validation, packaging, or documentation improvements.

Avoid:

- tenant-specific IDs, private URLs, credentials, or run payloads;
- solution ZIPs, unpacked exports, logs, or screenshots;
- broad rewrites that make the skill harder to scan.

## Checks

```bash
bash scripts/validate-skill.sh
bash scripts/test-install.sh
scripts/package-skill.sh --version test-package
git diff --check
```
