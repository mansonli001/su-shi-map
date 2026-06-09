#!/usr/bin/env python3
"""
全面数据质量扫描
1. 作品poem_id是否在诗文库中有对应文件
2. home页统计数字是否与实际数据同步
3. 空内容/坐标错位/导航问题检测
"""

import json
import glob
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4')
PLACES_DIR = os.path.join(DATA_DIR, 'places')
POEMS_DIR = os.path.join(DATA_DIR, 'poems')

def load_json(path):
    with open(path) as f:
        return json.load(f)

def main():
    # === 加载诗文库 ===
    poem_files = glob.glob(os.path.join(POEMS_DIR, '*.json'))
    poem_ids = set()
    poem_titles = {}
    for pf in poem_files:
        p = load_json(pf)
        pid = p.get('id', os.path.basename(pf).replace('.json', ''))
        poem_ids.add(pid)
        poem_titles[pid] = p.get('title', '')

    print(f'诗文库: {len(poem_ids)} 首')

    # === 加载地点数据 ===
    place_files = sorted(glob.glob(os.path.join(PLACES_DIR, 'P*.json')))
    places = {}
    for pf in place_files:
        p = load_json(pf)
        places[p['id']] = p

    print(f'地点: {len(places)} 个')

    # === 1. 作品poem_id链接检查 ===
    broken_links = []
    total_works = 0
    works_with_poem_id = 0
    works_without_poem_id = 0

    for pid, p in places.items():
        for w in p.get('global_works', []):
            total_works += 1
            poem_id = w.get('poem_id')
            if poem_id:
                works_with_poem_id += 1
                if poem_id not in poem_ids:
                    broken_links.append((pid, p.get('ancient_name', ''), w.get('title', ''), poem_id))
            else:
                works_without_poem_id += 1

    print(f'\n=== 1. 作品-诗文库链接检查 ===')
    print(f'总作品: {total_works}')
    print(f'有poem_id: {works_with_poem_id} ({works_with_poem_id*100//total_works if total_works else 0}%)')
    print(f'无poem_id(无法点击): {works_without_poem_id} ({works_without_poem_id*100//total_works if total_works else 0}%)')
    print(f'断裂链接(poem_id不存在): {len(broken_links)}')
    for pid, name, title, poem_id in broken_links[:20]:
        print(f'  {pid} {name}: "{title}" → poem_id={poem_id} 不存在')

    # === 2. Home页统计数字 ===
    print(f'\n=== 2. Home页统计数字 ===')
    total_places = len(places)
    has_works = sum(1 for p in places.values() if p.get('global_works'))
    has_events = sum(1 for p in places.values() if p.get('global_events'))
    has_food = sum(1 for p in places.values() if p.get('foods'))
    has_visit = sum(1 for p in places.values() if p.get('modern_visit'))
    
    # 路线数
    route_files = glob.glob(os.path.join(DATA_DIR, 'routes', '*.json'))
    
    print(f'地点总数: {total_places}')
    print(f'路线总数: {len(route_files)}')
    print(f'有作品地点: {has_works}')
    print(f'有事迹地点: {has_events}')
    print(f'有美食地点: {has_food}')
    print(f'有文旅地点: {has_visit}')
    print(f'作品总数: {total_works}')
    print(f'诗文库总数: {len(poem_ids)}')

    # === 3. 空内容/坐标错位检测 ===
    print(f'\n=== 3. 数据质量扫描 ===')
    
    empty_content = []
    coord_issues = []
    nav_issues = []
    
    for pid, p in places.items():
        name = p.get('ancient_name', '')
        
        # 空内容检测
        if not p.get('background') and not p.get('summary'):
            empty_content.append((pid, name, '无background和summary'))
        if not p.get('global_events') and not p.get('global_works'):
            empty_content.append((pid, name, '无事迹和作品'))
        
        # 坐标检测
        lat, lng = p.get('lat'), p.get('lng')
        if lat is None or lng is None:
            coord_issues.append((pid, name, '缺少坐标'))
        elif not (15 < lat < 55 and 70 < lng < 140):
            coord_issues.append((pid, name, f'坐标超出中国范围({lat},{lng})'))
        
        # 导航检测（modern_visit有但POI坐标偏差大）
        mv = p.get('modern_visit')
        if mv and isinstance(mv, list):
            for v in mv:
                if v.get('lat') and v.get('lng'):
                    vlat, vlng = v['lat'], v['lng']
                    dist = ((lat - vlat)**2 + (lng - vlng)**2)**0.5 * 111  # 粗略km
                    if dist > 50:
                        nav_issues.append((pid, name, f'POI偏离{dist:.0f}km: {v.get("name","?")}({vlat},{vlng})'))

    print(f'空内容地点: {len(empty_content)}')
    for pid, name, issue in empty_content[:10]:
        print(f'  {pid} {name}: {issue}')
    
    print(f'坐标问题: {len(coord_issues)}')
    for pid, name, issue in coord_issues[:10]:
        print(f'  {pid} {name}: {issue}')
    
    print(f'导航偏离(>50km): {len(nav_issues)}')
    for pid, name, issue in nav_issues[:10]:
        print(f'  {pid} {name}: {issue}')

if __name__ == '__main__':
    main()
