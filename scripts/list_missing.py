#!/usr/bin/env python3
"""List all poems missing reading or gold_quote."""
import json, os

poems_dir = 'public/data-v4/poems'
missing_reading = []
missing_gold = []

for fname in sorted(os.listdir(poems_dir)):
    if not fname.endswith('.json'): continue
    pid = fname.replace('.json','')
    fpath = os.path.join(poems_dir, fname)
    with open(fpath) as f:
        p = json.load(f)
    ptype = p.get('type','')
    if ptype not in ('诗', '词'): continue
    if not p.get('reading'):
        missing_reading.append(f"{pid}: {p['title']} ({ptype})")
    if not p.get('gold_quote'):
        missing_gold.append(f"{pid}: {p['title']} ({ptype})")

print(f"Missing reading ({len(missing_reading)}):")
for m in missing_reading:
    print(f"  {m}")
print(f"\nMissing gold_quote ({len(missing_gold)}):")
for m in missing_gold:
    print(f"  {m}")
