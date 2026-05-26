#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="power-automate-authoring"
SKILL_DIR="${ROOT_DIR}/${SKILL_NAME}"
SKILL_FILE="${SKILL_DIR}/SKILL.md"
AGENT_FILE="${SKILL_DIR}/agents/openai.yaml"
failures=0
# shellcheck disable=SC2016
router_ref_pattern='`references/[^`]+\.md`'

fail() {
  echo "ERROR: $*" >&2
  failures=$((failures + 1))
}

require_file() {
  local file="$1"
  [[ -f "${ROOT_DIR}/${file}" ]] || fail "missing required file: ${file}"
}

required_files=(
  ".editorconfig"
  ".gitattributes"
  ".gitignore"
  "AGENTS.md"
  "LICENSE"
  "README.md"
  "MAINTENANCE.md"
  "SECURITY.md"
  "CONTRIBUTING.md"
  "CHANGELOG.md"
  "install.sh"
  "scripts/package-skill.sh"
  "scripts/test-install.sh"
  "scripts/validate-workflow-json.py"
  ".github/CODEOWNERS"
  ".github/workflows/release.yml"
  ".github/workflows/validate.yml"
  "docs/how-to-vscode-codex-claude-code.md"
  "evals/001-fix-expression.md"
  "evals/002-add-try-catch.md"
  "evals/003-review-runafter.md"
  "evals/004-refuse-prod-import-without-approval.md"
  "evals/005-detect-hardcoded-secret.md"
  "power-automate-authoring/SKILL.md"
  "power-automate-authoring/agents/openai.yaml"
  "power-automate-authoring/references/connector-contracts.md"
  "power-automate-authoring/references/naming-conventions.md"
  "power-automate-authoring/references/solution-workflow.md"
  "power-automate-authoring/references/try-catch-logging.md"
  "tests/test_validate_workflow_json.py"
)

for file in "${required_files[@]}"; do
  require_file "${file}"
done

if [[ -f "${SKILL_FILE}" ]]; then
  frontmatter_lines="$(grep -n '^---$' "${SKILL_FILE}" | cut -d: -f1 || true)"
  first_frontmatter_line="$(printf '%s\n' "${frontmatter_lines}" | sed -n '1p')"
  second_frontmatter_line="$(printf '%s\n' "${frontmatter_lines}" | sed -n '2p')"
  if [[ -z "${second_frontmatter_line}" || "${first_frontmatter_line}" != "1" ]]; then
    fail "SKILL.md must start with YAML frontmatter delimited by ---"
  fi

  grep -Eq '^name: [a-z0-9-]{1,64}$' "${SKILL_FILE}" || fail "invalid skill name format"
  grep -Eq '^name: power-automate-authoring$' "${SKILL_FILE}" || fail "SKILL.md frontmatter must define name: power-automate-authoring"
  grep -Eq '^description: Use when .{40,}$' "${SKILL_FILE}" || fail "SKILL.md frontmatter description must start with 'Use when' and be specific"
  description_line="$(grep -E '^description: ' "${SKILL_FILE}" | sed 's/^description: //')"
  description_length="${#description_line}"
  if [[ "${description_length}" -gt 700 ]]; then
    fail "SKILL.md description is too long: ${description_length} chars; keep it under 700"
  fi

  while IFS= read -r ref; do
    [[ -f "${SKILL_DIR}/${ref}" ]] || fail "router reference missing: ${ref}"
  done < <(grep -Eo "${router_ref_pattern}" "${SKILL_FILE}" | tr -d '`' | sort -u)
fi

if [[ -f "${AGENT_FILE}" ]]; then
  grep -Eq '^interface:' "${AGENT_FILE}" || fail "openai.yaml must contain interface section"
  grep -Eq '^policy:' "${AGENT_FILE}" || fail "openai.yaml must contain policy section"
fi

bash -n "${ROOT_DIR}/install.sh" || fail "install.sh has shell syntax errors"
bash -n "${ROOT_DIR}/scripts/validate-skill.sh" || fail "scripts/validate-skill.sh has shell syntax errors"
bash -n "${ROOT_DIR}/scripts/package-skill.sh" || fail "scripts/package-skill.sh has shell syntax errors"
bash -n "${ROOT_DIR}/scripts/test-install.sh" || fail "scripts/test-install.sh has shell syntax errors"

if [[ "${CI:-}" == "true" ]] && ! command -v shellcheck >/dev/null 2>&1; then
  fail "shellcheck is required in CI"
elif command -v shellcheck >/dev/null 2>&1; then
  shellcheck "${ROOT_DIR}/install.sh" "${ROOT_DIR}"/scripts/*.sh || fail "shellcheck failed"
else
  echo "WARN: shellcheck not installed; skipping shell lint" >&2
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHONDONTWRITEBYTECODE=1 python3 -c 'import ast, pathlib, sys; ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"), filename=sys.argv[1])' "${ROOT_DIR}/scripts/validate-workflow-json.py" || fail "validate-workflow-json.py has Python syntax errors"
  PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "${ROOT_DIR}/tests" || fail "workflow JSON validator tests failed"
else
  fail "python3 is required for workflow JSON validator checks"
fi

api_token_pattern='(AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|ghp_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|[B]earer [A-Za-z0-9._~+/=-]{20,}|[e]yJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)'
database_url_pattern='([p]ostgres|[m]ysql)://[^[:space:]]+'
connection_string_pattern='[S]erver=.*[P]assword='
secret_pattern="(${api_token_pattern}|${database_url_pattern}|${connection_string_pattern})"
secret_scan_file="$(mktemp "${TMPDIR:-/tmp}/power-automate-authoring-secret-scan.XXXXXX")"
if git -C "${ROOT_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  while IFS= read -r -d '' file; do
    grep -IInE "${secret_pattern}" "${ROOT_DIR}/${file}" || true
  done < <(git -C "${ROOT_DIR}" ls-files -z) >"${secret_scan_file}"
else
  grep -RInIE "${secret_pattern}" \
    --exclude-dir=.git \
    --exclude-dir=dist \
    --exclude-dir=tmp \
    "${ROOT_DIR}" >"${secret_scan_file}" || true
fi

if [[ -s "${secret_scan_file}" ]]; then
  cat "${secret_scan_file}" >&2
  fail "possible secret-like value detected"
fi
rm -f "${secret_scan_file}"

metadata_files="$(find "${ROOT_DIR}" \( -path "${ROOT_DIR}/.git" -o -path "${ROOT_DIR}/dist" -o -path "${ROOT_DIR}/tmp" \) -prune -o \( -name '.DS_Store' -o -name 'Thumbs.db' -o -name '__MACOSX' \) -print || true)"
if [[ -n "${metadata_files}" ]]; then
  printf '%s\n' "${metadata_files}" >&2
  fail "metadata files must not be included"
fi

file_count=$(find "${SKILL_DIR}" -type f | wc -l | tr -d ' ')
if [[ "${file_count}" -gt 20 ]]; then
  fail "skill package has ${file_count} files; expected 20 or fewer"
fi

if [[ "${failures}" -gt 0 ]]; then
  echo "Validation failed with ${failures} error(s)." >&2
  exit 1
fi

echo "Skill validation passed."
