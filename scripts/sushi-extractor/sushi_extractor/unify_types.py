#!/usr/bin/env python3
"""
子地点类型命名统一：中文→英文
"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

# 中文→英文映射
TYPE_MAP = {
    '寺庙': 'temple',
    '山': 'mountain',
    '山峰': 'mountain',
    '岭': 'mountain',
    '名山': 'mountain',
    '岗': 'mountain',
    '遗址': 'ruins',
    '古迹': 'ruins',
    '湖泊': 'lake',
    '泉水': 'spring',
    '建筑': 'building',
    '楼': 'building',
    '台': 'building',
    '亭': 'pavilion',
    '古城': 'ancient_city',
    '城': 'ancient_city',
    '博物馆': 'museum',
    '祠堂': 'shrine',
    '祠': 'shrine',
    '历史街区': 'historic_street',
    '堤坝': 'dam',
    '风景': 'scenic',
    '公园': 'park',
    '驿站': 'post_station',
    '关隘': 'pass',
    '塔': 'pagoda',
    '书院': 'academy',
}

updated = 0
changed = 0

for i in range(1, 235):
    pid = f'P{i:03d}'
    fp = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(fp, 'r', encoding='utf-8') as f:
        p = json.load(f)
    
    modified = False
    for sp in p.get('sub_places', []):
        old_type = sp.get('type', '')
        if old_type in TYPE_MAP:
            sp['type'] = TYPE_MAP[old_type]
            changed += 1
            modified = True
    
    if modified:
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
        updated += 1

print(f"总计: 更新{updated}个地点文件, 统一{changed}个子地点类型")
