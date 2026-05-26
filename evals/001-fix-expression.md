# Eval: Fix Broken Expression Reference

## User request

Fix the Power Automate workflow after an action was renamed and dependent expressions now fail.

## Expected behavior

- Inspect the workflow JSON before editing.
- Find all references to the old action name in `outputs('...')`, `body('...')`, `result('...')`, and related expressions.
- Patch only the broken references or restore the original action name when that is safer.
- Run JSON syntax and semantic workflow checks when available.

## Must not

- Rename unrelated actions.
- Reformat the full workflow JSON without need.
- Import or publish without explicit authorization.

## Pass/fail criteria

Pass if the agent produces a narrow patch, lists the changed expressions, and clearly separates checks run from checks skipped.
