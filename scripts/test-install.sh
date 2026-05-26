#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="power-automate-authoring"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/power-automate-authoring-install-test.XXXXXX")"

cleanup() {
  rm -rf "${TMP_ROOT}"
}
trap cleanup EXIT

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

assert_file() {
  [[ -f "$1" ]] || fail "missing file: $1"
}

assert_no_path() {
  [[ ! -e "$1" ]] || fail "unexpected path exists: $1"
}

legacy_dir="${TMP_ROOT}/codex-legacy/skills/${SKILL_NAME}"
mkdir -p "${legacy_dir}"
printf 'legacy\n' >"${legacy_dir}/legacy-marker.txt"

CODEX_HOME="${TMP_ROOT}/codex-legacy" \
CLAUDE_HOME="${TMP_ROOT}/claude" \
AGENTS_HOME="${TMP_ROOT}/agents" \
"${ROOT_DIR}/install.sh" --target all

assert_file "${TMP_ROOT}/agents/skills/${SKILL_NAME}/SKILL.md"
assert_file "${TMP_ROOT}/agents/skills/${SKILL_NAME}/agents/openai.yaml"
assert_file "${TMP_ROOT}/claude/skills/${SKILL_NAME}/SKILL.md"
assert_no_path "${TMP_ROOT}/claude/skills/${SKILL_NAME}/agents/openai.yaml"
assert_no_path "${legacy_dir}"

legacy_backup_count="$(find "${TMP_ROOT}/codex-legacy/skills/.backups" -maxdepth 1 -type d -name "${SKILL_NAME}.*" 2>/dev/null | wc -l | tr -d ' ')"
[[ "${legacy_backup_count}" -eq 1 ]] || fail "expected one legacy Codex backup, found ${legacy_backup_count}"

CODEX_HOME="${TMP_ROOT}/codex-legacy" \
CLAUDE_HOME="${TMP_ROOT}/claude" \
AGENTS_HOME="${TMP_ROOT}/agents" \
"${ROOT_DIR}/install.sh" --target codex-legacy

assert_file "${TMP_ROOT}/codex-legacy/skills/${SKILL_NAME}/SKILL.md"
assert_file "${TMP_ROOT}/codex-legacy/skills/${SKILL_NAME}/agents/openai.yaml"

echo "Install smoke test passed."
