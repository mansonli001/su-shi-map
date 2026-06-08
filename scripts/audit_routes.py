#!/usr/bin/env python3
"""路线数据完整性验证"""
import json, os

with open('data-v4/routes-index.json') as f:
    ri = json.load(f)

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

place_map = {p['id']: p for p in pi['places']}

issues = []
route_stats = []

for route in ri['routes']:
    rid = route['id']
    rname = route.get('name', '')
    places_in_route = route.get('places', [])
    
    # 检查路线文件是否存在
    rf = f'data-v4/routes/{rid}.json'
    if not os.path.exists(rf):
        issues.append(f'{rid} {rname}: 路线详情文件不存在')
        continue
    
    with open(rf) as f:
        rd = json.load(f)
    
    # 检查路线中的地点是否存在
    missing_places = []
    for pid in places_in_route:
        if pid not in place_map:
            missing_places.append(pid)
    
    if missing_places:
        issues.append(f'{rid} {rname}: {len(missing_places)}个地点不存在: {missing_places[:3]}')
    
    # 检查路线颜色
    color = route.get('unique_color', '')
    if not color:
        issues.append(f'{rid} {rname}: 缺少路线颜色')
    
    # 检查路线坐标点
    coords = rd.get('coordinates', rd.get('coords', []))
    track = rd.get('track_segments', [])
    place_ids_in_route = []
    for seg in track:
        place_ids_in_route.extend(seg.get('place_ids', []))
    
    if not track:
        issues.append(f'{rid} {rname}: 缺少track_segments')
    
    route_stats.append({
        'id': rid,
        'name': rname,
        'places': len(place_ids_in_route),
        'segments': len(track),
        'color': color[:7] if color else 'N/A',
    })

print(f'路线总数: {len(ri["routes"])}')
print(f'问题数: {len(issues)}')
print()

if issues:
    print('问题列表:')
    for i in issues:
        print(f'  {i}')
else:
    print('所有路线数据完整，无问题')

print()
print('路线概览:')
print(f'{"ID":<6} {"名称":<30} {"地点":<6} {"段数":<6} {"颜色"}')
print('-' * 70)
for s in route_stats:
    print(f'{s["id"]:<6} {s["name"]:<30} {s["places"]:<6} {s["segments"]:<6} {s["color"]}')

# 检查地点的related_routes是否指向有效路线
route_ids = {r['id'] for r in ri['routes']}
orphan_refs = 0
for p in pi['places']:
    for rid in p.get('related_routes', []):
        if rid not in route_ids:
            orphan_refs += 1
            if orphan_refs <= 5:
                print(f'  孤立引用: {p["id"]} {p.get("ancient_name","")} 引用不存在的路线 {rid}')

if orphan_refs:
    print(f'共有 {orphan_refs} 个地点引用了不存在的路线')
else:
    print('所有地点的路线引用均有效')
