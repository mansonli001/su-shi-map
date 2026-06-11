#!/usr/bin/env python3
"""Rebuild poems-index.json from all actual poem files.
Ensures every poem file is represented in the index."""
import json, glob, os
from datetime import datetime

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4"

# Load existing index for reference
with open(f'{BASE}/poems-index.json') as f:
    old_idx = json.load(f)

# Build lookup from old index
old_lookup = {p['id']: p for p in old_idx['poems']}

# Scan all poem files
new_poems = []
has_full_text = 0

for f in sorted(glob.glob(f'{BASE}/poems/*.json')):
    fid = os.path.basename(f).replace('.json','')
    with open(f) as fp:
        d = json.load(fp)
    
    paras = d.get('paragraphs', [])
    has_content = bool(paras and len(paras) > 0)
    
    if has_content:
        has_full_text += 1
    
    # Build index entry - prefer existing index data, fill gaps from file
    old_entry = old_lookup.get(fid, {})
    
    entry = {
        'id': fid,
        'title': d.get('title', ''),
        'type': d.get('type', ''),
        'year': d.get('year', 0),
        'route_id': old_entry.get('route_id', d.get('route_id', '')),
        'related_route_ids': old_entry.get('related_route_ids', [d.get('route_id', '')] if d.get('route_id') else []),
        'has_full_text': has_content,
        'popularity_rank': d.get('popularity_rank', 999),
        'coreVerse': d.get('famousQuotes', [''])[0] if d.get('famousQuotes') else d.get('coreVerse', old_entry.get('coreVerse', ''))
    }
    
    # Clean up empty related_route_ids
    entry['related_route_ids'] = [r for r in entry['related_route_ids'] if r]
    
    new_poems.append(entry)

# Sort by ID
new_poems.sort(key=lambda x: x['id'])

# Build new index
new_idx = {
    'total': len(new_poems),
    'has_full_text': has_full_text,
    'pending_full_text': len(new_poems) - has_full_text,
    'poems': new_poems,
    'generated_at': datetime.now().isoformat()
}

# Write to both locations
for path in [f'{BASE}/poems-index.json', BASE.replace('public/', '') + '/poems-index.json']:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(new_idx, f, ensure_ascii=False, indent=2)
    print(f'Written: {path}')

print(f'\nIndex rebuilt:')
print(f'  Total: {new_idx["total"]}')
print(f'  Has full text: {new_idx["has_full_text"]}')
print(f'  Pending: {new_idx["pending_full_text"]}')
print(f'  Old total was: {old_idx["total"]}')
print(f'  Added: {new_idx["total"] - old_idx["total"]} entries')
