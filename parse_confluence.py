import json, re, sys

with open('/tmp/atlassian_result.json') as f:
    data = json.load(f)

if 'statusCode' in data and data['statusCode'] != 200:
    print("Error:", data.get('message', 'Unknown error'), file=sys.stderr)
    sys.exit(1)

print(f"Title:   {data.get('title')}")
print(f"Space:   {data.get('space', {}).get('name')}")
print(f"Version: {data.get('version', {}).get('number')}")

html = data.get('body', {}).get('storage', {}).get('value', '')
text = re.sub(r'<[^>]+>', ' ', html)
text = re.sub(r'\s+', ' ', text).strip()
print(f"\nContent (truncated):\n{text[:2000]}")
