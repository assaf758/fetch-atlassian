#!/usr/bin/env bash
# Usage:
#   access.sh jira <KEY>
#   access.sh confluence <PAGE_ID>
#   access.sh update-fields
#   access.sh search "<jql>"
#   access.sh add-comment <KEY> "<text>"
#   access.sh set-field <KEY> <field-name-or-id> "<value>"
#   access.sh transition <KEY> "<status>"
#   access.sh add-confluence-comment <PAGE_ID> "<text>"
#   access.sh update-page <PAGE_ID> "<new body text>"

set -e

TYPE="${1}"
KEY="${2}"
ARG3="${3}"
ARG4="${4}"

if [[ -z "${JIRA_EMAIL}" || -z "${JIRA_API_TOKEN}" || -z "${ATLASSIAN_SITE}" ]]; then
  echo "ERROR: JIRA_EMAIL, JIRA_API_TOKEN, and ATLASSIAN_SITE must be set"
  exit 1
fi

AUTH="-u ${JIRA_EMAIL}:${JIRA_API_TOKEN}"
BASE="https://${ATLASSIAN_SITE}"
SKILL_DIR="$(dirname "$0")"

# ── Read ──────────────────────────────────────────────────────────────────────

if [[ "${TYPE}" == "jira" ]]; then
  curl -s ${AUTH} -H "Accept: application/json" \
    "${BASE}/rest/api/3/issue/${KEY}?fields=*all" \
    -o /tmp/atlassian_result.json
  python3 "${SKILL_DIR}/parse_jira.py"

elif [[ "${TYPE}" == "confluence" ]]; then
  curl -s ${AUTH} -H "Accept: application/json" \
    "${BASE}/wiki/rest/api/content/${KEY}?expand=body.storage,version,space" \
    -o /tmp/atlassian_result.json
  python3 "${SKILL_DIR}/parse_confluence.py"

elif [[ "${TYPE}" == "update-fields" ]]; then
  curl -s ${AUTH} -H "Accept: application/json" \
    "${BASE}/rest/api/3/field" \
    -o /tmp/atlassian_result.json
  python3 "${SKILL_DIR}/fetch_fields.py"

elif [[ "${TYPE}" == "search" ]]; then
  [[ -z "${KEY}" ]] && { echo "ERROR: Usage: access.sh search \"<jql>\""; exit 1; }
  PAYLOAD=$(python3 -c "import json, sys; print(json.dumps({'jql': sys.argv[1], 'fields': ['summary','status','assignee'], 'maxResults': 50}))" "${KEY}")
  curl -s ${AUTH} -H "Accept: application/json" -H "Content-Type: application/json" \
    -X POST -d "${PAYLOAD}" \
    "${BASE}/rest/api/3/search/jql" \
    -o /tmp/atlassian_result.json
  python3 "${SKILL_DIR}/parse_search.py"

# ── Jira write ────────────────────────────────────────────────────────────────

elif [[ "${TYPE}" == "add-comment" ]]; then
  [[ -z "${ARG3}" ]] && { echo "ERROR: Usage: access.sh add-comment <KEY> \"<text>\""; exit 1; }
  PAYLOAD=$(python3 -c "
import json, sys
print(json.dumps({'body': {'type': 'doc', 'version': 1,
  'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': sys.argv[1]}]}]}}))
" "${ARG3}")
  HTTP=$(curl -s -o /tmp/atlassian_result.json -w "%{http_code}" ${AUTH} \
    -H "Accept: application/json" -H "Content-Type: application/json" \
    -X POST -d "${PAYLOAD}" "${BASE}/rest/api/3/issue/${KEY}/comment")
  [[ "${HTTP}" == "201" ]] && echo "Comment added to ${KEY}." || { echo "ERROR: HTTP ${HTTP}"; cat /tmp/atlassian_result.json; exit 1; }

elif [[ "${TYPE}" == "set-field" ]]; then
  [[ -z "${ARG3}" || -z "${ARG4}" ]] && { echo "ERROR: Usage: access.sh set-field <KEY> <field-name-or-id> \"<value>\""; exit 1; }
  JIRA_EMAIL="${JIRA_EMAIL}" JIRA_API_TOKEN="${JIRA_API_TOKEN}" ATLASSIAN_SITE="${ATLASSIAN_SITE}" \
    python3 "${SKILL_DIR}/jira_write.py" set-field "${KEY}" "${ARG3}" "${ARG4}"

elif [[ "${TYPE}" == "transition" ]]; then
  [[ -z "${ARG3}" ]] && { echo "ERROR: Usage: access.sh transition <KEY> \"<status>\""; exit 1; }
  JIRA_EMAIL="${JIRA_EMAIL}" JIRA_API_TOKEN="${JIRA_API_TOKEN}" ATLASSIAN_SITE="${ATLASSIAN_SITE}" \
    python3 "${SKILL_DIR}/jira_write.py" transition "${KEY}" "${ARG3}"

# ── Confluence write ──────────────────────────────────────────────────────────

elif [[ "${TYPE}" == "add-confluence-comment" ]]; then
  [[ -z "${ARG3}" ]] && { echo "ERROR: Usage: access.sh add-confluence-comment <PAGE_ID> \"<text>\""; exit 1; }
  PAYLOAD=$(python3 -c "
import json, sys
print(json.dumps({'type': 'comment', 'container': {'id': sys.argv[1], 'type': 'page'},
  'body': {'storage': {'value': sys.argv[2], 'representation': 'storage'}}}))
" "${KEY}" "${ARG3}")
  HTTP=$(curl -s -o /tmp/atlassian_result.json -w "%{http_code}" ${AUTH} \
    -H "Accept: application/json" -H "Content-Type: application/json" \
    -X POST -d "${PAYLOAD}" "${BASE}/wiki/rest/api/content")
  [[ "${HTTP}" == "200" ]] && echo "Comment added to page ${KEY}." || { echo "ERROR: HTTP ${HTTP}"; cat /tmp/atlassian_result.json; exit 1; }

elif [[ "${TYPE}" == "update-page" ]]; then
  [[ -z "${ARG3}" ]] && { echo "ERROR: Usage: access.sh update-page <PAGE_ID> \"<new body text>\""; exit 1; }
  JIRA_EMAIL="${JIRA_EMAIL}" JIRA_API_TOKEN="${JIRA_API_TOKEN}" ATLASSIAN_SITE="${ATLASSIAN_SITE}" \
    python3 "${SKILL_DIR}/confluence_write.py" update-page "${KEY}" "${ARG3}"

else
  echo "ERROR: unknown command '${TYPE}'."
  echo "Valid commands: jira, confluence, update-fields, search, add-comment, set-field, transition, add-confluence-comment, update-page"
  exit 1
fi
