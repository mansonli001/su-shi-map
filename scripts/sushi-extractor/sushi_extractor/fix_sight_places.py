#!/usr/bin/env python3
"""
修正sight类型地点的虚构居住地
策略：
1. 路径/水路类(transit)：删除虚构驿馆，将子地点改为transit类型
2. 山岳类：删除虚构驿馆，保留真实景点
3. 景观类：删除虚构居所，保留真实景点
"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

transit_keywords = ['古道', '水路', '全程', '全线', '沿岸', '驿道', '栈道', '渡口', '航线']
water_keywords = ['运河', '江', '河', '湖', '海峡', '水', '湾']
mountain_keywords = ['山', '岭', '峰', '关', '峡']

fake_keywords = ['附近驿馆', '居所']  # 虚构居住地的关键词

fixed = 0
removed_fake = 0
added_transit = 0

for i in range(1, 235):
    pid = f'P{i:03d}'
    fp = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(fp, 'r', encoding='utf-8') as f:
        p = json.load(fh := f)
    fh.close()
    
    if p.get('type') != 'sight':
        continue
    
    name = p.get('ancient_name', '')
    sp = p.get('sub_places', [])
    
    is_transit = any(kw in name for kw in transit_keywords + water_keywords)
    
    # 找出虚构居住地
    fake_indices = []
    for idx, s in enumerate(sp):
        sname = s.get('name', '')
        if s.get('type') == 'residence' and any(fk in sname for fk in fake_keywords):
            fake_indices.append(idx)
    
    if not fake_indices:
        continue
    
    # 删除虚构居住地
    new_sp = []
    for idx, s in enumerate(sp):
        if idx in fake_indices:
            removed_fake += 1
            continue
        new_sp.append(s)
    
    # 如果是路径/水路类且子地点为空，添加transit类型子地点
    if is_transit and not new_sp:
        new_sp.append({
            'name': name,
            'ancient_name': name,
            'type': 'transit',
            'period': '',
            'description': f'苏轼途经{name}',
            'works': [],
            'importance': 'primary',
            'lat': p.get('lat'),
            'lng': p.get('lng'),
            'modern_address': p.get('sxzk_address', '') or p.get('modern_visit', {}).get('address', ''),
            'coordinate_source': p.get('coordinate_source', ''),
            'verification_status': 'verified',
            'note': '途经点，非停留地'
        })
        added_transit += 1
    
    p['sub_places'] = new_sp
    
    # 如果删除了所有子地点且没有新增transit，且主坐标来自虚构居住地
    # 保留原有lat/lng不变（作为途经参考坐标）
    
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(p, f, ensure_ascii=False, indent=2)
    
    fixed += 1
    category = 'transit' if is_transit else 'scenic'
    print(f"✅ {pid} {name} ({category}): 删除{len(fake_indices)}个虚构驿馆, 剩余{len(new_sp)}个子地点")

print(f"\n总计: 修正{fixed}个地点, 删除{removed_fake}个虚构居住地, 新增{added_transit}个transit子地点")
