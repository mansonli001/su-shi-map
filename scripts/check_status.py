import json, glob, os

BASE = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map'

# Check both directories
for base in [f'{BASE}/public/data-v4/poems', f'{BASE}/data-v4/poems']:
    files = sorted(glob.glob(f'{base}/S*.json'))
    print(f'{base}: {len(files)} files')

# Check index vs files mismatch
with open(f'{BASE}/public/data-v4/poems-index.json') as f:
    idx = json.load(f)

indexed_ids = {p['id'] for p in idx['poems']}
file_ids = {os.path.basename(f).replace('.json','') for f in glob.glob(f'{BASE}/public/data-v4/poems/S*.json')}

in_index_not_file = sorted(indexed_ids - file_ids)
in_file_not_index = sorted(file_ids - indexed_ids)

print(f'\nIn index but no file: {len(in_index_not_file)}')
if in_index_not_file:
    for i in in_index_not_file[:30]:
        # find the title in index
        title = next((p['title'] for p in idx['poems'] if p['id'] == i), '')
        print(f'  {i}: {title}')
    if len(in_index_not_file) > 30:
        print(f'  ... and {len(in_index_not_file)-30} more')

print(f'\nIn file but not index: {len(in_file_not_index)}')
if in_file_not_index:
    for i in in_file_not_index[:20]:
        print(f'  {i}')

# Check empty entries
empty_entries = []
for f in sorted(glob.glob(f'{BASE}/public/data-v4/poems/S*.json')):
    with open(f) as fp:
        d = json.load(fp)
    if not d.get('paragraphs', []):
        empty_entries.append(d.get('id', ''))

print(f'\nEmpty entries (no paragraphs): {len(empty_entries)}')
