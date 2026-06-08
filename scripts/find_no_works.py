#!/usr/bin/env python3
"""找出缺关联作品的地点"""
import json, os

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

no_works = []
for p in pi['places']:
    pid = p['id']
    pf = f'data-v4/places/{pid}.json'
    if not os.path.exists(pf): continue
    with open(pf) as f:
        pd = json.load(f)
    
    gw = pd.get('global_works', [])
    re = pd.get('route_events', {})
    has_works = len(gw) > 0
    has_route_works = any(len(v) > 0 for v in re.values()) if re else False
    
    if not has_works and not has_route_works:
        no_works.append((pid, pd.get('ancient_name',''), pd.get('type','')))

print(f"缺关联作品的地点: {len(no_works)}")
for pid, name, t in no_works:
    print(f"  {pid} {name} ({t})")
