#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="power-automate-authoring"
SKILL_DIR="${ROOT_DIR}/${SKILL_NAME}"
DIST_DIR="${ROOT_DIR}/dist"
VERSION=""

usage() {
  cat <<'EOF'
Package the power-automate-authoring Agent Skill as a release zip.

Usage:
  scripts/package-skill.sh [--version VERSION] [--output-dir DIR] [--help]

Environment:
  PACKAGE_VERSION  Version used in the zip filename when --version is omitted.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      if [[ -z "${2:-}" ]]; then
        echo "ERROR: --version requires a value" >&2
        exit 2
      fi
      VERSION="$2"
      shift 2
      ;;
    --output-dir)
      if [[ -z "${2:-}" ]]; then
        echo "ERROR: --output-dir requires a value" >&2
        exit 2
      fi
      DIST_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${VERSION}" ]]; then
  VERSION="${PACKAGE_VERSION:-}"
fi

if [[ -z "${VERSION}" ]] && git -C "${ROOT_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  VERSION="$(git -C "${ROOT_DIR}" describe --tags --exact-match 2>/dev/null || true)"
fi

if [[ -z "${VERSION}" ]] && git -C "${ROOT_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  VERSION="dev-$(git -C "${ROOT_DIR}" rev-parse --short HEAD)"
fi

if [[ -z "${VERSION}" ]]; then
  VERSION="dev"
fi

if [[ ! "${VERSION}" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "ERROR: version may contain only letters, numbers, dots, underscores, and hyphens" >&2
  exit 2
fi

if [[ ! -d "${SKILL_DIR}" ]]; then
  echo "ERROR: skill directory not found: ${SKILL_DIR}" >&2
  exit 1
fi

if ! command -v zip >/dev/null 2>&1; then
  echo "ERROR: zip command not found" >&2
  exit 1
fi
if ! command -v unzip >/dev/null 2>&1; then
  echo "ERROR: unzip command not found" >&2
  exit 1
fi

bash "${ROOT_DIR}/scripts/validate-skill.sh"

mkdir -p "${DIST_DIR}"
DIST_DIR="$(cd "${DIST_DIR}" && pwd)"
STAGING_DIR="$(mktemp -d "${TMPDIR:-/tmp}/power-automate-authoring-package.XXXXXX")"
cleanup() {
  rm -rf "${STAGING_DIR}"
}
trap cleanup EXIT

cp -R "${SKILL_DIR}" "${STAGING_DIR}/${SKILL_NAME}"
if [[ -f "${ROOT_DIR}/LICENSE" ]]; then
  cp "${ROOT_DIR}/LICENSE" "${STAGING_DIR}/${SKILL_NAME}/LICENSE"
fi
find "${STAGING_DIR}" -name '.DS_Store' -o -name 'Thumbs.db' -o -name '__MACOSX' | while IFS= read -r metadata_file; do
  rm -rf "${metadata_file}"
done

ZIP_PATH="${DIST_DIR}/${SKILL_NAME}-${VERSION}.zip"
rm -f "${ZIP_PATH}" "${ZIP_PATH}.sha256"

(
  cd "${STAGING_DIR}"
  zip -qr "${ZIP_PATH}" "${SKILL_NAME}"
)

if [[ ! -s "${ZIP_PATH}" ]]; then
  echo "ERROR: package was not created: ${ZIP_PATH}" >&2
  exit 1
fi

zip_listing="$(unzip -l "${ZIP_PATH}")"

grep -Fq "${SKILL_NAME}/SKILL.md" <<<"${zip_listing}" || {
  echo "ERROR: package missing SKILL.md" >&2
  exit 1
}

if grep -E '(__MACOSX|\.DS_Store|Thumbs\.db|\.git/)' <<<"${zip_listing}"; then
  echo "ERROR: package contains local metadata" >&2
  exit 1
fi

if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "${ZIP_PATH}" >"${ZIP_PATH}.sha256"
elif command -v sha256sum >/dev/null 2>&1; then
  sha256sum "${ZIP_PATH}" >"${ZIP_PATH}.sha256"
else
  echo "ERROR: shasum or sha256sum command not found" >&2
  exit 1
fi

printf 'Created package: %s\n' "${ZIP_PATH}"
printf 'Created checksum: %s\n' "${ZIP_PATH}.sha256"
