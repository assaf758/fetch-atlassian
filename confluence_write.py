"""
Confluence write operations: update-page.
Called by access.sh with env vars JIRA_EMAIL, JIRA_API_TOKEN, ATLASSIAN_SITE.
"""
import json, os, sys
import urllib.request, urllib.error
import base64

EMAIL = os.environ['JIRA_EMAIL']
TOKEN = os.environ['JIRA_API_TOKEN']
SITE  = os.environ['ATLASSIAN_SITE']
BASE  = f'https://{SITE}'

AUTH = base64.b64encode(f'{EMAIL}:{TOKEN}'.encode()).decode()
HEADERS = {'Authorization': f'Basic {AUTH}', 'Accept': 'application/json', 'Content-Type': 'application/json'}


def request(method, url, data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def cmd_update_page(page_id, new_body):
    # Fetch current page to get title and version
    status, page = request('GET', f'{BASE}/wiki/rest/api/content/{page_id}?expand=version,title')
    if status != 200:
        print(f"ERROR: HTTP {status} fetching page")
        print(json.dumps(page, indent=2))
        sys.exit(1)

    title = page['title']
    next_version = page['version']['number'] + 1

    payload = {
        'version': {'number': next_version},
        'title': title,
        'type': 'page',
        'body': {
            'storage': {
                'value': new_body,
                'representation': 'storage'
            }
        }
    }

    status, body = request('PUT', f'{BASE}/wiki/rest/api/content/{page_id}', payload)
    if status == 200:
        print(f"Page '{title}' (ID: {page_id}) updated to version {next_version}.")
    else:
        print(f"ERROR: HTTP {status}")
        print(json.dumps(body, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'update-page':
        cmd_update_page(sys.argv[2], sys.argv[3])
    else:
        print(f"ERROR: unknown command '{cmd}'")
        sys.exit(1)
