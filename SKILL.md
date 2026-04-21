---
name: atlassian-access
description: Fetch, summarize, search, and update Jira issues or Confluence pages from your Atlassian instance using the REST API. Use when the user provides a Jira issue key (e.g. IG4-1369) or URL, wants a summary, wants to search issues with natural language or JQL, or wants to update a ticket (add comment, set field, transition status).
---

# Jira / Confluence via REST API

Read and write Jira issues and Confluence pages using Basic auth (email + API token).

## Prerequisites

`JIRA_EMAIL`, `JIRA_API_TOKEN`, and `ATLASSIAN_SITE` must be set (configured in `~/.claude/settings.json` under `env`).
If missing, tell the user to add them and generate a token at: https://id.atlassian.com/manage-profile/security/api-tokens

## Step 1: Determine the operation and extract identifiers

**Read operations:**
- Jira URL: `https://<site>/browse/<KEY>` → extract `<KEY>`, use `jira` command
- Plain key: `IG4-1369`, `ML-123`, etc. → use `jira` command
- Confluence URL: `https://<site>/wiki/spaces/<SPACE>/pages/<ID>/...` → extract `<ID>`, use `confluence` command
- Natural language query ("show me open bugs assigned to me", "find tickets in project X") → translate to JQL, use `search` command

**Write operations** — detect intent from user message:
- "add a comment" → `add-comment`
- "set/change [field]" (severity, priority, assignee, etc.) → `set-field`
- "transition / move to [status]" → `transition`
- "add a comment to confluence page" → `add-confluence-comment`
- "update confluence page" → `update-page`

## Step 2: Run the command

```bash
bash /Users/Assaf_Ben_Amitai/.claude/skills/atlassian-access/access.sh <command> [args]
```

| Command | Args | Description |
|---|---|---|
| `jira` | `<KEY>` | Fetch and display a Jira issue |
| `confluence` | `<PAGE_ID>` | Fetch and display a Confluence page |
| `update-fields` | — | Refresh custom field name mappings |
| `search` | `"<jql>"` | Search issues by JQL, returns key/status/assignee/summary |
| `add-comment` | `<KEY> "<text>"` | Add a comment to a Jira issue |
| `set-field` | `<KEY> <field-name> "<value>"` | Update any Jira field (e.g. severity, priority) |
| `transition` | `<KEY> "<status>"` | Move a Jira issue to a new status |
| `add-confluence-comment` | `<PAGE_ID> "<text>"` | Add a footer comment to a Confluence page |
| `update-page` | `<PAGE_ID> "<body>"` | Replace a Confluence page's body content |

## Step 3: Present results

- For read operations: present a clean, readable summary.
- For write operations: confirm success or report the error.
- Answer follow-up questions based on fetched data.
