#!/usr/bin/env python3
"""Analyze empty entries and stats discrepancy."""
import json, glob
from collections import Counter

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems"

empty = []
has_content = []
for f in sorted(glob.glob(f'{BASE}/*.json')):
    with open(f) as fp:
        d = json.load(fp)
    fid = f.replace('.json','').split('/')[-1]
    paras = d.get('paragraphs', [])
    title = d.get('title','')
    ptype = d.get('type','')
    year = d.get('year',0)
    loc = d.get('location','')
    if not paras or len(paras) == 0:
        empty.append({'id':fid, 'title':title, 'type':ptype, 'year':year, 'loc':loc})
    else:
        has_content.append(fid)

print(f'=== EMPTY ENTRIES ({len(empty)}) ===')
for e in empty:
    print(f"  {e['id']}: {e['title']} | type={e['type']} | year={e['year']} | loc={e['loc']}")

print(f'\n=== STATS ===')
print(f'Total files: {len(empty)+len(has_content)}')
print(f'Has content: {len(has_content)}')
print(f'Empty: {len(empty)}')

type_counts = Counter(e['type'] for e in empty)
print(f'\nEmpty by type: {dict(type_counts)}')

# Check which empty ones are place names vs actual poems
place_names = [e for e in empty if not e['type'] or e['type'] == '']
poems_no_para = [e for e in empty if e['type'] and e['type'] != '']
print(f'\nPlace/index entries (no type): {len(place_names)}')
print(f'Poems with type but no paragraphs: {len(poems_no_para)}')
for e in poems_no_para:
    print(f"  {e['id']}: {e['title']} | type={e['type']}")
