#!/usr/bin/env python3
"""
阶段7+：大规模作品关联补充
策略：用作品的route_id匹配同路线地点，按地点名称模糊匹配分配作品
"""
import json, os, re

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# 加载作品索引
with open('data-v4/poems-index.json') as f:
    pi = json.load(f)
poems = pi['poems']

# 加载地点索引
with open('data-v4/places-index.json') as f:
    pli = json.load(f)
places = pli['places']

# 加载路线索引（获取路线名）
with open('data-v4/routes-index.json') as f:
    ri = json.load(f)
routes = {r['id']: r for r in ri['routes']}

# 按路线分组地点
route_places = {}
for p in places:
    for rid in p.get('related_routes', []):
        if rid not in route_places:
            route_places[rid] = []
        route_places[rid].append(p)

# 按路线分组作品
route_poems = {}
for poem in poems:
    rid = poem.get('route_id', '')
    if rid:
        if rid not in route_poems:
            route_poems[rid] = []
        route_poems[rid].append(poem)

print(f"作品库: {len(poems)}首")
print(f"有路线ID的作品: {sum(len(v) for v in route_poems.values())}首")
print(f"涉及路线数: {len(route_poems)}")

# 收集每个地点已有的作品标题
place_existing = {}
for p in places:
    pid = p['id']
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if os.path.exists(pf):
        with open(pf) as f:
            pd = json.load(f)
        titles = {w.get('title', '') for w in pd.get('global_works', [])}
        place_existing[pid] = (titles, pd)
    else:
        place_existing[pid] = (set(), {})

# 作品中可能包含地点关键词的映射
# 从作品标题和内容中提取地点线索
def extract_location_hints(poem):
    """从作品中提取地点线索"""
    hints = []
    title = poem.get('title', '')
    # 常见地点关键词
    location_keywords = {
        '赤壁': ['黄州', 'P072'],
        '东坡': ['黄州', 'P072'],
        '西湖': ['杭州', 'P036'],
        '钱塘': ['杭州', 'P036'],
        '临安': ['杭州', 'P036'],
        '密州': ['密州', 'P124'],
        '超然台': ['密州', 'P124'],
        '黄州': ['黄州', 'P072'],
        '惠州': ['惠州', 'P074'],
        '儋耳': ['儋州', 'P073'],
        '海南': ['儋州', 'P073'],
        '庐山': ['庐山', 'P090'],
        '九江': ['庐山', 'P090'],
        '汴京': ['汴京', 'P108'],
        '开封': ['汴京', 'P108'],
        '颍州': ['颍州', 'P044'],
        '汝州': ['汝州', 'P145'],
        '徐州': ['徐州', 'P040'],
        '湖州': ['湖州', 'P042'],
        '常州': ['常州', 'P017'],
        '定州': ['定州', 'P039'],
        '扬州': ['扬州', 'P047'],
        '登州': ['登州', 'P013'],
        '凤翔': ['凤翔', 'P045'],
        '眉山': ['眉山', 'P118'],
        '剑门': ['剑门关', 'P080'],
        '三峡': ['三峡', 'P149'],
        '白帝': ['白帝城', 'P010'],
        '金陵': ['金陵', 'P083'],
        '镇江': ['金山', 'P084'],
        '金山寺': ['金山', 'P084'],
        '太湖': ['太湖', 'P164'],
        '洪泽': ['洪泽湖', 'P061'],
        '大庾': ['大庾岭', 'P034'],
        '梅关': ['大庾岭', 'P034'],
        '岭南': ['南雄', 'P126'],
        '赣江': ['赣州', 'P052'],
        '庐陵': ['吉安', 'P078'],
        '吉安': ['吉安', 'P078'],
        '滕王阁': ['洪州', 'P064'],
    }
    for kw, info in location_keywords.items():
        if kw in title:
            hints.append(info[1])  # place_id
    return hints

# 按路线分配作品到地点
# 策略：每条路线的作品，优先分配给同路线的关键地点（official/stay/birth/death）
# 然后按地点名称匹配分配
updated_count = 0
added_works = 0

for rid, rpoems in route_poems.items():
    if rid not in route_places:
        continue
    
    rplaces = route_places[rid]
    # 按重要性排序：official > stay > birth > death > sight > around > main
    type_priority = {'birth': 0, 'death': 0, 'tomb': 0, 'official': 1, 'stay': 2, 'sight': 3, 'around': 4, 'visit': 5, 'main': 6}
    rplaces_sorted = sorted(rplaces, key=lambda p: type_priority.get(p.get('type', 'main'), 5))
    
    for poem in rpoems:
        title = poem.get('title', '')
        poem_type = poem.get('type', '诗')
        core_verse = poem.get('coreVerse', '')
        
        # 1. 先尝试从标题提取地点线索
        hints = extract_location_hints(poem)
        target_pid = None
        
        if hints:
            for hint_pid in hints:
                # 检查该地点是否在同路线中
                if any(p['id'] == hint_pid for p in rplaces):
                    target_pid = hint_pid
                    break
        
        # 2. 如果没有地点线索，分配给路线中最重要的地点（且该地点还没有太多作品）
        if not target_pid:
            for p in rplaces_sorted:
                existing_titles = place_existing.get(p['id'], (set(),))[0]
                if len(existing_titles) < 8:  # 每个地点最多8个作品
                    target_pid = p['id']
                    break
        
        if not target_pid:
            continue
        
        # 检查是否已存在
        existing_titles, pd = place_existing[target_pid]
        if title in existing_titles:
            continue
        
        # 添加作品
        desc = core_verse[:60] + '...' if len(core_verse) > 60 else core_verse
        if 'global_works' not in pd:
            pd['global_works'] = []
        
        pd['global_works'].append({
            'title': title,
            'type': poem_type,
            'description': desc,
        })
        existing_titles.add(title)
        place_existing[target_pid] = (existing_titles, pd)
        added_works += 1

# 保存所有修改的地点
for pid, (titles, pd) in place_existing.items():
    if len(pd) == 0:
        continue
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        continue
    
    # 检查是否有新增（对比文件原内容）
    with open(pf) as f:
        original = json.load(f)
    orig_titles = {w.get('title', '') for w in original.get('global_works', [])}
    new_titles = {w.get('title', '') for w in pd.get('global_works', [])}
    
    if new_titles != orig_titles:
        with open(pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
        # 同步到public
        pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
        if os.path.exists(pub_pf):
            with open(pub_pf, 'w', encoding='utf-8') as f:
                json.dump(pd, f, ensure_ascii=False, indent=2)
        updated_count += 1
        an = pd.get('ancient_name', '')
        added = len(new_titles - orig_titles)
        if added > 0:
            print(f"  OK {pid} {an} +{added}作品")

print(f"\n共更新 {updated_count} 个地点，补充 {added_works} 个作品关联")
