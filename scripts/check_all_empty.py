import json, glob, os
from collections import Counter

BASE = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems'

all_files = sorted(glob.glob(f'{BASE}/*.json'))
empty = []
has_content = []
by_prefix = Counter()

for f in all_files:
    with open(f) as fp:
        d = json.load(fp)
    fid = d.get('id', os.path.basename(f).replace('.json',''))
    prefix = fid[0] if fid else '?'
    paras = d.get('paragraphs', [])
    by_prefix[prefix] += 1
    if not paras:
        empty.append({
            'id': fid, 
            'title': d.get('title',''), 
            'type': d.get('type',''), 
            'location': d.get('location',''),
            'prefix': prefix
        })
    else:
        has_content.append(fid)

print(f'Total files: {len(all_files)}')
print(f'Has content: {len(has_content)}')
print(f'Empty (no paragraphs): {len(empty)}')
print()

# Empty by prefix
empty_by_prefix = Counter(e['prefix'] for e in empty)
print('Empty by prefix:', dict(empty_by_prefix))

# Empty by type
empty_by_type = Counter(e['type'] for e in empty)
print('Empty by type:', dict(empty_by_type))

print(f'\n=== ALL {len(empty)} EMPTY ENTRIES ===')
for e in empty:
    print(f"{e['id']}: {e['title']} | type={e['type']} | loc={e['location']}")
