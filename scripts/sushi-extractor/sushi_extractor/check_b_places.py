#!/usr/bin/env python3
"""查看B级地点当前作品美食数据"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

with open(os.path.join(SCRIPT_DIR, 'reports', 'place_richness_analysis.json')) as f:
    analysis = json.load(f)

b_places = [r for r in analysis if r['grade'] == 'B']

print(f'B级地点: {len(b_places)}个')
print('=' * 70)

for r in sorted(b_places, key=lambda x: -x['score']):
    pid = r['place_id']
    fp = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(fp) as fh:
        p = json.load(fh)
    
    sp = p.get('sub_places', [])
    foods = p.get('foods', [])
    global_works = p.get('global_works', [])
    sp_works_total = sum(len(s.get('works', [])) for s in sp)
    
    sp_summary = []
    for s in sp:
        w = s.get('works', [])
        if w:
            sp_summary.append(f"{s.get('name','')}({s.get('type','')}):{','.join(w[:2])}")
        else:
            sp_summary.append(f"{s.get('name','')}({s.get('type','')})")
    
    print(f"{pid} {p.get('ancient_name','')} (score={r['score']}, type={p.get('type','')})")
    print(f"  子地点: {len(sp)}个, 子地点作品: {sp_works_total}, global_works: {len(global_works)}, 美食: {len(foods)}")
    if sp_summary:
        print(f"  子地点: {'; '.join(sp_summary[:5])}")
