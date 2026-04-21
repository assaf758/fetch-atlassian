import json, sys

with open('/tmp/atlassian_result.json') as f:
    data = json.load(f)

if 'errorMessages' in data and data['errorMessages']:
    print("Error:", data['errorMessages'], file=sys.stderr)
    sys.exit(1)

issues = data.get('issues', [])
total = data.get('total', len(issues))

if not issues:
    print("No issues found.")
    sys.exit(0)

print(f"Found {total} issue(s){' (showing first ' + str(len(issues)) + ')' if len(issues) < total else ''}:\n")

# Column widths
KEY_W = max(len(i['key']) for i in issues)
KEY_W = max(KEY_W, 3)

statuses = [i['fields'].get('status', {}).get('name', '') or '' for i in issues]
STATUS_W = max((len(s) for s in statuses), default=6)
STATUS_W = max(STATUS_W, 6)

assignees = [(i['fields'].get('assignee') or {}).get('displayName', 'Unassigned') for i in issues]
ASSIGNEE_W = max((len(a) for a in assignees), default=8)
ASSIGNEE_W = max(ASSIGNEE_W, 8)

header = f"{'KEY':<{KEY_W}}  {'STATUS':<{STATUS_W}}  {'ASSIGNEE':<{ASSIGNEE_W}}  SUMMARY"
print(header)
print('-' * min(len(header) + 20, 120))

for issue, status, assignee in zip(issues, statuses, assignees):
    key = issue['key']
    summary = issue['fields'].get('summary', '') or ''
    # Truncate summary so total line stays readable
    max_summary = 120 - KEY_W - STATUS_W - ASSIGNEE_W - 6
    if len(summary) > max_summary:
        summary = summary[:max_summary - 1] + '…'
    print(f"{key:<{KEY_W}}  {status:<{STATUS_W}}  {assignee:<{ASSIGNEE_W}}  {summary}")
