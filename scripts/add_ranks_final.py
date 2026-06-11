#!/usr/bin/env python3
"""Add popularity_rank to ALL poems. Top 30 defined, rest get 999."""
import json, os

poems_dir = 'public/data-v4/poems'

# Already ranked 1-25 (24 actually, #11 望江南 missing) from the 25 samples
# Add ranks 26-30 for additional well-known works
# Rank 11 is skipped (望江南 not found), so we use 11 for another famous one
additional = {
    "C040": 11,  # 浣溪沙·簌簌衣巾落枣花 (very famous)
    "C035": 26,  # 西江月·世事一场大梦
    "C034": 27,  # 满庭芳·三十三年
    "S014": 28,  # 游金山寺
    "C014": 29,  # 阳关曲·中秋月
    "C006": 30,  # 江城子·十年生死两茫茫 (another version)
}

# All already-ranked IDs (from import_25_samples.py)
already_ranked = {
    "C012": 1, "C036": 2, "C037": 3, "C002": 4, "S098": 5,
    "S021": 6, "F004": 7, "F005": 8, "W009": 9, "S013": 10,
    "C033": 12, "S017": 13, "S114": 14, "C038": 15, "C008": 16,
    "C003": 17, "C074": 18, "S080": 19, "C046": 20, "S142": 21,
    "S150": 22, "S164": 23, "C039": 24, "S078": 25,
}

# Merge
all_ranks = {**already_ranked, **additional}

updated = 0
for fname in sorted(os.listdir(poems_dir)):
    if not fname.endswith('.json'): continue
    pid = fname.replace('.json','')
    fpath = os.path.join(poems_dir, fname)
    with open(fpath) as f:
        p = json.load(f)
    
    rank = all_ranks.get(pid, 999)
    
    if 'popularity_rank' not in p or p['popularity_rank'] != rank:
        p['popularity_rank'] = rank
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
        updated += 1

print(f"Updated {updated} files with popularity_rank")
print(f"Top 30 poems:")
for pid in sorted(all_ranks, key=all_ranks.get):
    fpath = os.path.join(poems_dir, f"{pid}.json")
    with open(fpath) as f:
        p = json.load(f)
    print(f"  Rank {all_ranks[pid]:2d}: {pid} - {p['title']}")
