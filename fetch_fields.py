"""
Fetches all custom field names from the Jira API and writes them to custom_fields.json.
Preserves the existing 'suppress' list if the file already exists.
"""
import json, os, sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(SKILL_DIR, 'custom_fields.json')

with open('/tmp/atlassian_result.json') as f:
    all_fields = json.load(f)

names = {
    f['id']: f['name']
    for f in all_fields
    if f['id'].startswith('customfield_')
}

# Preserve existing suppress list
suppress = []
if os.path.exists(OUTPUT):
    with open(OUTPUT) as f:
        existing = json.load(f)
    suppress = existing.get('suppress', [])

with open(OUTPUT, 'w') as f:
    json.dump({'names': names, 'suppress': suppress}, f, indent=2)

print(f"Wrote {len(names)} custom fields to {OUTPUT}")
