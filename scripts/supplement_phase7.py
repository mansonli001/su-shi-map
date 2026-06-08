#!/usr/bin/env python3
"""
阶段7：作品库交叉校验
1. 检查poems-index.json中的作品是否与对应地点的global_works关联
2. 补充缺失的global_works关联
"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# 加载作品索引
with open('data-v4/poems-index.json') as f:
    pi = json.load(f)

poems = pi['poems']
print(f"作品库总数: {len(poems)}")

# 加载地点索引
with open('data-v4/places-index.json') as f:
    pli = json.load(f)
places = pli['places']

# 建立地点名→地点ID映射
place_name_map = {}
for p in places:
    place_name_map[p.get('ancient_name', '')] = p['id']
    place_name_map[p.get('modern_name', '')] = p['id']

# 按路线建立地点列表
route_places = {}
for p in places:
    for rid in p.get('related_routes', []):
        if rid not in route_places:
            route_places[rid] = []
        route_places[rid].append(p)

# 统计每首作品的location是否在地点数据中有对应
poem_location_map = {}  # poem_id -> place_id
for poem in poems:
    loc = poem.get('location', '')
    pid = poem.get('id', '')
    rid = poem.get('route_id', '')
    
    # 尝试匹配地点
    matched_pid = None
    
    # 1. 直接名称匹配
    if loc in place_name_map:
        matched_pid = place_name_map[loc]
    
    # 2. 在同路线地点中模糊匹配
    if not matched_pid and rid in route_places:
        for rp in route_places[rid]:
            an = rp.get('ancient_name', '')
            mn = rp.get('modern_name', '')
            if loc and (loc in an or loc in mn or an in loc or mn in loc):
                matched_pid = rp['id']
                break
    
    if matched_pid:
        poem_location_map[pid] = matched_pid

print(f"作品-地点匹配数: {len(poem_location_map)}/{len(poems)}")

# 检查地点的global_works是否包含对应作品
# 先收集每个地点已有的作品标题
place_existing_works = {}  # place_id -> set of titles
for p in places:
    pid = p['id']
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if os.path.exists(pf):
        with open(pf) as fh:
            pd = json.load(fh)
        titles = set()
        for w in pd.get('global_works', []):
            titles.add(w.get('title', ''))
        place_existing_works[pid] = titles

# 找出缺失的作品关联
missing_links = {}  # place_id -> [poem_info]
for poem in poems:
    pid = poem.get('id', '')
    if pid in poem_location_map:
        place_id = poem_location_map[pid]
        existing = place_existing_works.get(place_id, set())
        title = poem.get('title', '')
        if title not in existing:
            if place_id not in missing_links:
                missing_links[place_id] = []
            missing_links[place_id].append({
                'title': title,
                'type': poem.get('type', '诗'),
                'description': poem.get('coreVerse', '')[:50] + '...' if poem.get('coreVerse', '') else '',
                'poem_id': pid,
            })

print(f"\n缺失作品关联的地点数: {len(missing_links)}")
total_missing = sum(len(v) for v in missing_links.values())
print(f"缺失作品总数: {total_missing}")

# 执行补充（限制每个地点最多补充5个，避免过度）
updated = 0
supplemented = 0
for place_id, works in missing_links.items():
    pf = os.path.join(PLACES_DIR, f'{place_id}.json')
    if not os.path.exists(pf):
        continue
    
    with open(pf) as f:
        pd = json.load(f)
    
    if 'global_works' not in pd:
        pd['global_works'] = []
    
    existing_titles = {w.get('title', '') for w in pd['global_works']}
    added = 0
    for w in works[:5]:  # 每个地点最多补充5个
        if w['title'] not in existing_titles:
            pd['global_works'].append({
                'title': w['title'],
                'type': w['type'],
                'description': w['description'],
            })
            existing_titles.add(w['title'])
            added += 1
            supplemented += 1
    
    if added > 0:
        with open(pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
        pub_pf = os.path.join(PUBLIC_DIR, f'{place_id}.json')
        if os.path.exists(pub_pf):
            with open(pub_pf, 'w', encoding='utf-8') as f:
                json.dump(pd, f, ensure_ascii=False, indent=2)
        updated += 1
        an = pd.get('ancient_name', '')
        print(f"  OK {place_id} {an} +{added}作品")

print(f"\n共更新 {updated} 个地点，补充 {supplemented} 个作品关联")
