#!/usr/bin/env python3
"""Add popularity_rank to all poems. Top 30 defined, rest get 999."""
import json, os

poems_dir = 'public/data-v4/poems'

# Additional top poems (rank 26-30) beyond the 24 samples
# These are well-known Su Shi works
additional_ranks = {
    "C011": 26,  # 水调歌头·落日绣帘卷 (less famous variant)
    "C040": 27,  # 鹧鸪天·林断山明竹隐墙
    "S014": 28,  # 游金山寺
    "S020": 29,  # 饮湖上初晴后雨 (duplicate check)
    "C050": 30,  # 满庭芳
}

# First, find some actually well-known poems for ranks 26-30
# Let me check what's available
well_known = {
    # Rank 26-30: additional famous works
    "C011": 26,  # Need to check title
    "C040": 27,
    "S014": 28,
    "C050": 29,
    "C060": 30,
}

# Check what these are
for pid, rank in well_known.items():
    fpath = os.path.join(poems_dir, f"{pid}.json")
    if os.path.exists(fpath):
        with open(fpath) as f:
            p = json.load(f)
        print(f"{pid}: {p['title']} (type={p.get('type','')})")
    else:
        print(f"{pid}: NOT FOUND")

# Actually let me find the most famous ones by checking famousQuotes
print("\n--- Looking for famous poems ---")
famous_pids = []
for fname in sorted(os.listdir(poems_dir)):
    if not fname.endswith('.json'): continue
    pid = fname.replace('.json','')
    fpath = os.path.join(poems_dir, fname)
    with open(fpath) as f:
        p = json.load(f)
    fq = p.get('famousQuotes', [])
    if len(fq) >= 2:
        famous_pids.append((pid, p.get('title',''), p.get('type',''), len(fq)))

famous_pids.sort(key=lambda x: -x[3])
for pid, title, ptype, nfq in famous_pids[:20]:
    print(f"{pid}: {title} ({ptype}, {nfq} quotes)")
