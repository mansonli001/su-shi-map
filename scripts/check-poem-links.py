#!/usr/bin/env python3
"""检查地点事件与诗词的关联情况"""
import json
from pathlib import Path

# 加载诗词索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    poems_data = json.load(f)

poems = poems_data.get('poems', [])
poem_id_set = set(p.get('id') for p in poems)

# 检查所有地点的global_works是否有有效的poem_id
places_dir = Path('data-v4/places')
place_files = sorted(places_dir.glob('P*.json'))

works_with_poem_id = 0
works_without_poem_id = 0
works_total = 0

print('=== 地点作品与诗词关联检查 ===')
print('=' * 60)

for pf in place_files:
    with open(pf, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    
    place_id = place_data.get('id', '')
    place_name = place_data.get('ancient_name', place_data.get('name', ''))
    works = place_data.get('global_works', [])
    
    for work in works:
        works_total += 1
        poem_id = work.get('poem_id', '')
        
        if poem_id:
            if poem_id in poem_id_set:
                works_with_poem_id += 1
            else:
                works_without_poem_id += 1
                print(f'⚠️ [{place_id}] {place_name}: 作品 "{work.get("title", "")}" 引用了不存在的 poem_id: {poem_id}')
        else:
            works_without_poem_id += 1

print('\n' + '=' * 60)
print(f'作品总数: {works_total}')
print(f'有有效poem_id的作品: {works_with_poem_id}')
print(f'无poem_id或无效的作品: {works_without_poem_id}')
print(f'关联成功率: {works_with_poem_id/works_total*100:.1f}%')

# 检查诗词中提到的地点是否在地点数据中存在
print('\n\n=== 诗词地点引用检查 ===')
place_names = set()
for pf in place_files:
    with open(pf, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    if 'ancient_name' in place_data:
        place_names.add(place_data['ancient_name'])
    if 'modern_name' in place_data:
        place_names.add(place_data['modern_name'])

# 检查是否有不应该显示的标点
print('\n=== 诗词标点检查 ===')
bad_punctuation = ['```', '---', '>>>', '<<<', '**', '__', '~~']
has_bad_punctuation = False

for poem in poems:
    pid = poem.get('id', '')
    fpath = Path(f'data-v4/poems/{pid}.json')
    
    if not fpath.exists():
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        pdata = json.dumps(f.read())
    
    for bad_char in bad_punctuation:
        if bad_char in pdata:
            has_bad_punctuation = True
            print(f'⚠️ [{pid}] 发现不应该显示的标点: "{bad_char}"')

if not has_bad_punctuation:
    print('✓ 未发现不应该显示的标点')
