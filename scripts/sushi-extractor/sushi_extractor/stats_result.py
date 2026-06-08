#!/usr/bin/env python3
"""统计GPS精细化结果"""
import json, os, glob

places_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data-v4', 'places')
places_dir = os.path.normpath(places_dir)

total = 0
has_sub = 0
has_latlng = 0
has_residence = 0
total_sub_places = 0
total_residences = 0
total_scenic = 0
total_other = 0
coord_sources = {}
verification_statuses = {}
sub_place_types = {}

for f in sorted(glob.glob(os.path.join(places_dir, 'P*.json'))):
    with open(f) as fh:
        p = json.load(fh)
    total += 1
    sp = p.get('sub_places', [])
    if sp: has_sub += 1
    total_sub_places += len(sp)
    
    # 检查主坐标（lat/lng）
    if p.get('lat') is not None and p.get('lng') is not None:
        has_latlng += 1
    src = p.get('coordinate_source', 'none')
    coord_sources[src] = coord_sources.get(src, 0) + 1
    
    has_res = False
    for s in sp:
        t = s.get('type', 'unknown')
        sub_place_types[t] = sub_place_types.get(t, 0) + 1
        if t == 'residence':
            has_res = True
            total_residences += 1
        elif t == 'scenic':
            total_scenic += 1
        else:
            total_other += 1
        vs = s.get('verification_status', 'none')
        verification_statuses[vs] = verification_statuses.get(vs, 0) + 1
    if has_res: has_residence += 1

print("=" * 60)
print("📊 GPS精细化结果统计")
print("=" * 60)
print(f"总地点数: {total}")
print(f"有sub_places: {has_sub} ({has_sub/total*100:.1f}%)")
print(f"有lat/lng主坐标: {has_latlng} ({has_latlng/total*100:.1f}%)")
print(f"有residence子地点: {has_residence} ({has_residence/total*100:.1f}%)")
print(f"\n子地点总数: {total_sub_places}")
print(f"  居住地(residence): {total_residences}")
print(f"  游览地(scenic): {total_scenic}")
print(f"  其他: {total_other}")
print(f"\n子地点类型分布:")
for k, v in sorted(sub_place_types.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print(f"\n主坐标来源(coordinate_source):")
for k, v in sorted(coord_sources.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print(f"\n子地点验证状态:")
for k, v in sorted(verification_statuses.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
