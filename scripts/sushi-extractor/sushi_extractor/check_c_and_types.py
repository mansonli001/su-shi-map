#!/usr/bin/env python3
"""查看C级地点当前作品美食数据 + 统计子地点中文类型"""
import json, os
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

with open(os.path.join(SCRIPT_DIR, 'reports', 'place_richness_analysis.json')) as f:
    analysis = json.load(f)

c_places = [r for r in analysis if r['grade'] == 'C']

print(f'=== C级地点: {len(c_places)}个 ===')
print('=' * 70)

# 同时统计所有子地点类型
type_counter = Counter()
no_coord_sp = []

for i in range(1, 235):
    pid = f'P{i:03d}'
    fp = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(fp) as fh:
        p = json.load(fh)
    for s in p.get('sub_places', []):
        type_counter[s.get('type', 'unknown')] += 1
        if s.get('verification_status') == 'no_coordinates':
            no_coord_sp.append({'place_id': pid, 'place_name': p.get('ancient_name',''), 'sp_name': s.get('name',''), 'sp_type': s.get('type','')})

for r in sorted(c_places, key=lambda x: -x['score']):
    pid = r['place_id']
    fp = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(fp) as fh:
        p = json.load(fh)
    
    sp = p.get('sub_places', [])
    foods = p.get('foods', [])
    global_works = p.get('global_works', [])
    sp_works_total = sum(len(s.get('works', [])) for s in sp)
    
    sp_info = []
    for s in sp:
        w = s.get('works', [])
        w_str = ','.join(w[:2]) if w else ''
        sp_info.append(f"{s.get('name','')}({s.get('type','')}){'→'+w_str if w_str else ''}")
    
    print(f"{pid} {p.get('ancient_name','')} (score={r['score']}, type={p.get('type','')})")
    print(f"  子地点:{len(sp)} 作品:{sp_works_total} global:{len(global_works)} 美食:{len(foods)}")
    if sp_info:
        print(f"  [{'; '.join(sp_info[:6])}]")

print(f"\n=== 子地点类型分布 ===")
for t, c in type_counter.most_common():
    print(f"  {t}: {c}")

# 中文类型映射
cn_types = [t for t in type_counter if any('\u4e00' <= c <= '\u9fff' for c in t)]
if cn_types:
    print(f"\n=== 需要统一的中文类型 ===")
    for t in cn_types:
        print(f"  {t}: {type_counter[t]}")

print(f"\n=== no_coordinates子地点: {len(no_coord_sp)}个 ===")
for s in no_coord_sp[:30]:
    print(f"  {s['place_id']} {s['place_name']} → {s['sp_name']} ({s['sp_type']})")
if len(no_coord_sp) > 30:
    print(f"  ... 还有{len(no_coord_sp)-30}个")
