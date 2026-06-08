#!/usr/bin/env python3
"""全面审计：按路线统计各地点数据完整度"""
import json, os
from collections import defaultdict

with open('data-v4/places-index.json') as f:
    pi = json.load(f)
with open('data-v4/routes-index.json') as f:
    ri = json.load(f)

places = pi['places']
routes = ri['routes']

# 按路线分组
route_places = defaultdict(list)
for p in places:
    for rid in p.get('related_routes', []):
        route_places[rid].append(p)

print("=" * 80)
print("苏轼行踪路线图 · 数据完整度审计报告")
print("=" * 80)

# 全局统计
total_places = len(places)
has_events = 0
has_works = 0
has_foods = 0
has_memorial = 0
has_sub_with_note = 0
total_subs = 0
subs_with_note = 0
has_global_works = 0
total_works = 0
auto_gen = 0

place_details = {}
for p in places:
    pid = p['id']
    pf = os.path.join('data-v4/places', f'{pid}.json')
    if os.path.exists(pf):
        with open(pf) as fh:
            pd = json.load(fh)
        place_details[pid] = pd
        
        if pd.get('global_events') and len(pd['global_events']) > 0:
            has_events += 1
        if pd.get('global_works') and len(pd['global_works']) > 0:
            has_global_works += 1
            total_works += len(pd['global_works'])
        if pd.get('foods') and len(pd['foods']) > 0:
            has_foods += 1
        if pd.get('memorial_sites') and len(pd['memorial_sites']) > 0:
            has_memorial += 1
        if pd.get('_auto_generated'):
            auto_gen += 1
        
        subs = pd.get('sub_places', [])
        total_subs += len(subs)
        for sp in subs:
            if sp.get('note', '').strip() or sp.get('description', '').strip():
                subs_with_note += 1

print(f"\n{'─' * 40}")
print(f"全局数据概况")
print(f"{'─' * 40}")
print(f"地点总数:        {total_places}")
print(f"有事迹事件:      {has_events}/{total_places} ({100*has_events//total_places}%)")
print(f"有关联作品:      {has_global_works}/{total_places} ({100*has_global_works//total_places}%)")
print(f"作品总数:        {total_works}")
print(f"有美食数据:      {has_foods}/{total_places} ({100*has_foods//total_places}%)")
print(f"有文旅景点:      {has_memorial}/{total_places} ({100*has_memorial//total_places}%)")
print(f"自动生成地点:    {auto_gen}/{total_places}")
print(f"子地点总数:      {total_subs} (有描述: {subs_with_note}, 空: {total_subs - subs_with_note})")

# 按路线统计
print(f"\n{'=' * 80}")
print(f"按路线数据完整度")
print(f"{'=' * 80}")
print(f"{'路线':<8} {'名称':<24} {'地点':>4} {'事迹':>4} {'作品':>4} {'美食':>4} {'文旅':>4} {'自动':>4}")
print(f"{'─' * 80}")

for r in routes:
    rid = r['id']
    rname = r.get('name', '')[:22]
    rps = route_places.get(rid, [])
    r_events = 0
    r_works = 0
    r_foods = 0
    r_memorial = 0
    r_auto = 0
    for p in rps:
        pd = place_details.get(p['id'], {})
        if pd.get('global_events') and len(pd['global_events']) > 0:
            r_events += 1
        if pd.get('global_works') and len(pd['global_works']) > 0:
            r_works += 1
        if pd.get('foods') and len(pd['foods']) > 0:
            r_foods += 1
        if pd.get('memorial_sites') and len(pd['memorial_sites']) > 0:
            r_memorial += 1
        if pd.get('_auto_generated'):
            r_auto += 1
    
    print(f"{rid:<8} {rname:<24} {len(rps):>4} {r_events:>4} {r_works:>4} {r_foods:>4} {r_memorial:>4} {r_auto:>4}")

# 找出数据最薄弱的地点（无事件+无作品+无美食+无文旅）
print(f"\n{'=' * 80}")
print(f"数据最薄弱地点（无事件+无作品+无美食+无文旅）")
print(f"{'=' * 80}")
weak_places = []
for p in places:
    pd = place_details.get(p['id'], {})
    has_e = pd.get('global_events') and len(pd['global_events']) > 0
    has_w = pd.get('global_works') and len(pd['global_works']) > 0
    has_f = pd.get('foods') and len(pd['foods']) > 0
    has_m = pd.get('memorial_sites') and len(pd['memorial_sites']) > 0
    if not has_e and not has_w and not has_f and not has_m:
        weak_places.append((p['id'], p.get('ancient_name',''), p.get('type',''), p.get('related_routes',[])))

print(f"共 {len(weak_places)} 个地点完全无事迹/作品/美食/文旅数据")
for pid, name, ptype, routes in weak_places[:30]:
    print(f"  {pid} {name} ({ptype}) [{','.join(routes)}]")
if len(weak_places) > 30:
    print(f"  ... 还有 {len(weak_places)-30} 个")

# 有事件但无作品的地点
print(f"\n{'=' * 80}")
print(f"有事迹但无作品的地点（优先补充作品）")
print(f"{'=' * 80}")
no_works_but_events = []
for p in places:
    pd = place_details.get(p['id'], {})
    has_e = pd.get('global_events') and len(pd['global_events']) > 0
    has_w = pd.get('global_works') and len(pd['global_works']) > 0
    if has_e and not has_w:
        no_works_but_events.append((p['id'], p.get('ancient_name',''), p.get('type',''), len(pd.get('global_events',[]))))

print(f"共 {len(no_works_but_events)} 个地点有事迹但无作品")
for pid, name, ptype, evt_count in no_works_but_events:
    print(f"  {pid} {name} ({ptype}) - {evt_count}个事迹")

# 有作品但无美食的居住/任职地
print(f"\n{'=' * 80}")
print(f"居住/任职地缺少美食数据（优先补充美食）")
print(f"{'=' * 80}")
no_food_stay = []
for p in places:
    if p.get('type') in ('stay', 'official', 'birth'):
        pd = place_details.get(p['id'], {})
        has_f = pd.get('foods') and len(pd['foods']) > 0
        if not has_f:
            no_food_stay.append((p['id'], p.get('ancient_name',''), p.get('type','')))

print(f"共 {len(no_food_stay)} 个居住/任职地缺少美食数据")
for pid, name, ptype in no_food_stay:
    print(f"  {pid} {name} ({ptype})")
