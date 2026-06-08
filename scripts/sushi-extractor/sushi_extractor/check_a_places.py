#!/usr/bin/env python3
"""查看A级地点当前作品美食数据"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

with open(os.path.join(SCRIPT_DIR, 'reports', 'place_richness_analysis.json')) as f:
    analysis = json.load(f)

a_places = [r for r in analysis if r['grade'] == 'A']

print('A级地点及当前数据:')
print('=' * 70)
for r in a_places:
    pid = r['place_id']
    fp = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(fp) as fh:
        p = json.load(fh)
    
    sp = p.get('sub_places', [])
    foods = p.get('foods', [])
    global_works = p.get('global_works', [])
    route_works = p.get('route_works', {})
    
    # 统计route_works
    rw_count = sum(len(v) if isinstance(v, list) else 0 for v in route_works.values())
    
    print(f'\n{pid} {p.get("ancient_name","")} (type={p.get("type","")})')
    print(f'  子地点: {len(sp)}个, global_works: {len(global_works)}, route_works: {rw_count}, 美食: {len(foods)}')
    
    for s in sp:
        w = s.get('works', [])
        w_str = ', '.join(w) if w else '无'
        print(f'  - {s.get("name","")} ({s.get("type","")}): 作品=[{w_str}]')
    
    if global_works:
        print(f'  global_works: {global_works[:5]}')
    if foods:
        print(f'  foods: {foods}')
