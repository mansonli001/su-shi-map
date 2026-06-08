#!/usr/bin/env python3
"""
从 data-v4/places/*.json 同步坐标到 places-index.json 和 public/
"""
import json, os, math

PLACES_DIR = 'data-v4/places'
INDEX_FILE = 'data-v4/places-index.json'
PUBLIC_DIR = 'public/data-v4/places'
PUBLIC_INDEX = 'public/data-v4/places-index.json'

with open(INDEX_FILE, encoding='utf-8') as f:
    pi = json.load(f)

# 建立 index 中 place 的查找表
index_map = {}
for p in pi['places']:
    index_map[p['id']] = p

updated = 0
for pid, ip in index_map.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        continue
    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)
    
    changed = False
    # 同步坐标
    if pd.get('lat') and pd.get('lng'):
        if ip.get('lat') != pd['lat'] or ip.get('lng') != pd['lng']:
            ip['lat'] = pd['lat']
            ip['lng'] = pd['lng']
            changed = True
    
    # 同步 type 和 designType
    if pd.get('type') and ip.get('type') != pd['type']:
        ip['type'] = pd['type']
        changed = True
    if pd.get('designType') and ip.get('designType') != pd['designType']:
        ip['designType'] = pd['designType']
        changed = True
    
    # 同步 ancient_name / modern_name
    if pd.get('ancient_name') and ip.get('ancient_name') != pd['ancient_name']:
        ip['ancient_name'] = pd['ancient_name']
        changed = True
    if pd.get('modern_name') and ip.get('modern_name') != pd['modern_name']:
        ip['modern_name'] = pd['modern_name']
        changed = True
    
    if changed:
        updated += 1

# 写回 index
with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    json.dump(pi, f, ensure_ascii=False, indent=2)
with open(PUBLIC_INDEX, 'w', encoding='utf-8') as f:
    json.dump(pi, f, ensure_ascii=False, indent=2)

print(f"同步完成，更新了 {updated} 个地点的index数据")

# 验证关键地点
for pid in ['P024', 'P072']:
    with open(os.path.join(PLACES_DIR, f'{pid}.json')) as f:
        pd = json.load(f)
    p = index_map[pid]
    print(f"  {pid} {pd.get('ancient_name','')}: place=({pd.get('lat')},{pd.get('lng')}), index=({p.get('lat')},{p.get('lng')})")
