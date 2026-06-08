#!/usr/bin/env python3
"""全面审计地点/作品/文旅/美食数据"""
import json, os
from collections import Counter

# 加载数据
with open('data-v4/places-index.json') as f:
    pi = json.load(f)
with open('data-v4/routes-index.json') as f:
    ri = json.load(f)

places = pi['places']
routes = ri['routes']

print('=== 基础统计 ===')
print(f'地点总数: {len(places)}')
print(f'路线总数: {len(routes)}')

# 地点类型分布
type_c = Counter(p.get('type','') for p in places)
print(f'\n=== 地点类型分布 ===')
for t, c in type_c.most_common():
    print(f'  {t or "(空)"}: {c}')

# 子地点统计
sub_total = 0
sub_type_c = Counter()
sub_empty_note = 0
places_with_subs = 0
for p in places:
    pid = p['id']
    pf = os.path.join('data-v4/places', f'{pid}.json')
    if os.path.exists(pf):
        with open(pf) as fh:
            pd = json.load(fh)
        subs = pd.get('sub_places', [])
        if subs:
            places_with_subs += 1
            sub_total += len(subs)
            for sp in subs:
                st = sp.get('type', '')
                sub_type_c[st] += 1
                if not sp.get('note', '').strip():
                    sub_empty_note += 1

print(f'\n=== 子地点统计 ===')
print(f'有子地点的主地点: {places_with_subs}')
print(f'子地点总数: {sub_total}')
print(f'子地点空note: {sub_empty_note}')
print(f'子地点类型分布:')
for t, c in sub_type_c.most_common():
    print(f'  {t or "(空)"}: {c}')

# 作品统计
works_count = 0
places_with_works = 0
works_by_route = Counter()
for p in places:
    pid = p['id']
    pf = os.path.join('data-v4/places', f'{pid}.json')
    if os.path.exists(pf):
        with open(pf) as fh:
            pd = json.load(fh)
        w = pd.get('works', [])
        if w:
            places_with_works += 1
            works_count += len(w)
            for rid in p.get('related_routes', []):
                works_by_route[rid] += len(w)

print(f'\n=== 作品统计 ===')
print(f'有作品关联的地点: {places_with_works}/{len(places)}')
print(f'作品总数: {works_count}')
print(f'各路线作品数:')
for rid in sorted(works_by_route.keys()):
    print(f'  {rid}: {works_by_route[rid]}')

# 文旅/美食统计
food_count = 0
food_places = 0
culture_count = 0
culture_places = 0
for p in places:
    pid = p['id']
    pf = os.path.join('data-v4/places', f'{pid}.json')
    if os.path.exists(pf):
        with open(pf) as fh:
            pd = json.load(fh)
        food = pd.get('food', [])
        culture = pd.get('culture', [])
        if food:
            food_places += 1
            food_count += len(food)
        if culture:
            culture_places += 1
            culture_count += len(culture)

print(f'\n=== 文旅/美食统计 ===')
print(f'美食条目: {food_count} (涉及{food_places}个地点)')
print(f'文旅条目: {culture_count} (涉及{culture_places}个地点)')

# GPS统计
gps_ok = 0
gps_missing = 0
for p in places:
    if p.get('lat') and p.get('lng'):
        gps_ok += 1
    else:
        gps_missing += 1
print(f'\n=== GPS统计 ===')
print(f'有坐标: {gps_ok}')
print(f'缺坐标: {gps_missing}')

# 各路线地点数
route_place_count = Counter()
for p in places:
    for rid in p.get('related_routes', []):
        route_place_count[rid] += 1
print(f'\n=== 各路线地点数 ===')
for r in routes:
    rid = r['id']
    print(f'  {rid} {r.get("name","")}: {route_place_count.get(rid, 0)}个地点')

# 检查地点详情文件完整性
missing_detail = []
for p in places:
    pid = p['id']
    pf = os.path.join('data-v4/places', f'{pid}.json')
    if not os.path.exists(pf):
        missing_detail.append(pid)

print(f'\n=== 详情文件完整性 ===')
print(f'缺失详情文件: {len(missing_detail)}')
if missing_detail:
    print(f'  缺失: {missing_detail[:20]}')
