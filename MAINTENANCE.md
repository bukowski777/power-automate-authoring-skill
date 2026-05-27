# Maintenance

## Local Checks

```bash
bash scripts/validate-skill.sh
bash scripts/test-install.sh
python3 -m unittest discover -s tests
python3 scripts/validate-workflow-json.py path/to/Workflows/<workflow-file>.json
python3 scripts/validate-workflow-json.py --strict path/to/Workflows/<workflow-file>.json
scripts/package-skill.sh --version test-package
git diff --check
```

`scripts/validate-skill.sh` checks required files, `SKILL.md` frontmatter, reference links, shell syntax, ShellCheck when available locally and mandatory in CI, Python validator tests, secret-like patterns, and local metadata.

`scripts/test-install.sh` installs into temporary Codex, Claude Code, and legacy Codex roots. It verifies that Claude Code installs do not include `agents/openai.yaml`.

`scripts/package-skill.sh` validates the repository, creates a release zip in `dist/`, inspects the archive, and writes a `.sha256` checksum.

## Release

1. Update `CHANGELOG.md`.
2. Run local checks.
3. Create and push a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The GitHub release workflow validates the skill and uploads both the zip and checksum.
