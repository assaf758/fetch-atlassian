import json, os, sys

with open('/tmp/atlassian_result.json') as f:
    data = json.load(f)

if 'errorMessages' in data and data['errorMessages']:
    print("Error:", data['errorMessages'], file=sys.stderr)
    sys.exit(1)

fields = data['fields']

# Load custom field names and suppress list from file (run 'access.sh update-fields' to populate)
_cf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_fields.json')
if os.path.exists(_cf_path):
    with open(_cf_path) as f:
        _cf = json.load(f)
    CUSTOM_FIELD_NAMES = _cf.get('names', {})
    SUPPRESS = set(_cf.get('suppress', []))
else:
    CUSTOM_FIELD_NAMES = {}
    SUPPRESS = set()

# Fields handled explicitly (skip in the extras dump)
HANDLED = {'summary', 'issuetype', 'status', 'priority', 'assignee', 'reporter',
           'labels', 'fixVersions', 'description', 'comment',
           'customfield_10014', 'customfield_10020', 'customfield_10037'}


def scalar(value):
    """Return a printable string for a field value, or None if empty."""
    if value is None:
        return None
    if isinstance(value, str):
        return value or None
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        parts = [scalar(v) for v in value]
        parts = [p for p in parts if p]
        return ', '.join(parts) or None
    if isinstance(value, dict):
        for key in ('displayName', 'name', 'value', 'id'):
            if value.get(key):
                return str(value[key])
    return None


def extract_text(node, out):
    if node.get('type') == 'text':
        out.append(node.get('text', ''))
    for child in node.get('content', []):
        extract_text(child, out)


# Sprint: list of sprint objects
sprint_val = fields.get('customfield_10020')
sprint_str = 'None'
if sprint_val:
    if isinstance(sprint_val, list) and sprint_val:
        sprint_str = sprint_val[-1].get('name', 'N/A')
    elif isinstance(sprint_val, dict):
        sprint_str = sprint_val.get('name', 'N/A')

severity_val = fields.get('customfield_10037')
severity_str = scalar(severity_val) or 'N/A'

print(f"Key:       {data['key']}")
print(f"Summary:   {fields.get('summary', 'N/A')}")
print(f"Type:      {fields.get('issuetype', {}).get('name', 'N/A')}")
print(f"Status:    {fields.get('status', {}).get('name', 'N/A')}")
print(f"Priority:  {fields.get('priority', {}).get('name', 'N/A')}")
print(f"Severity:  {severity_str}")
print(f"Assignee:  {(fields.get('assignee') or {}).get('displayName', 'Unassigned')}")
print(f"Reporter:  {(fields.get('reporter') or {}).get('displayName', 'N/A')}")
print(f"Sprint:    {sprint_str}")
fix_versions = ', '.join(v.get('name', '') for v in fields.get('fixVersions') or []) or 'None'
print(f"Fix Ver:   {fix_versions}")
print(f"Labels:    {', '.join(fields.get('labels', [])) or 'None'}")

# Extra non-null custom fields
extras = []
for k, v in sorted(fields.items()):
    if k in HANDLED or k in SUPPRESS or not k.startswith('customfield_'):
        continue
    s = scalar(v)
    if s:
        name = CUSTOM_FIELD_NAMES.get(k, k)
        extras.append((name, s))

if extras:
    print("\nOther fields:")
    for name, val in extras:
        print(f"  {name+':':<35} {val[:120]}")

# Description
desc = fields.get('description')
if desc and desc.get('content'):
    texts = []
    for block in desc['content']:
        extract_text(block, texts)
        texts.append('\n')
    print(f"\nDescription:\n{''.join(texts).strip()}")

# Comments
comments = (fields.get('comment') or {}).get('comments', [])
if comments:
    print(f"\nComments ({len(comments)} total, last 3):")
    for c in comments[-3:]:
        author = (c.get('author') or {}).get('displayName', 'Unknown')
        body_texts = []
        if c.get('body', {}).get('content'):
            for block in c['body']['content']:
                extract_text(block, body_texts)
                body_texts.append('\n')
        print(f"  [{author}]: {''.join(body_texts).strip()[:300]}")
