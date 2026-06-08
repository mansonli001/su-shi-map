#!/usr/bin/env python3
"""列出有事迹但无作品的地点"""
import json, os

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

places = pi['places']
result = []

for p in places:
    pid = p['id']
    pf = os.path.join('data-v4/places', f'{pid}.json')
    if os.path.exists(pf):
        with open(pf) as fh:
            pd = json.load(fh)
        has_e = pd.get('global_events') and len(pd['global_events']) > 0
        has_w = pd.get('global_works') and len(pd['global_works']) > 0
        if has_e and not has_w:
            evt_count = len(pd.get('global_events', []))
            result.append((pid, p.get('ancient_name',''), p.get('type',''), evt_count, p.get('related_routes',[])))

print(f"共 {len(result)} 个地点有事迹但无作品")
for pid, name, ptype, evt_count, routes in result:
    print(f"  {pid} {name} ({ptype}) - {evt_count}个事迹 [{','.join(routes)}]")
