#!/usr/bin/env python3
"""Find missing entries from poems-index.json"""
import json, glob, os

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4"

with open(f'{BASE}/poems-index.json') as f:
    idx = json.load(f)
indexed_ids = {p['id'] for p in idx['poems']}

file_ids = set()
for f in glob.glob(f'{BASE}/poems/*.json'):
    fid = os.path.basename(f).replace('.json','')
    file_ids.add(fid)

missing = sorted(file_ids - indexed_ids)
print(f'Files total: {len(file_ids)}')
print(f'Indexed: {len(indexed_ids)}')
print(f'Missing from index: {len(missing)}')
print()

has_content = []
no_content = []
for fid in missing:
    with open(f'{BASE}/poems/{fid}.json') as f:
        d = json.load(f)
    paras = d.get('paragraphs', [])
    if paras:
        has_content.append({
            'id': fid,
            'title': d.get('title',''),
            'type': d.get('type',''),
            'year': d.get('year',0),
            'location': d.get('location',''),
            'route_id': d.get('route_id',''),
            'coreVerse': d.get('famousQuotes',[''])[0] if d.get('famousQuotes') else d.get('coreVerse','')
        })
    else:
        no_content.append({'id': fid, 'title': d.get('title','')})

print(f'Missing WITH content: {len(has_content)}')
for e in has_content:
    print(f"  {e['id']}: {e['title']} | type={e['type']} | year={e['year']} | loc={e['location']} | route={e['route_id']}")

print(f'\nMissing WITHOUT content: {len(no_content)}')
for e in no_content:
    print(f"  {e['id']}: {e['title']}")

# Also check: indexed but no file
orphaned = sorted(indexed_ids - file_ids)
if orphaned:
    print(f'\nIndexed but NO file: {len(orphaned)}')
    for fid in orphaned:
        print(f"  {fid}")
else:
    print(f'\nNo orphaned index entries.')
