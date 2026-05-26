# Power Automate Solution Workflow

Use these commands as templates. Replace placeholders with project values or exported shell variables.

## Variables

```bash
export PA_SOLUTION_NAME="<solution-name>"
export PA_WORK_DIR="tmp/power-automate/<change-name>"
export PA_SITE_URL="<sharepoint-site-url>"
export PA_LIST_TITLE="<sharepoint-list-title>"
```

## Tool Checks

```bash
pac help
pac auth list
pac solution list
m365 version
m365 status --output json
jq --version
rg --version
git status --short
```

Install Microsoft 365 CLI if needed:

```bash
npm install -g @pnp/cli-microsoft365
```

## Export And Unpack

```bash
mkdir -p "$PA_WORK_DIR"

pac solution export \
  --name "$PA_SOLUTION_NAME" \
  --path "$PA_WORK_DIR/before.zip" \
  --managed false \
  --overwrite

rm -rf "$PA_WORK_DIR/unpacked"
pac solution unpack \
  --zipfile "$PA_WORK_DIR/before.zip" \
  --folder "$PA_WORK_DIR/unpacked" \
  --packagetype Unmanaged \
  --allowWrite \
  --clobber
```

Inspect workflows:

```bash
find "$PA_WORK_DIR/unpacked/Workflows" -maxdepth 1 -name '*.json' -print

for f in "$PA_WORK_DIR"/unpacked/Workflows/*.json; do
  echo "== ${f##*/}"
  jq -r '.properties.definition.actions | to_entries[] | "  \(.key): \(.value.type)"' "$f" | sed -n '1,20p'
done
```

## Validate Edited JSON

```bash
jq empty "$PA_WORK_DIR/unpacked/Workflows/<workflow-file>.json"
rg -n "TRY_|CATCH_|runAfter|formatNumber|float|<field-or-action-name>" "$PA_WORK_DIR/unpacked/Workflows"
git diff --check
```

## Pack And Import

```bash
pac solution pack \
  --zipfile "$PA_WORK_DIR/after.zip" \
  --folder "$PA_WORK_DIR/unpacked" \
  --packagetype Unmanaged \
  --allowWrite \
  --clobber

pac solution import \
  --path "$PA_WORK_DIR/after.zip" \
  --publish-changes \
  --force-overwrite
```

## Re-export Verification

```bash
pac solution export \
  --name "$PA_SOLUTION_NAME" \
  --path "$PA_WORK_DIR/verify.zip" \
  --managed false \
  --overwrite

rm -rf "$PA_WORK_DIR/verify"
pac solution unpack \
  --zipfile "$PA_WORK_DIR/verify.zip" \
  --folder "$PA_WORK_DIR/verify" \
  --packagetype Unmanaged \
  --allowWrite \
  --clobber

rg -n "TRY_|CATCH_|<action-name>|<expression-fragment>" "$PA_WORK_DIR/verify/Workflows"
```

## SharePoint Control

```bash
m365 request \
  --method get \
  --url "$PA_SITE_URL/_api/web/lists/getbytitle('$PA_LIST_TITLE')/items?\$top=5" \
  --output json | jq
```

Encode list titles with spaces when needed.
