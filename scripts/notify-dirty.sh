#!/usr/bin/env bash
# ==============================================================================
# notify-dirty.sh: Notify via Mailrise when agy-config is dirty / uncommitted.
# Notifies once until repository is clean and synced with upstream.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Capture any environment variables set by caller
CLI_MAILRISE_URL="${MAILRISE_URL:-}"
CLI_MAILRISE_TO="${MAILRISE_TO:-}"
CLI_MAILRISE_FROM="${MAILRISE_FROM:-}"
CLI_MAILRISE_USER="${MAILRISE_USER:-}"
CLI_MAILRISE_PASSWORD="${MAILRISE_PASSWORD:-}"
CLI_CHECK_ALL_FILES="${CHECK_ALL_FILES:-}"
CLI_TARGET_REGEX="${TARGET_REGEX:-}"
CLI_NOTIFY_MODE="${NOTIFY_MODE:-}"
CLI_STATE_FILE="${STATE_FILE:-}"

# Load .env if present
ENV_FILE="${REPO_DIR}/.env"
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck source=/dev/null
  set -a
  source "${ENV_FILE}"
  set +a
fi

# Config defaults (caller env > .env > default)
MAILRISE_URL="${CLI_MAILRISE_URL:-${MAILRISE_URL:-smtp://smtp.l.nicholaswilde.io:8025}}"
MAILRISE_TO="${CLI_MAILRISE_TO:-${MAILRISE_TO:-all@mailrise.xyz}}"
MAILRISE_FROM="${CLI_MAILRISE_FROM:-${MAILRISE_FROM:-agy-config@$(hostname)}}"
MAILRISE_USER="${CLI_MAILRISE_USER:-${MAILRISE_USER:-}}"
MAILRISE_PASSWORD="${CLI_MAILRISE_PASSWORD:-${MAILRISE_PASSWORD:-}}"
CHECK_ALL_FILES="${CLI_CHECK_ALL_FILES:-${CHECK_ALL_FILES:-false}}"
TARGET_REGEX="${CLI_TARGET_REGEX:-${TARGET_REGEX:-skills/|rules/|settings\.json|config\.json|mcp_config\.json}}"
NOTIFY_MODE="${CLI_NOTIFY_MODE:-${NOTIFY_MODE:-dirty}}"
NOTIFY_MODE="$(echo "${NOTIFY_MODE}" | tr '[:upper:]' '[:lower:]')"
STATE_FILE="${CLI_STATE_FILE:-${STATE_FILE:-${XDG_STATE_HOME:-$HOME/.local/state}/agy-config/dirty.state}}"

FORCE=false
if [[ "${1:-}" == "--force" || "${1:-}" == "-f" ]]; then
  FORCE=true
fi

# Exit early if notifications disabled (unless forced test)
if [[ "${FORCE}" == "false" ]]; then
  case "${NOTIFY_MODE}" in
    disabled|disable|off|none|false)
      echo "Notifications are disabled (NOTIFY_MODE=${NOTIFY_MODE})."
      exit 0
      ;;
  esac
fi

# Verify git repository
if ! git -C "${REPO_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: ${REPO_DIR} is not a git repository" >&2
  exit 1
fi

# 1. Check uncommitted / untracked changes
DIRTY_ALL="$(git -C "${REPO_DIR}" status --porcelain=v1)"
DIRTY_MATCH=""
if [[ -n "${DIRTY_ALL}" ]]; then
  if [[ "${CHECK_ALL_FILES}" == "true" ]]; then
    DIRTY_MATCH="${DIRTY_ALL}"
  else
    DIRTY_MATCH="$(echo "${DIRTY_ALL}" | grep -E "${TARGET_REGEX}" || true)"
  fi
fi

# 2. Check unpushed commits (if upstream tracking branch exists)
UNPUSHED_COMMITS=""
UNPUSHED_COUNT=0
if git -C "${REPO_DIR}" rev-parse --abbrev-ref @{u} >/dev/null 2>&1; then
  UNPUSHED_COUNT="$(git -C "${REPO_DIR}" rev-list @{u}..HEAD --count 2>/dev/null || echo 0)"
  if [[ "${UNPUSHED_COUNT}" -gt 0 ]]; then
    UNPUSHED_COMMITS="$(git -C "${REPO_DIR}" log @{u}..HEAD --oneline)"
  fi
fi

IS_DIRTY=false
if [[ -n "${DIRTY_MATCH}" ]] || [[ "${UNPUSHED_COUNT}" -gt 0 ]]; then
  IS_DIRTY=true
fi

# Check last recorded state
LAST_STATE=""
if [[ -f "${STATE_FILE}" ]]; then
  LAST_STATE="$(cat "${STATE_FILE}" 2>/dev/null || echo "")"
