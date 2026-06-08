#!/usr/bin/env python3
"""同步路线详情文件的unique_color"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
ROUTES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'routes')
INDEX_PATH = os.path.join(PROJECT_DIR, 'data-v4', 'routes-index.json')

with open(INDEX_PATH) as f:
    index = json.load(f)

color_map = {r['id']: r['unique_color'] for r in index['routes']}

updated = 0
for rid, color in color_map.items():
    fp = os.path.join(ROUTES_DIR, f'{rid}.json')
    if not os.path.exists(fp):
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    old_color = data.get('unique_color', '')
    if old_color != color:
        data['unique_color'] = color
        # 也更新dim色
        data['unique_color_dim'] = ''  # 清空旧的dim色，前端自动计算
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        updated += 1
        print(f"  {rid}: {old_color} → {color}")

print(f"\n总计: 更新{updated}个路线详情文件")
