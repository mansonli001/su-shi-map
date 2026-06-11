import json
from collections import Counter

with open('/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems-index.json') as f:
    idx = json.load(f)

# Count by type
type_counts = Counter(p.get('type','') for p in idx['poems'])
print('By type:', dict(type_counts))

# Count C-prefix entries
c_entries = [p for p in idx['poems'] if p['id'].startswith('C')]
s_entries = [p for p in idx['poems'] if p['id'].startswith('S')]
print(f'\nC-prefix entries: {len(c_entries)}')
print(f'S-prefix entries: {len(s_entries)}')

# Check C entries - do any have has_full_text=True?
c_with_content = [p for p in c_entries if p.get('has_full_text')]
c_without_content = [p for p in c_entries if not p.get('has_full_text')]
print(f'C entries with has_full_text: {len(c_with_content)}')
print(f'C entries without has_full_text: {len(c_without_content)}')

# Show some C entries
print('\nSample C entries:')
for p in c_entries[:10]:
    print(f'  {p["id"]}: {p["title"]} | type={p.get("type","")} | has_full_text={p.get("has_full_text",False)} | route={p.get("route_id","")}')

# Check S entries with/without content
s_with = [p for p in s_entries if p.get('has_full_text')]
s_without = [p for p in s_entries if not p.get('has_full_text')]
print(f'\nS entries with has_full_text: {len(s_with)}')
print(f'S entries without has_full_text: {len(s_without)}')