fi

HOST="$(hostname)"
BRANCH="$(git -C "${REPO_DIR}" branch --show-current 2>/dev/null || echo 'unknown')"
NEW_STATE=""
SUBJECT=""

# Determine if notification should be sent based on NOTIFY_MODE and state
if [[ "${IS_DIRTY}" == "true" ]]; then
  if [[ "${FORCE}" == "false" && "${LAST_STATE}" == "DIRTY" ]]; then
    echo "Repository dirty, but notification already sent. Waiting for sync."
    exit 0
  fi
  NEW_STATE="DIRTY"
  SUBJECT="[agy-config] Uncommitted changes on ${HOST}"
else
  # Clean / synced state
  if [[ "${FORCE}" == "true" ]]; then
    NEW_STATE="CLEAN"
    SUBJECT="[agy-config] Test notification from ${HOST}"
  elif [[ "${NOTIFY_MODE}" == "both" && "${LAST_STATE}" == "DIRTY" ]]; then
    NEW_STATE="CLEAN"
    SUBJECT="[agy-config] Repository clean and synced on ${HOST}"
  else
    if [[ "${LAST_STATE}" == "DIRTY" || ("${NOTIFY_MODE}" != "both" && -f "${STATE_FILE}") ]]; then
      rm -f "${STATE_FILE}"
      echo "Repository synced and clean. Notification state reset."
    else
      echo "Repository clean and synced. Nothing to do."
    fi
    exit 0
  fi
fi

# Format porcelain status into human-readable labels
format_changes() {
  local input="$1"
  while IFS= read -r line; do
    [[ -z "${line}" ]] && continue
    local code="${line:0:2}"
    local path="${line:3}"
    local label=""

    case "${code}" in
      '??')           label="untracked" ;;
      ' M')           label="modified" ;;
      'M ')           label="staged modified" ;;
      'MM')           label="staged & modified" ;;
      'A ')           label="staged new" ;;
      'AM')           label="staged new (modified)" ;;
      ' D')           label="deleted" ;;
      'D ')           label="staged deleted" ;;
      'R '|'RM')      label="renamed" ;;
      'UU'|'AA'|'DD') label="conflict" ;;
      *)              label="${code// /}" ;;
    esac

    printf "  %-20s %s\n" "[${label}]" "${path}"
  done <<< "${input}"
}

# Build notification content
if [[ "${IS_DIRTY}" == "true" ]]; then
  BODY_CONTENT="Repository: ${REPO_DIR}
Branch: ${BRANCH}
Host: ${HOST}
Date: $(date -R)
"

  if [[ -n "${DIRTY_MATCH}" ]]; then
    FORMATTED_CHANGES="$(format_changes "${DIRTY_MATCH}")"
    BODY_CONTENT+="
Uncommitted / Untracked Changes:
${FORMATTED_CHANGES}
"
  fi

  if [[ "${UNPUSHED_COUNT}" -gt 0 ]]; then
    BODY_CONTENT+="
Unpushed Commits (${UNPUSHED_COUNT}):
${UNPUSHED_COMMITS}
"
  fi

  BODY_CONTENT+="
Please review, commit, and push your changes."
else
  STATUS_TEXT="Clean and synced with upstream."
  if [[ "${FORCE}" == "true" ]]; then
    STATUS_TEXT="Clean (test trigger)"
  fi

  BODY_CONTENT="Repository: ${REPO_DIR}
Branch: ${BRANCH}
Host: ${HOST}
Date: $(date -R)

Repository status: ${STATUS_TEXT}

Repository is clean and up to date."
fi

echo "Sending notification via Mailrise (${MAILRISE_URL})..."

CURL_ARGS=(
  -fsSL
  --url "${MAILRISE_URL}"
  --mail-from "${MAILRISE_FROM}"
  --mail-rcpt "${MAILRISE_TO}"
)

if [[ -n "${MAILRISE_USER}" && -n "${MAILRISE_PASSWORD}" ]]; then
  CURL_ARGS+=(--user "${MAILRISE_USER}:${MAILRISE_PASSWORD}")
fi

if curl "${CURL_ARGS[@]}" --upload-file - <<EOF
From: Antigravity Config <${MAILRISE_FROM}>
To: ${MAILRISE_TO}
Subject: ${SUBJECT}

${BODY_CONTENT}
EOF
then
  mkdir -p "$(dirname "${STATE_FILE}")"
  echo "${NEW_STATE}" > "${STATE_FILE}"
  echo "Notification sent successfully. State saved to ${STATE_FILE}."
else
  echo "Failed to send notification via Mailrise." >&2
  exit 1
fi
