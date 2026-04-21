#!/usr/bin/env bash
set -e

REPO="https://github.com/assaf758/atlassian-access.git"
DEST="${HOME}/.claude/skills/atlassian-access"

if [[ -d "${DEST}/.git" ]]; then
  echo "Updating existing installation..."
  git -C "${DEST}" pull --ff-only
else
  echo "Installing atlassian-access skill..."
  mkdir -p "${HOME}/.claude/skills"
  git clone --depth=1 "${REPO}" "${DEST}"
fi

echo ""
echo "Done. Add your credentials to ~/.claude/settings.json:"
echo ""
echo '  "env": {'
echo '    "JIRA_EMAIL": "you@example.com",'
echo '    "JIRA_API_TOKEN": "<token>",'
echo '    "ATLASSIAN_SITE": "yourorg.atlassian.net"'
echo '  }'
echo ""
echo "Generate a token at: https://id.atlassian.com/manage-profile/security/api-tokens"
