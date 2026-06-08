#!/usr/bin/env python3
"""分析sight类型地点的子地点问题"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

# 分类sight地点
transit_keywords = ['古道', '水路', '全程', '全线', '沿岸', '驿道', '栈道', '渡口', '航线']
water_keywords = ['运河', '江', '河', '湖', '海峡', '水', '湾']
mountain_keywords = ['山', '岭', '峰', '关', '峡']

transit_sights = []  # 路径/水路类，不应有居住地
scenic_sights = []   # 景观类，可以有游览子地点
mountain_sights = [] # 山岳类

for i in range(1, 235):
    pid = f'P{i:03d}'
    fp = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(fp) as fh:
        p = json.load(fh)
    
    if p.get('type') != 'sight':
        continue
    
    name = p.get('ancient_name', '')
    sp = p.get('sub_places', [])
    
    # 判断子地点问题
    fake_residences = [s for s in sp if s.get('type') == 'residence' and ('附近驿馆' in s.get('name', '') or '居所' in s.get('name', ''))]
    real_residences = [s for s in sp if s.get('type') == 'residence' and '附近驿馆' not in s.get('name', '') and '居所' not in s.get('name', '')]
    scenic_sp = [s for s in sp if s.get('type') == 'scenic']
    other_sp = [s for s in sp if s.get('type') not in ('residence', 'scenic')]
    
    is_transit = any(kw in name for kw in transit_keywords + water_keywords)
    is_mountain = any(kw in name for kw in mountain_keywords) and not is_transit
    
    category = 'transit' if is_transit else ('mountain' if is_mountain else 'scenic')
    
    entry = {
        'id': pid,
        'name': name,
        'category': category,
        'fake_residences': len(fake_residences),
        'real_residences': len(real_residences),
        'scenic_sp': len(scenic_sp),
        'other_sp': len(other_sp),
        'total_sp': len(sp),
        'fake_names': [s.get('name', '') for s in fake_residences],
        'real_names': [s.get('name', '') for s in real_residences],
        'scenic_names': [s.get('name', '') for s in scenic_sp],
    }
    
    if is_transit:
        transit_sights.append(entry)
    elif is_mountain:
        mountain_sights.append(entry)
    else:
        scenic_sights.append(entry)

print(f"=== sight类型地点分析 ===")
print(f"总计: {len(transit_sights) + len(mountain_sights) + len(scenic_sights)}个")
print(f"  路径/水路类(transit): {len(transit_sights)}个")
print(f"  山岳类(mountain): {len(mountain_sights)}个")
print(f"  景观类(scenic): {len(scenic_sights)}个")

print(f"\n--- 路径/水路类（应删除虚构驿馆）---")
for e in transit_sights:
    print(f"  {e['id']} {e['name']}: 虚构驿馆={e['fake_residences']}, 真实居住地={e['real_residences']}, 游览地={e['scenic_sp']}")
    if e['fake_names']:
        print(f"    虚构: {e['fake_names']}")

print(f"\n--- 山岳类（可保留真实景点）---")
for e in mountain_sights:
    print(f"  {e['id']} {e['name']}: 虚构驿馆={e['fake_residences']}, 真实居住地={e['real_residences']}, 游览地={e['scenic_sp']}")
    if e['fake_names']:
        print(f"    虚构: {e['fake_names']}")

print(f"\n--- 景观类（需逐个判断）---")
for e in scenic_sights:
    print(f"  {e['id']} {e['name']}: 虚构驿馆={e['fake_residences']}, 真实居住地={e['real_residences']}, 游览地={e['scenic_sp']}")
    if e['fake_names']:
        print(f"    虚构: {e['fake_names']}")
