#!/usr/bin/env python3
"""输出87个空白地点的完整列表，按路线分组"""
import json, os
from collections import defaultdict

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

places = pi['places']

# 找出87个空白地点
weak_by_route = defaultdict(list)
for p in places:
    pid = p['id']
    pf = os.path.join('data-v4/places', f'{pid}.json')
    if os.path.exists(pf):
        with open(pf) as fh:
            pd = json.load(fh)
        has_e = pd.get('global_events') and len(pd['global_events']) > 0
        has_w = pd.get('global_works') and len(pd['global_works']) > 0
        has_f = pd.get('foods') and len(pd['foods']) > 0
        has_m = pd.get('memorial_sites') and len(pd['memorial_sites']) > 0
        if not has_e and not has_w and not has_f and not has_m:
            for rid in p.get('related_routes', []):
                weak_by_route[rid].append({
                    'id': pid,
                    'ancient_name': p.get('ancient_name', ''),
                    'modern_name': p.get('modern_name', ''),
                    'type': p.get('type', ''),
                })

for rid in sorted(weak_by_route.keys()):
    places_list = weak_by_route[rid]
    print(f"\n=== {rid} ({len(places_list)}个空白地点) ===")
    for p in places_list:
        print(f"  {p['id']} {p['ancient_name']} / {p['modern_name']} ({p['type']})")
