#!/usr/bin/env python3
"""列出居住/任职地缺少美食数据的地点"""
import json, os

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

places = pi['places']
result = []

for p in places:
    if p.get('type') in ('stay', 'official', 'birth'):
        pid = p['id']
        pf = os.path.join('data-v4/places', f'{pid}.json')
        if os.path.exists(pf):
            with open(pf) as fh:
                pd = json.load(fh)
            has_f = pd.get('foods') and len(pd['foods']) > 0
            if not has_f:
                result.append((pid, p.get('ancient_name',''), p.get('type',''), p.get('related_routes',[])))

print(f"共 {len(result)} 个居住/任职地缺少美食数据")
for pid, name, ptype, routes in result:
    print(f"  {pid} {name} ({ptype}) [{','.join(routes)}]")
