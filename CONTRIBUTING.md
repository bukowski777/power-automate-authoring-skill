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
python3 -m unittest discover -s tests
python3 scripts/validate-workflow-json.py path/to/Workflows/<workflow-file>.json
python3 scripts/validate-workflow-json.py --strict path/to/Workflows/<workflow-file>.json
scripts/package-skill.sh --version test-package
git diff --check
```
