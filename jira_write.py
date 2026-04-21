"""
Jira write operations: set-field, transition.
Called by access.sh with env vars JIRA_EMAIL, JIRA_API_TOKEN, ATLASSIAN_SITE.
"""
import json, os, sys
import urllib.request, urllib.error

EMAIL = os.environ['JIRA_EMAIL']
TOKEN = os.environ['JIRA_API_TOKEN']
SITE  = os.environ['ATLASSIAN_SITE']
BASE  = f'https://{SITE}'
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))

import base64
AUTH = base64.b64encode(f'{EMAIL}:{TOKEN}'.encode()).decode()
HEADERS = {'Authorization': f'Basic {AUTH}', 'Accept': 'application/json', 'Content-Type': 'application/json'}


def request(method, url, data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read()
            return r.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {}


def load_field_map():
    path = os.path.join(SKILL_DIR, 'custom_fields.json')
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        # Build reverse map: lowercase name → id
        return {v.lower(): k for k, v in data.get('names', {}).items()}
    return {}


def resolve_field_id(field_name_or_id, reverse_map):
    """Return the Jira field ID for a given name or ID."""
    if field_name_or_id.startswith('customfield_') or not field_name_or_id[0].isalpha():
        return field_name_or_id
    return reverse_map.get(field_name_or_id.lower(), field_name_or_id)


def build_field_value(value):
    """Try to build a sensible field payload. Tries object shapes first, falls back to string."""
    # Return multiple candidates to try in order
    return [
        {'value': value},       # select / option fields (e.g. severity)
        {'name': value},        # named fields (e.g. priority)
        value,                  # plain string (e.g. summary, description text)
    ]


def cmd_set_field(key, field_name_or_id, value):
    reverse_map = load_field_map()
    field_id = resolve_field_id(field_name_or_id, reverse_map)

    for candidate in build_field_value(value):
        payload = {'fields': {field_id: candidate}}
        status, body = request('PUT', f'{BASE}/rest/api/3/issue/{key}', payload)
        if status == 204:
            print(f"Field '{field_name_or_id}' updated on {key}.")
            return
        # 400 with "expected" errors means wrong shape — try next candidate
        errors = body.get('errors', {}) or body.get('errorMessages', [])
        if status == 400 and errors:
            continue
        # Unexpected error
        print(f"ERROR: HTTP {status}")
        print(json.dumps(body, indent=2))
        sys.exit(1)

    print(f"ERROR: Could not update field '{field_name_or_id}' — no payload shape accepted.")
    sys.exit(1)


def cmd_transition(key, status_name):
    status, body = request('GET', f'{BASE}/rest/api/3/issue/{key}/transitions')
    if status != 200:
        print(f"ERROR: HTTP {status} fetching transitions")
        print(json.dumps(body, indent=2))
        sys.exit(1)

    transitions = body.get('transitions', [])
    match = next((t for t in transitions if t['name'].lower() == status_name.lower()), None)
    if not match:
        available = [t['name'] for t in transitions]
        print(f"ERROR: status '{status_name}' not found. Available: {', '.join(available)}")
        sys.exit(1)

    status, body = request('POST', f'{BASE}/rest/api/3/issue/{key}/transitions',
                           {'transition': {'id': match['id']}})
    if status == 204:
        print(f"{key} transitioned to '{match['name']}'.")
    else:
        print(f"ERROR: HTTP {status}")
        print(json.dumps(body, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'set-field':
        cmd_set_field(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'transition':
        cmd_transition(sys.argv[2], sys.argv[3])
    else:
        print(f"ERROR: unknown command '{cmd}'")
        sys.exit(1)
