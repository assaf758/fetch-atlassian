# atlassian-access

A Claude Code skill that fetches, searches, and summarizes Jira issues and Confluence pages from your Atlassian instance using the REST API.

## What it does

When you paste a Jira issue key (e.g. `ML-12447`) or a Confluence page URL into Claude Code, this skill automatically fetches the content and presents a clean summary. You can also search for tickets in natural language — Claude translates your query to JQL and returns a results table. You can then ask follow-up questions about any ticket or page.

**Supported inputs:**
- Jira issue key: `ML-12447`, etc.
- Jira URL: `https://yourorg.atlassian.net/browse/ML-12447`
- Confluence URL: `https://yourorg.atlassian.net/wiki/spaces/SPACE/pages/123456789/...`
- Natural language search: "show me open bugs assigned to me in project ML"

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_GITHUB_USER/atlassian-access/main/install.sh | bash
```

Re-run the same command to update to the latest version.

**For developers:** clone directly into the skills directory:

```bash
git clone https://github.com/YOUR_GITHUB_USER/atlassian-access.git ~/.claude/skills/atlassian-access
```

## Configuration

### 1. Generate an Atlassian API token

Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) and create a new token.

### 2. Add credentials to Claude Code settings

Open (or create) `~/.claude/settings.json` and add your Atlassian email and API token under the `env` key:

```json
{
  "env": {
    "JIRA_EMAIL": "your-email@example.com",
    "JIRA_API_TOKEN": "your-api-token-here",
    "ATLASSIAN_SITE": "yourorg.atlassian.net"
  }
}
```

| Variable | Required | Description |
|----------|----------|-------------|
| `JIRA_EMAIL` | Yes | Your Atlassian account email |
| `JIRA_API_TOKEN` | Yes | API token generated above |
| `ATLASSIAN_SITE` | Yes | Your Atlassian domain, e.g. `yourorg.atlassian.net` |

> These environment variables are loaded automatically by Claude Code at startup, so the skill can use them without any extra steps.

### 3. Fetch custom field names (first-time setup)

After setting your credentials, ask Claude to populate the custom field name mapping:

```
update my jira custom fields
```

This calls `fetch.sh update-fields`, which fetches all field definitions from your Jira instance and writes them to `custom_fields.json` in the skill directory. Without this step, custom fields will appear with raw IDs (e.g. `customfield_10037`) instead of human-readable names (e.g. `Severity`).

Re-run this any time your Jira instance adds new custom fields.

## Usage

Just paste a Jira issue key or Atlassian URL into the chat. Claude will detect it and fetch the content automatically.

**Examples:**

```
Summarize ML-12447
```

```
https://yourorg.atlassian.net/browse/ML-12447
```

```
https://yourorg.atlassian.net/wiki/spaces/ENG/pages/123456789/My-Page
```

You can also search for tickets in natural language — Claude translates to JQL automatically:

```
show me open bugs assigned to me in project ML
```

```
find all In Progress tickets in project ML with priority High
```

Or use JQL directly:

```
search jira: project = ML AND assignee = currentUser() AND status != Done
```

And ask follow-up questions after fetching:

```
What's the priority of ML-12447 and who is assigned to it?
```

```
What is the root cause of ML-12447?
```

```
Who should I talk to about ML-12447?
```

### Writing / updating tickets

Add a comment:

```
add a comment to ML-12447: investigated and confirmed the issue is in the frames client
```

Change a field (priority, severity, etc.):

```
set the severity of ML-12447 to High
```

Transition status:

```
move ML-12447 to In Progress
```

Confluence — add a comment or update a page body:

```
add a comment to confluence page 123456789: reviewed and approved
```

```
update confluence page 123456789 with: <new content>
```

## Relationship to the official Atlassian plugin

Claude Code has an official Atlassian plugin (available via the plugin marketplace) that also provides Jira/Confluence access. The recommended setup is to **keep this skill enabled** as your default, and only install the official plugin if you need capabilities it offers beyond this skill. Main reason: the skill consumes <100 tokens from the context, while the plugin (if enabled) requires ~10K tokens.

If you do install the official plugin and want to avoid duplicate responses, disable this skill via `skipSkills` in `~/.claude/settings.json`:

```json
{
  "skipSkills": ["atlassian-access"]
}
```

Or conversely, disable the plugin while keeping this skill:

```json
{
  "enabledPlugins": {
    "atlassian@<marketplace>": false
  }
}
```

Remove the entry (or set `enabledPlugins` back to `true`) to re-enable.

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Skill definition loaded by Claude Code |
| `access.sh` | Shell script that calls the Atlassian REST API |
| `parse_jira.py` | Parses and formats Jira issue JSON |
| `parse_search.py` | Parses and formats Jira search results as a table |
| `parse_confluence.py` | Parses and formats Confluence page JSON |
| `fetch_fields.py` | Writes custom field ID → name mappings to `custom_fields.json` |
| `custom_fields.json` | Per-instance field name map and suppress list (not committed) |

## Requirements

- `curl` (for API calls)
- `python3` (for JSON parsing)
