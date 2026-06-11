#!/usr/bin/env python3
"""Full validation of all poem data files."""
import json, os

poems_dir = 'public/data-v4/poems'
issues = []

total = 0
has_reading = 0
has_popularity = 0
template_count = 0
missing_fields = 0

TEMPLATE_PHRASES = [
    '他写的是风景，但说的不是风景',
    '表面是一句普通的话，里面藏着他当时真正的心思',
    '他对自然的感知力极强',
    '这句话听起来简单，但仔细想想',
    '正处于人生的某个节点',
    '他总是能在任何处境下找到值得写下来的东西',
    '他不是在诉苦，他只是在描述一个状态',
    '但这个状态本身，比任何诉苦都让人难受',
]

for fname in sorted(os.listdir(poems_dir)):
    if not fname.endswith('.json'): continue
    pid = fname.replace('.json','')
    fpath = os.path.join(poems_dir, fname)
    
    try:
        with open(fpath) as f:
            p = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(f"{pid}: JSON parse error: {e}")
        continue
    
    total += 1
    ptype = p.get('type','')
    
    # Check required fields
    for field in ['id', 'title', 'author', 'type']:
        if not p.get(field):
            issues.append(f"{pid}: missing required field '{field}'")
            missing_fields += 1
    
    # Check popularity_rank
    if 'popularity_rank' in p:
        has_popularity += 1
    else:
        issues.append(f"{pid}: missing popularity_rank")
    
    # Check reading for poems/ci
    if ptype in ('诗', '词'):
        reading = p.get('reading')
        if reading:
            has_reading += 1
            # Check for template phrases
            is_template = False
            for line in reading.get('lines', []):
                explain = line.get('explain', '')
                for tp in TEMPLATE_PHRASES:
                    if tp in explain:
                        is_template = True
                        break
                if is_template: break
            person = reading.get('person', '')
            for tp in TEMPLATE_PHRASES:
                if tp in person:
                    is_template = True
                    break
            if is_template:
                template_count += 1
        else:
            issues.append(f"{pid} ({ptype}): missing reading")
    
    # Check gold_quote and gold_quote_note
    if ptype in ('诗', '词') and not p.get('gold_quote'):
        issues.append(f"{pid}: missing gold_quote")

# Check index
idx_path = 'public/data-v4/poems-index.json'
with open(idx_path) as f:
    idx = json.load(f)

idx_ids = {p['id'] for p in idx['poems']}
file_ids = set()
for fname in os.listdir(poems_dir):
    if fname.endswith('.json'):
        file_ids.add(fname.replace('.json',''))

missing_from_idx = file_ids - idx_ids
extra_in_idx = idx_ids - file_ids

if missing_from_idx:
    issues.append(f"Missing from index: {len(missing_from_idx)} files: {sorted(missing_from_idx)[:10]}")
if extra_in_idx:
    issues.append(f"Extra in index: {len(extra_in_idx)} entries: {sorted(extra_in_idx)[:10]}")

# Check top 30 ranks
top30 = [p for p in idx['poems'] if p.get('popularity_rank', 999) <= 30]
top30.sort(key=lambda x: x.get('popularity_rank', 999))
print("=== Top 30 by popularity_rank ===")
for p in top30:
    print(f"  Rank {p.get('popularity_rank', 999):2d}: {p['id']} - {p['title']}")

print(f"\n=== Summary ===")
print(f"Total files: {total}")
print(f"Has popularity_rank: {has_popularity}")
print(f"Has reading (诗/词): {has_reading}")
print(f"Template reading remaining: {template_count}")
print(f"Missing fields issues: {missing_fields}")
print(f"Index total: {idx['total']}")
print(f"Missing from index: {len(missing_from_idx)}")
print(f"Extra in index: {len(extra_in_idx)}")
print(f"\nTotal issues: {len(issues)}")
for issue in issues[:30]:
    print(f"  - {issue}")
if len(issues) > 30:
    print(f"  ... and {len(issues) - 30} more")
