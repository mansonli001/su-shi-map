#!/usr/bin/env python3
"""确认主地点GPS优化状态"""
import json, os
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

coord_sources = Counter()
has_sub_coords = 0
total = 0

for i in range(1, 235):
    pid = f'P{i:03d}'
    fp = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(fp) as f:
        p = json.load(f)
    
    total += 1
    cs = p.get('coordinate_source', 'none')
    coord_sources[cs] += 1
    
    # 检查子地点是否有比主坐标更精确的坐标
    sp = p.get('sub_places', [])
    for s in sp:
        if s.get('lat') and s.get('verification_status') == 'verified':
            has_sub_coords += 1
            break

print(f"=== 主地点GPS坐标来源 ===")
for src, cnt in coord_sources.most_common():
    print(f"  {src}: {cnt}")
print(f"\n总计: {total}个主地点, {sum(coord_sources.values())}个有坐标")
print(f"有verified子地点坐标的地点: {has_sub_coords}个")

# 检查关键地点的主坐标是否来自子地点居住地
key_places = ['P008', 'P034', 'P058', 'P072', 'P075', 'P119', 'P195', 'P017']
print(f"\n=== 关键地点主坐标来源 ===")
for pid in key_places:
    fp = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(fp) as f:
        p = json.load(f)
    name = p.get('ancient_name', '')
    cs = p.get('coordinate_source', '')
    lat = p.get('lat', '')
    lng = p.get('lng', '')
    # 找居住地子地点
    residences = [s for s in p.get('sub_places', []) if s.get('type') == 'residence']
    if residences:
        r = residences[0]
        print(f"  {pid} {name}: 主坐标来源={cs}, lat={lat}, lng={lng}")
        print(f"    首个居住地: {r.get('name','')} lat={r.get('lat','')} lng={r.get('lng','')} status={r.get('verification_status','')}")
    else:
        print(f"  {pid} {name}: 主坐标来源={cs}, lat={lat}, lng={lng}, 无居住地子地点")
