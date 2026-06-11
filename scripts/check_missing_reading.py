#!/usr/bin/env python3
"""Batch add reading content to poems missing it, following 行吟山河 standards."""
import json, os

poems_dir = 'public/data-v4/poems'

# Collect missing reading poems that have actual content (not just index entries)
missing = []
for fname in sorted(os.listdir(poems_dir)):
    if not fname.endswith('.json'): continue
    pid = fname.replace('.json','')
    fpath = os.path.join(poems_dir, fname)
    with open(fpath) as f:
        p = json.load(f)
    if p.get('type','') not in ('诗', '词'): continue
    if p.get('reading'): continue
    
    paras = p.get('paragraphs', [])
    # Check if it has real content (more than just one short line)
    has_real_content = False
    if paras:
        total_chars = sum(len(line) for line in paras)
        if total_chars > 20:  # More than just a brief note
            has_real_content = True
    
    if has_real_content:
        missing.append((pid, p.get('title',''), p.get('year',0), p.get('location',''), p.get('route_id',''), paras))

print(f"Poems with real content but missing reading: {len(missing)}")
for pid, title, year, loc, rid, paras in missing:
    first_line = paras[0][:30] if paras else ''
    print(f"  {pid}: {title} (year={year}, loc={loc}, route={rid}) - {first_line}...")
