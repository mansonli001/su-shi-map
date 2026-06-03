#!/usr/bin/env python3
"""
检查地点详情中的作品是否都有对应的诗词数据
"""
import json
import os
from pathlib import Path

# 读取诗词索引
poems_index_path = Path('data-v4/poems-index.json')
with open(poems_index_path, 'r', encoding='utf-8') as f:
    poems_index = json.load(f)

# 获取所有诗词ID
poem_ids = set(poem['id'] for poem in poems_index['poems'])
print(f"诗词索引中共有 {len(poem_ids)} 首诗词")

# 读取所有地点数据
places_dir = Path('data-v4/places')
place_files = sorted(places_dir.glob('*.json'))

# 统计信息
total_works = 0
works_with_poem_id = 0
works_without_poem_id = 0
missing_poems = []

for place_file in place_files:
    with open(place_file, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    
    place_id = place_data.get('id', '')
    place_name = place_data.get('ancient_name', '')
    
    # 检查 global_works
    global_works = place_data.get('global_works', [])
    for work in global_works:
        total_works += 1
        work_title = work.get('title', '')
        poem_id = work.get('poem_id', '')
        
        if poem_id:
            works_with_poem_id += 1
            if poem_id not in poem_ids:
                missing_poems.append({
                    'place_id': place_id,
                    'place_name': place_name,
                    'work_title': work_title,
                    'poem_id': poem_id
                })
        else:
            works_without_poem_id += 1

print(f"\n地点详情中共有 {total_works} 部作品")
print(f"有 poem_id 的作品: {works_with_poem_id} 部")
print(f"没有 poem_id 的作品: {works_without_poem_id} 部")

if missing_poems:
    print(f"\n⚠️  发现 {len(missing_poems)} 个 poem_id 在诗词索引中不存在:")
    for item in missing_poems:
        print(f"  - {item['place_name']} ({item['place_id']}): 《{item['work_title']}》 -> {item['poem_id']}")
else:
    print("\n✅ 所有 poem_id 都在诗词索引中存在")

# 输出没有 poem_id 的作品详情
if works_without_poem_id > 0:
    print(f"\n📋 没有 poem_id 的作品列表:")
    for place_file in place_files:
        with open(place_file, 'r', encoding='utf-8') as f:
            place_data = json.load(f)
        
        place_id = place_data.get('id', '')
        place_name = place_data.get('ancient_name', '')
        
        global_works = place_data.get('global_works', [])
        works_without_id = [w for w in global_works if not w.get('poem_id')]
        
        if works_without_id:
            print(f"\n  {place_name} ({place_id}):")
            for work in works_without_id:
                print(f"    - 《{work.get('title', '')}》 ({work.get('type', '')})")